# coding:utf-8


import os
from testlib.domain.umac.xlop import xlsOP
from testlib.domain.umac.umacHtmlExcel import umacHtmlExcel
from testlib.domain.umac.umacHtmlDBInterface import umacHtmlDBInterface
from robot.api import logger


class FunctionAnalysis:
    def __init__(self):
        pass

    @staticmethod
    def _init_files(dir_name, html_file_name):
        def __remove_file(file_name):
            if os.path.exists(file_name):
                os.remove(file_name)

        mid_excel_file_path = dir_name + '\\middle.xlsx'
        dest_db_file_path = dir_name + '\\' + html_file_name + '.db'
        dest_excel_file_path = dir_name + '\\'+ html_file_name + '.xlsx'

        __remove_file(mid_excel_file_path)
        __remove_file(dest_db_file_path)
        __remove_file(dest_excel_file_path)
        return mid_excel_file_path, dest_db_file_path, dest_excel_file_path

    # when type_creat_db = 'partialTable', then exclude some commands in the excel sheet
    @staticmethod
    def analysis_function(rule_file, html_file, type_creat_db='partialTable'):
        logger.info(u'开始分析html文件...')

        if type_creat_db not in ['allTable', 'partialTable']:
            raise Exception('analysis_function: invalid type_create_db {0}'.format(type_creat_db))

        dir_name = os.path.dirname(html_file)
        html_file_name = os.path.splitext(os.path.basename(html_file))[0]

        mid_excel_file_path, dest_db_file_path, dest_excel_file_path = FunctionAnalysis._init_files(dir_name,
                                                                                                    html_file_name)
        excel_op = xlsOP(rule_file, dir_name)
        excel_op.parseRuleXls()

        umacDB = umacHtmlDBInterface(html_file, mid_excel_file_path, dest_db_file_path)
        umacDB.create_DB(type_creat_db)

        htmlExcel = umacHtmlExcel(mid_excel_file_path, dest_db_file_path, dest_excel_file_path)
        htmlExcel.all_tables = umacDB.all_tables
        htmlExcel.execute()
        #print 'open commands:','\n'.join(htmlExcel.open_commands)
        logger.info(u'分析结果已保存至文件:{0}'.format(dest_excel_file_path))

        #os.remove(mid_excel_file_path)
        #os.remove(dest_db_file_path)
        return dest_excel_file_path
