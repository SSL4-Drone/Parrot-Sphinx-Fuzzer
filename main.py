import socket
from RandPayload import RandPayload
from PacketParser import PacketParser
import FuzzerDB
import db_data
import UlogParser
from threading import Thread
from threading import Lock
import time

# DB_DATA
DB_HOST = db_data.HOST
DB_PORT = 3306
DB_USER = db_data.USER
DB_PW = db_data.PW
DB = db_data.DB
TB = db_data.TB
CHARSET = "utf8"

IP = "192.168.42.1"  # Drone IP
PORT = 2233  # Drone port

iface = "Wi-Fi"

ULOG_SERVER_ADDR = "192.168.0.35"  # Ulog server IP
ULOG_SERVER_PORT = 33333  # Ulog server port

fuzzDB = None
ulog_parser = None
ulogBuf_lock = Lock()


def printInfo():
    print('''
         _    ___      _                      
        | |  /   |    | |                     
 ___ ___| | / /| |  __| |_ __ ___  _ __   ___ 
/ __/ __| |/ /_| | / _` | '__/ _ \| '_ \ / _ \\
\__ \__ \ |\___  || (_| | | | (_) | | | |  __/
|___/___/_|    |_| \__,_|_|  \___/|_| |_|\___|
''')

def connectDB():
    db = FuzzerDB.FuzzerDB(DB_HOST, DB_PORT, DB_USER, DB_PW, DB, TB, CHARSET)
    print("**[DB Connected]**")
    print(f"host : {db.host}")
    print(f"user : {db.user}")
    print(f"DB   : {db.db_name}")
    print(f"table: {db.tb_name}")
    return db


def processUlog(payload, ack, received_log_lines, crashed):
    if fuzzDB == None or ulog_parser == None:
        return

    ulog_parser.parse_lines_to_queue(received_log_lines)

    PAYLOAD_TEST = payload
    ACK_TEST = ack
    CRASHED = crashed
    while True:
        log = ulog_parser.next()
        if log is None:
            break
        else:
            print(log)  # Display parsed logs
            # save_result(timestamp, payload, ack, ulog_code, ulog_binary, ulog_desc, crashed)
            if (
                log["code"] == "W" or log["code"] == "I"  # TODO change the code type
            ):  # save data, only code is W or E
                fuzzDB.save_result(
                    log["time"],
                    PAYLOAD_TEST,
                    ACK_TEST,
                    log["code"],
                    log["binary"],
                    log["desc"][:-3],
                    CRASHED == 1,  # TODO must be modified
                )

class Sniff(Thread):
    def __init__(self, iface, seq):
        threading.Thread.__init__(self)
        self.iface = iface
        self.seq = seq
        self.data = None
    
    def run(self):
        parser = PacketParser(self.iface, self.seq)
        self.data = parser.parsing()
    
    def get_data(self):
        return self.data


def main():
    global fuzzDB, ulog_parser
    fuzzDB = connectDB()
    randPayload = RandPayload()
    received_log_lines = [None] * 1
    trash_log_lines = [None] * 1
    ulog_parser = UlogParser.UlogParser()
    ulog_socket = ulog_parser.connect_tcp(ULOG_SERVER_ADDR, ULOG_SERVER_PORT)
    
    # Threads
    packetThread = Sniff(iface, seq)
    
    UlogConsumingThread = Thread(
        target=ulog_parser.listen,
        args=(0, trash_log_lines),
        name="UlogConsumingThread",
    )  # 프로그램 종료까지 계속 실행됨

    UlogReadingThread = Thread(
        target=ulog_parser.listen,
        args=(1, received_log_lines),
        name="UlogReadingThread",
    )

    try:
        UlogConsumingThread.start()
        time.sleep(3)
        # sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        while True:
            for seq in range(255):
                payload = randPayload.generate_random_payload(seq)
                sock.sendto(payload, (IP, PORT))

                # Parsing ACK packet payload
                packetThread.start()
                ack_data = packetThread.get_data()

                # Ulog, ack payload DB에 저장

                # Parsing Ulog
                UlogReadingThread = Thread(
                    target=ulog_parser.listen,
                    args=(1, received_log_lines),
                    name="UlogReadingThread",
                )
                UlogReadingThread.start()
                
                UlogReadingThread.join()
                packetThread.join()
                data = packetThread.get_data()

                print("recved :", received_log_lines)
                # db에는 processUlog 인자로 received_log_lines[0] 저장
                log_lines = received_log_lines[0].decode("utf-8")
                processUlog(payload, ack_data, log_lines, 0)

    except Exception as ex:
        print("**[Error]** ", ex)

    finally:
        # sock.close()
        print("finish")
        if UlogReadingThread.is_alive():
            UlogReadingThread.join()
        ulog_parser.return_listening_loop()
        UlogConsumingThread.join()
        ulog_socket.close()
        exit()


if __name__ == "__main__":
    main()
