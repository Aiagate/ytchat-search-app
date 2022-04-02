#! ./.venv/bin/python
# -*- coding: utf-8 -*-

# ---standard library---

# ---third party library---
import mysql.connector
# from mysql.connector.connection_cext import CMySQLConnection
# from mysql.connector.cursor_cext import CMySQLCursor

# ---local library---
import config

class DatabaseConnect(object):
    def __init__(self, db_name):
        self.db = db_name

    def __enter__(self):
        try:
            self.cnx = mysql.connector.connect(
                host=config.DATABASE_HOST,
                user=config.DATABASE_USER,
                password=config.DATABASE_PASSWORD,
                database=self.db,
                use_pure=True
            )
            self.cursor = self.cnx.cursor(buffered=True)
        except Exception as e:
            self.cnx = None
            raise e
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        if self.cnx != None:
            self.cnx.commit()
            self.cursor.close()
            self.cnx.close()

    def execute(self,*args):
        return self.cursor.execute(args)

    def create_table(self, tb_name: str, coulumns: str):
        sql = 'CREATE TABLE ' + tb_name + ' (' + coulumns + ')'
        return self.cursor.execute(sql)

    def insert(self, tb_name: str, values: str):
        sql = 'INSERT INTO ' + tb_name + ' values (' + values + ')'
        self.cursor.execute(sql)

if __name__ == "__main__":
    pass