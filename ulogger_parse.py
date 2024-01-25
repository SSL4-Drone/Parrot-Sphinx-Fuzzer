import FuzzerDB
import UlogParser
import socket
import time

HOST = ""
PORT = 3306
USER = ""
PW = ""
DB = "arsdk_fuzzDB"
TB = "sphinx_tb"
CHARSET = "utf8"

ULOG_SERVER_ADDR = "192.168.0.35"
ULOG_SERVER_PORT = 33333


def process_log(payload, ack, received_log_lines, crashed):
    ulog_parser = UlogParser.UlogParser()

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
                log["code"] == "W" or log["code"] == "I"
            ):  # save data, only code is W or E
                testdb.save_result(
                    log["time"],
                    PAYLOAD_TEST,
                    ACK_TEST,
                    log["code"],
                    log["binary"],
                    log["desc"][:-3],
                    CRASHED == 1,  # TODO must be modified
                )


testdb = FuzzerDB.FuzzerDB(HOST, PORT, USER, PW, DB, TB, CHARSET)

ulog_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ulog_socket.connect((ULOG_SERVER_ADDR, ULOG_SERVER_PORT))


try:
    while True:
        while True:
            log_lines = b""
            # 데이터 수신
            while True:
                data = ulog_socket.recv(1)
                log_lines += data
                if data == b"\n":
                    break

            # 수신된 데이터를 문자열로 디코딩

            log_lines = log_lines.decode("utf-8")
            print(log_lines)

            # 로그 처리 (payload, ack, received_log_lines, crashed)
            process_log(
                "1010101010101010", "2020202020202020", log_lines, 0
            )  # TODO 테스트 data 수정


except KeyboardInterrupt:
    print("Server terminated by user.")
