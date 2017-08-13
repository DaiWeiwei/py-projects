# -*- coding: utf-8 -*- 

import umacHtmlDBInterface
import umacHtmlExcel
import xlop
import umacHtmlLog
import wx
import umacHtmlFrame
import umacHtmlPanel
import os

def main():
    mainLog = umacHtmlLog.umacHtmlLog().getLogging('umacHtmlMain')
    src_HtmlFile_Path = r'F:\aa\result\BR_20140307130651.html'
    src_ExcelFile_Path = r'F:\aa\result\middle.xlsx'
    dest_DbFile_Path = r'F:\aa\result\BR_20140307130651.DB'
    dest_ExcelFile_Path = r'F:\aa\result\finalResult.xlsx'
    se_ExcelFile_Path = r'F:\aa\result\H3GSE.xlsx'


    excelOp = xlop.xlsOP(se_ExcelFile_Path)
    excelOp.parseRuleXls()
    excelOp.writeTmpXlsx(r'D:\Workspace\Html\config\example.xlsx')
    
    mainLog.info('Srart Create DB')
    umacDBIn = umacHtmlDBInterface.umacHtmlDBInterface(src_HtmlFile_Path,src_ExcelFile_Path,dest_DbFile_Path)
    umacDBIn.create_DB('allTable')
    mainLog.info('Create DB successfully')
    
    htmlExcel = umacHtmlExcel.umacHtmlExcel(src_ExcelFile_Path,dest_DbFile_Path,dest_ExcelFile_Path)
    htmlExcel.execute()
    
    mainLog.info('END')

def mainGui():
    
    mainLog = umacHtmlLog.umacHtmlLog().getLogging('umacHtmlMain')
    app = wx.App(False)
    frame = umacHtmlFrame.umacHtmlFrame(None, u'umac功能开启分析系统')
    panel = umacHtmlPanel.umacHtmlPanel(frame)
    frame.Show()
    app.MainLoop()

if __name__ == '__main__':
    mainGui()

    
