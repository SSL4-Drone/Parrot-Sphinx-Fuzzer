import FuzzerDB
import db_data

HOST = db_data.HOST
PORT = 3306
USER = db_data.USER
PW = db_data.PW
DB = db_data.DB
TB = db_data.TB
CHARSET = "utf8"


testdb = FuzzerDB.FuzzerDB(HOST, PORT, USER, PW, DB, TB, CHARSET)


# 결과 DB에 업로드
testdb.save_result(
    1234512345.1233,  # timestamp
    "test_payload",  # payload
    "test_ack",  # ack
    "E",  # ulog_code
    "test_bin",  # ulog_binary
    "test_desc",  # ulog_desc
    1,  # crashed (0 or 1)
)

testdb.save_result(
    1234512345.1233,  # timestamp
    "test_payloadtest_payloadtest_payloadtest_payloadtest_payloadtest_payloadtest_payloadtest_payloadtest_payloadtest_payloadtest_payload",  # payload
    "test_ack",  # ack
    "C",  # ulog_code
    "test_bin",  # ulog_binary
    "test_desc",  # ulog_desc
    1,  # crashed (0 or 1)
)


testdb.print_crashed()  # crashed == 1인 row 출력
# testdb.delete_all() #모든 rows 삭제


testdb.close()
