# -*- coding: utf-8 -*- 
#-------------------------------------------------------------------------------
# Name:        ??1
# Purpose:
#
# Author:      Administrator
#
# Created:     03-04-2015
# Copyright:   (c) Administrator 2015
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import sqlite3
import os
import logging

class umacHtmlDB:
    dbLog = None
    SHOW_SQL = None
    #??????
    def __init__(self):
        self.dbLog = logging.getLogger('umacHtmlMain.umacHtmlDB')
        self.SHOW_SQL = False
        
    def get_conn(self,dbFilePath):
        conn = sqlite3.connect(dbFilePath)
        if os.path.exists(dbFilePath) and os.path.isfile(dbFilePath):
            return conn
        else:
            conn = None
            return sqlite3.connect(':memory:')

    def get_cursor(self,conn):
        if conn is not None:
            return conn.cursor()
        else:
            return self.get_conn('').cursor()

    def close_all(self,conn, cu):
        try:
            if cu is not None:
                cu.close()
        finally:
            if cu is not None:
                cu.close()

    def create_table(self,conn,sql):
        if sql is not None and sql != '':
            cu = self.get_cursor(conn)
            cu.execute(sql)
            conn.commit()
            self.close_all(conn, cu)
        else:
            print('the [{}] is empty or equal None!'.format(sql))

    def save_data(self,conn,sql):
        if sql is not None and sql != '':
            cu = self.get_cursor(conn)
            if self.SHOW_SQL:
                print('执行sql:[{}]'.format(sql))

            cu.execute(sql)
            conn.commit()
            self.close_all(conn, cu)
        else:
            print('the [{}] is empty or equal None!'.format(sql))

    def insert_table(self,conn,tableName,row,data):
        insert_sql = 'INSERT INTO '+ tableName+' values ('+str(row)
        for d in data:
            if '"' in d:
                #d = d.translate({34:u' '})                 #将"号从字符串中删除，替换为空，"的ascII编码为34
                d = d.replace('"','').replace("'",'')

            d = d.replace(u'\xa0',u'')         #删除空格符
            insert_sql = insert_sql+',"'+d+'"'
        insert_sql = insert_sql+')'
        self.save_data(conn,insert_sql)

    def create_table_fromHead(self,conn,tableName,tableHead):

        create_table_sql = 'CREATE TABLE '+'`'+tableName+'` ' +'(`idv1` int(11) NOT NULL,'
        for field in tableHead:
            field = field.replace(u'\xa0',u'')   #删除空格符
            field = field.replace(' ','')
            field = field.replace('-','')
            create_table_sql = create_table_sql +'`'+ field+'` ' + 'varchar(80) NOT NULL,'

        create_table_sql = create_table_sql+'PRIMARY KEY (`idv1`))'
        self.create_table(conn,create_table_sql) 
           
    def fetchall(self,conn, sql):
        if sql == '':
            print('the [{}] is empty or equal None!'.format(sql))
            return None
                    
        cu = self.get_cursor(conn)
        try:
            cu.execute(sql)
        except Exception,ex:
            #self.dbLog.info(ex)
            return None
        r = cu.fetchall()
        return r
    
    def getAllTableName(self,conn):
        cu = self.get_cursor(conn)
        cu.execute("select name from sqlite_master where type = 'table' order by name")
        allTable = cu.fetchall()
        return allTable
    
    def get_table_struct(self,conn,tablename):
        cu = self.get_cursor(conn)
        try:
            cu.execute("PRAGMA table_info("+tablename+")")
        except Exception,ex:
            #self.dbLog.info(ex)
            return None
        ts = cu.fetchall()
        return ts
    
    def get_table_field(self,conn,tablename):
        ts = self.get_table_struct(conn, tablename)
        allField = []
        for s in ts:
            allField.append(s[1])
        return allField
    
if __name__ == '__main__':
    print ''
