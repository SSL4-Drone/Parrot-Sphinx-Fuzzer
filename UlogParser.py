import re
import queue
from datetime import datetime
import time
import socket
from threading import Event, Lock


class UlogParser:
    def __init__(self):
        self.parsed_logs_queue = queue.Queue()  # a queue for a single parsed logs
        self.ulog_str = ""
        self.ulog_socket = 0
        self.lock = Lock()
        self.loop = 1
        self.event = Event()
        self.replace_to_current_time = 1  # If 1: replace the timestamp of parsed logs to current timestamp. Else : do nothing.

    # Split(\n) and parse each log strings, and put them in parsed_logs_queue.
    # Can be only called when the queue is empty.
    def parse_lines_to_queue(self, ulog_str):
        if not self.parsed_logs_queue.empty():
            return
        self.ulog_str = ulog_str
        ulog_lines = ulog_str.strip().split("\n")
        for line in ulog_lines:
            self.parsed_logs_queue.put(self.parse_log_line(line))

    def parse_log_line(self, line):
        # Regular expression
        pattern = r"(?:(\x1b\[\d{1,}\;\d{2}m))?(?P<time>\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3})\s+(?P<code>[IEWC])\s+(?P<binary>.*?)\s*:\s*(?P<desc>.*)"

        # if not isinstance(line, bytes):
        #     line = line.encode("utf-8")

        match = re.match(pattern, line)

        if match:
            groups = match.groupdict()

            # Time modification
            if self.replace_to_current_time == 1:
                timestamp = datetime.now()
                groups["time"] = timestamp.timestamp()
            return groups
        else:
            return None

    # Return the queue even if the queue is empty.
    def get_parsed_queue(self):
        return self.parsed_logs_queue

    # If the queue is NOT empty, then return a single parsed line.
    # If empty, return None.
    def next(self):
        if self.parsed_logs_queue.empty():
            return None
        else:
            return self.parsed_logs_queue.get()

    def connect_tcp(self, ip, port):
        self.ulog_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.ulog_socket.connect((ip, port))
        return self.ulog_socket

    def recvline(self):
        try:
            if self.ulog_socket:
                pass
            else:
                print("ULOG_SOCKET NOT INITIALIZED")  # debug
                return
            self.lock.acquire()
            # print("recvline lock acquired")  # debug
            line = b""
            while True:
                data = self.ulog_socket.recv(1)
                line += data
                if data == b"\n":
                    self.lock.release()
                    # print(line.decode() + "  recvline lock released")  # debug
                    return line
        except TypeError:
            return b""

    def listen(self, timeout, recved_lines: list):
        lines = b""
        if timeout > 0:
            self.pause_listening_loop()
            end_time = time.time() + timeout
            while time.time() < end_time:
                # 데이터 수신 후 반환
                line = self.recvline()
                if line != b"":
                    lines += line
                # print(lines.decode())
            recved_lines[0] = lines
            self.resume_listening_loop()
            return recved_lines
        elif timeout == 0:
            while not self.event.is_set():
                if self.loop == 1:
                    pass
                else:
                    continue
                recved_lines.clear()
                line = self.recvline()
                # if line != b"":
                #     #print(line.decode())
                #     recved_lines.append(line)
            self.event.clear()
        else:
            return

    def return_listening_loop(self):
        self.event.set()

    def pause_listening_loop(self):
        self.loop = 0

    def resume_listening_loop(self):
        self.loop = 1
