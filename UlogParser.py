import re
import queue
from datetime import datetime


class UlogParser:
    def __init__(self):
        self.parsed_logs_queue = queue.Queue()  # a queue for a single parsed logs
        self.ulog_str = ""
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
        pattern = r"(?:(\x1b\[\d\;\d{2}m))?(?P<time>\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3})\s+(?P<code>[IEWC])\s+(?P<binary>.*?)\s*:\s*(?P<desc>.*)"

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
