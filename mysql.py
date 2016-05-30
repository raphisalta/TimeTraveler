# -*- coding: utf-8 -*-
#!/usr/bin/python

__author__ = 'yasu'

import MySQLdb

class MySQL:
    def __init__(self, dbname):
        self.user = 'timemachine'
        self.passwd = 't1MeM@sh1ne'

        self.con = MySQLdb.connect(
            host='localhost',
            db=dbname,
            user=self.user,
            passwd=self.passwd,
            charset="utf8")
        self.cur = self.con.cursor()


    def end_connection(self):
        self.cur.close()
        self.con.close()


    def exec_sql(self, sql):
        self.cur.execute(sql)
        self.con.commit()

    def param_sql(self, sql, param):
        self.cur.execute(sql,param)
        self.con.commit()

    def select(self, tname, select, where):
        com = 'SELECT ' + select + ' FROM ' + tname
        if len(where) > 0:
            com += ' WHERE ' + where
        self.cur.execute(com)
        return self.cur.fetchall()
