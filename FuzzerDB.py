import pymysql
from datetime import datetime


class FuzzerDB:
    def __init__(self, host, port, user, passwd, db_name, tb_name, charset):
        self.host = host
        self.port = port
        self.user = user
        self.passwd = passwd
        self.db_name = db_name
        self.tb_name = tb_name
        self.charset = charset
        self.db = pymysql.connect(
            host=self.host,
            port=self.port,
            user=self.user,
            passwd=self.passwd,
            db=self.db_name,
            charset=self.charset,
        )

    # save result
    # timestamp & payload & crashed cannot be NULL
    def save_result(
        self, timestamp, payload, ack, ulog_code, ulog_binary, ulog_desc, crashed
    ):
        cursor = self.db.cursor()
        sql = f"""INSERT INTO {self.tb_name} (timestamp, payload, ack, ulog_code, ulog_binary, ulog_desc, crashed) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s)"""
        timestamp_dt = datetime.fromtimestamp(timestamp)
        timestamp_str = timestamp_dt.strftime("%Y-%m-%d %H:%M:%S.%f")
        cursor.execute(
            sql,
            (timestamp_str, payload, ack, ulog_code, ulog_binary, ulog_desc, crashed),
        )
        self.db.commit()

    # delete every row
    def delete_all(self):
        cursor = self.db.cursor()
        sql = f"""DELETE FROM {self.tb_name}"""

        cursor.execute(sql)
        self.db.commit()

    # print every crashed == 1 row
    def print_crashed(self):
        cursor = self.db.cursor()
        sql = f"""SELECT * FROM {self.tb_name} WHERE crashed = 1;"""
        cursor.execute(sql)

        rows = cursor.fetchall()

        column_names = [desc[0] for desc in cursor.description]
        header = "\t".join(f"{name:<25}" for name in column_names)
        print(header)

        for row in rows:
            formatted_row = [
                f"{value:%Y-%m-%d %H:%M:%S.%f}"
                if isinstance(value, datetime)
                else f"{value:<25}"[:25]  # prints up to 25 characters
                for value in row
            ]
            row_str = "\t".join(formatted_row)
            print(row_str)

    def close(self):
        self.db.close()
