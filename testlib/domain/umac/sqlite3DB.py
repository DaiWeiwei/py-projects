# -*- coding: cp936 -*-
import sqlite3
import os
'''SQLite���ݿ���һ��ǳ�С�ɵ�Ƕ��ʽ��Դ���ݿ������Ҳ����˵
û�ж�����ά�����̣����е�ά���������ڳ�����
��python�У�ʹ��sqlite3�������ݿ�����ӣ�������ָ�������ݿ��ļ������ڵ�ʱ��
���Ӷ�����Զ��������ݿ��ļ���������ݿ��ļ��Ѿ����ڣ������Ӷ��󲻻��ٴ���
���ݿ��ļ�������ֱ�Ӵ򿪸����ݿ��ļ���
     ���Ӷ��������Ӳ����������ݿ��ļ���Ҳ�����ǽ������ڴ��еģ����ڴ��е����ݿ�
     ִ�����κβ����󣬶�����Ҫ�ύ�����(commit)
 
     ������Ӳ�����棺 conn = sqlite3.connect('c:\\test\\test.db')
     �������ڴ����棺 conn = sqlite3.connect('"memory:')
 
     ��������һӲ�����洴�����ݿ��ļ�Ϊ��������˵����
     conn = sqlite3.connect('c:\\test\\hongten.db')
     ����conn���������ݿ����Ӷ��󣬶��������ݿ����Ӷ�����˵���������²�����
 
         commit()            --�����ύ
         rollback()          --����ع�
         close()             --�ر�һ�����ݿ�����
         cursor()            --����һ���α�
 
     cu = conn.cursor()
     �������Ǿʹ�����һ���α����cu
     ��sqlite3�У�����sql����ִ�ж�Ҫ���α����Ĳ��������
     �����α����cu���������¾��������
 
         execute()           --ִ��һ��sql���
         executemany()       --ִ�ж���sql���
         close()             --�α�ر�
         fetchone()          --�ӽ����ȡ��һ����¼
         fetchmany()         --�ӽ����ȡ��������¼
          fetchall()          --�ӽ����ȡ�����м�¼
          scroll()            --�α����
  
  '''
 
#global var
#���ݿ��ļ�����·��
DB_FILE_PATH = ''
#������
TABLE_NAME = ''
#�Ƿ��ӡsql
SHOW_SQL = True
 
def get_conn(path):
     '''��ȡ�����ݿ�����Ӷ��󣬲���Ϊ���ݿ��ļ��ľ���·��
     ������ݵĲ����Ǵ��ڣ��������ļ�����ô�ͷ���Ӳ�������
     ·���µ����ݿ��ļ������Ӷ��󣻷��򣬷����ڴ��е����ݽ�
     ���Ӷ���'''
     conn = sqlite3.connect(path)
     if os.path.exists(path) and os.path.isfile(path):
         print('Ӳ������:[{}]'.format(path))
         return conn
     else:
         conn = None
         print('�ڴ�����:[:memory:]')
         return sqlite3.connect(':memory:')
 
def get_cursor(conn):
     '''�÷����ǻ�ȡ���ݿ���α���󣬲���Ϊ���ݿ�����Ӷ���
     ������ݿ�����Ӷ���ΪNone���򷵻����ݿ����Ӷ�������
     �����α���󣻷��򷵻�һ���α���󣬸ö������ڴ�������
     �����Ӷ������������α����'''
     if conn is not None:
         return conn.cursor()
     else:
         return get_conn('').cursor()
 
 ###############################################################
 ####            ����|ɾ�������     START
 ###############################################################
def drop_table(conn, table):
     '''��������,��ɾ����������д������ݵ�ʱ��ʹ�ø�
     ������ʱ��Ҫ���ã�'''
     if table is not None and table != '':
         sql = 'DROP TABLE IF EXISTS ' + table
         if SHOW_SQL:
             print('ִ��sql:[{}]'.format(sql))
         cu = get_cursor(conn)
         cu.execute(sql)
         conn.commit()
         print('ɾ�����ݿ��[{}]�ɹ�!'.format(table))
         close_all(conn, cu)
     else:
         print('the [{}] is empty or equal None!'.format(sql))
 
def create_table(conn, sql):
     '''�������ݿ��student'''
     if sql is not None and sql != '':
         cu = get_cursor(conn)
         if SHOW_SQL:
             print('ִ��sql:[{}]'.format(sql))
         cu.execute(sql)
         conn.commit()
         print('�������ݿ��[student]�ɹ�!')
         close_all(conn, cu)
     else:
         print('the [{}] is empty or equal None!'.format(sql))
 
 ###############################################################
 ####            ����|ɾ�������     END
 ###############################################################
 
def close_all(conn, cu):
     '''�ر����ݿ��α��������ݿ����Ӷ���'''
     try:
         if cu is not None:
             cu.close()
     finally:
         if cu is not None:
             cu.close()
 
 ###############################################################
 ####            ���ݿ����CRUD     START
 ###############################################################
 
def save(conn, sql, data):
     '''��������'''
     if sql is not None and sql != '':
         if data is not None:
             cu = get_cursor(conn)
             for d in data:
                 if SHOW_SQL:
                     print('ִ��sql:[{}],����:[{}]'.format(sql, d))
                 cu.execute(sql, d)
                 conn.commit()
             close_all(conn, cu)
     else:
         print('the [{}] is empty or equal None!'.format(sql))
 
def fetchall(conn, sql):
     '''��ѯ��������'''
     if sql is not None and sql != '':
         cu = get_cursor(conn)
         if SHOW_SQL:
             print('ִ��sql:[{}]'.format(sql))
         cu.execute(sql)
         r = cu.fetchall()
         if len(r) > 0:
             for e in range(len(r)):
                 print(r[e])
     else:
         print('the [{}] is empty or equal None!'.format(sql)) 
 
def fetchone(conn, sql, data):
     '''��ѯһ������'''
     if sql is not None and sql != '':
         if data is not None:
             #Do this instead
             d = (data,) 
             cu = get_cursor(conn)
             if SHOW_SQL:
                 print('ִ��sql:[{}],����:[{}]'.format(sql, data))
             cu.execute(sql, d)
             r = cu.fetchall()
             if len(r) > 0:
                 for e in range(len(r)):
                     print(r[e])
         else:
             print('the [{}] equal None!'.format(data))
     else:
         print('the [{}] is empty or equal None!'.format(sql))
 
def update(conn, sql, data):
     '''��������'''
     if sql is not None and sql != '':
         if data is not None:
             cu = get_cursor(conn)
             for d in data:
                 if SHOW_SQL:
                     print('ִ��sql:[{}],����:[{}]'.format(sql, d))
                 cu.execute(sql, d)
                 conn.commit()
             close_all(conn, cu)
     else:
         print('the [{}] is empty or equal None!'.format(sql))
 
def delete(conn, sql, data):
     '''ɾ������'''
     if sql is not None and sql != '':
         if data is not None:
             cu = get_cursor(conn)
             for d in data:
                 if SHOW_SQL:
                     print('ִ��sql:[{}],����:[{}]'.format(sql, d))
                 cu.execute(sql, d)
                 conn.commit()
             close_all(conn, cu)
     else:
         print('the [{}] is empty or equal None!'.format(sql))
 ###############################################################
 ####            ���ݿ����CRUD     END
 ###############################################################
 
 
 ###############################################################
 ####            ���Բ���     START
 ###############################################################
def drop_table_test():
     '''ɾ�����ݿ�����'''
     print('ɾ�����ݿ�����...')
     conn = get_conn(DB_FILE_PATH)
     drop_table(conn, TABLE_NAME)
 
def create_table_test():
     '''�������ݿ�����'''
     print('�������ݿ�����...')
     create_table_sql = '''CREATE TABLE `student` (
                           `id` int(11) NOT NULL,
                           `name` varchar(20) NOT NULL,
                           `gender` varchar(4) DEFAULT NULL,
                           `age` int(11) DEFAULT NULL,
                           `address` varchar(200) DEFAULT NULL,
                           `phone` varchar(20) DEFAULT NULL,
                            PRIMARY KEY (`id`)
                         )'''
     conn = get_conn(DB_FILE_PATH)
     create_table(conn, create_table_sql)
 
def save_test():
     '''�������ݲ���...'''
     print('�������ݲ���...')
     save_sql = '''INSERT INTO student values (?, ?, ?, ?, ?, ?)'''
     data = [(1, 'Hongten', u'��', 20, u'�㶫ʡ������', '13423****62'),
             (2, 'Tom', u'��', 22, u'�����ɽ�ɽ', '15423****63'),
             (3, 'Jake', u'Ů', 18, u'�㶫ʡ������', '18823****87'),
             (4, 'Cate', u'Ů', 21, u'�㶫ʡ������', '14323****32')]
     conn = get_conn(DB_FILE_PATH)
     save(conn, save_sql, data)
 
def fetchall_test():
     '''��ѯ��������...'''
     print('��ѯ��������...')
     fetchall_sql = '''SELECT * FROM student'''
     conn = get_conn(DB_FILE_PATH)
     fetchall(conn, fetchall_sql)
 
def fetchone_test():
     '''��ѯһ������...'''
     print('��ѯһ������...')
     fetchone_sql = 'SELECT * FROM student WHERE ID = ? '
     data = 1
     conn = get_conn(DB_FILE_PATH)
     fetchone(conn, fetchone_sql, data)
 
def update_test():
     '''��������...'''
     print('��������...')
     update_sql = 'UPDATE student SET name = ? WHERE ID = ? '
     data = [('HongtenAA', 1),
             ('HongtenBB', 2),
             ('HongtenCC', 3),
             ('HongtenDD', 4)]
     conn = get_conn(DB_FILE_PATH)
     update(conn, update_sql, data)
 
def delete_test():
     '''ɾ������...'''
     print('ɾ������...')
     delete_sql = 'DELETE FROM student WHERE NAME = ? AND ID = ? '
     data = [('HongtenAA', 1),
             ('HongtenCC', 3)]
     conn = get_conn(DB_FILE_PATH)
     delete(conn, delete_sql, data)
 
 ###############################################################
 ####            ���Բ���     END
 ###############################################################
 
def init():
     '''��ʼ������'''
     #���ݿ��ļ�����·��
     global DB_FILE_PATH
     DB_FILE_PATH = 'F:\\Python\\hongten.db'
     #���ݿ������
     global TABLE_NAME
     TABLE_NAME = 'student'
     #�Ƿ��ӡsql
     global SHOW_SQL
     SHOW_SQL = True
     print('show_sql : {}'.format(SHOW_SQL))
     #����������ݿ����ɾ����
     drop_table_test()
     #�������ݿ��student
     create_table_test()
     #�����ݿ���в�������
     save_test()
     
 
def main():
     init()
     fetchall_test()
     print('#' * 50)
     fetchone_test()
     #print('#' * 50)
     #update_test()
     #fetchall_test()
     #print('#' * 50)
     #delete_test()
     #fetchall_test()
 
if __name__ == '__main__':
     main()
