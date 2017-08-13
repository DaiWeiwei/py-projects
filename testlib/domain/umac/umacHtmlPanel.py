# -*- coding: utf-8 -*- 
import umacHtmlFrame
import wx
import umacHtmlDBInterface
import umacHtmlExcel
import xlop
import umacHtmlMain
import os
import umacHtmlLog

class umacHtmlPanel(wx.Panel):
    src_ExcelFile_Path = ''
    src_HtmlFile_Path  = ''
    mid_ExcelFile_Path = ''
    dest_DbFile_Path   = ''
    dest_ExcelFile_Path = ''
    
    excelFileTc = None
    htmlFileTc  = None
    resultTc = None 
    dbCombox = None
    langCombox = None
    
    dbTypeEng = []
    type_creat_db=''
    langTypeEng = []
    type_lang = '' 
    
    panelLog = None 
  
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        grid = wx.GridBagSizer(hgap=5, vgap=5)
        
        excelFileText = wx.StaticText(self, label=u"功能规则表")  
        grid.Add(excelFileText, pos=(2, 0), flag=wx.LEFT|wx.TOP, border=10)  
  
        self.excelFileTc = wx.TextCtrl(self,style=wx.TE_READONLY)  
        grid.Add(self.excelFileTc, pos=(2, 1), span=(1, 3), flag=wx.TOP|wx.EXPAND,   
            border=5)  
          
        excelFileButton = wx.Button(self, label="Browse...")  
        grid.Add(excelFileButton, pos=(2, 4), flag=wx.TOP|wx.RIGHT, border=5) 
        self.Bind(wx.EVT_BUTTON, self.OpenExcelFile, excelFileButton) 
          
        htmlFileText = wx.StaticText(self, label="Html源文件")  
        grid.Add(htmlFileText, pos=(3, 0), flag=wx.TOP|wx.LEFT, border=10)  
  
        self.htmlFileTc = wx.TextCtrl(self,style=wx.TE_READONLY)  
        grid.Add(self.htmlFileTc, pos=(3, 1), span=(1, 3),   
            flag=wx.TOP|wx.EXPAND, border=5)  
  
        htmlFileButton = wx.Button(self, label="Browse...")  
        grid.Add(htmlFileButton, pos=(3, 4), flag=wx.TOP|wx.RIGHT, border=5)
        self.Bind(wx.EVT_BUTTON, self.OpenHtmlFile, htmlFileButton) 
        
        dbText = wx.StaticText(self, label=u"建库方式") 
        grid.Add(dbText,pos=(4,0),flag=wx.TOP|wx.LEFT, border=10) 
        
        dbType = [u'不建数据库',u'全部表建库',u'部分表建库']
        self.dbTypeEng = ['NO','allTable','partialTable']
        self.type_creat_db=''
        self.dbCombox = wx.ComboBox(self,choices=dbType)  
        grid.Add(self.dbCombox,pos=(4, 1), span=(1, 1),   
            flag=wx.TOP|wx.EXPAND, border=5)
        self.Bind(wx.EVT_COMBOBOX, self.OnSelectDBType, self.dbCombox)
        
#增加版本语言    
#         langText = wx.StaticText(self, label=u"版本语言") 
#         grid.Add(langText,pos=(5,0),flag=wx.TOP|wx.LEFT, border=10)
#         langType = [u'英文',u'中文']
#         self.langTypeEng = ['English','Chinese']
#         self.type_lang = '' 
#         self.langCombox = wx.ComboBox(self,choices=langType)  
#         grid.Add(self.langCombox,pos=(5, 1), span=(1, 1),   
#             flag=wx.TOP|wx.EXPAND, border=5)
#         self.Bind(wx.EVT_COMBOBOX, self.OnSelectLangType, self.langCombox)
        
        text5 = wx.StaticText(self, label=u"分析结果")
        grid.Add(text5, pos=(5, 0), flag=wx.TOP|wx.LEFT, border=10)
        
        self.resultTc = wx.TextCtrl(self,style=wx.TE_AUTO_SCROLL|wx.TE_MULTILINE)  
        grid.Add(self.resultTc, pos=(6, 0), span=(13, 5),  
            flag=wx.TOP|wx.EXPAND|wx.BOTTOM, border=5)


        button3 = wx.Button(self, label=u"运行",size=(70, 30))
        grid.Add(button3, pos=(19, 3), span=(2, 1),flag=wx.TOP|wx.LEFT|wx.EXPAND|wx.BOTTOM)
        self.Bind(wx.EVT_BUTTON, self.OnRun, button3)
        
        button4 = wx.Button(self, label=u"退出",size=(70, 30))
        grid.Add(button4, pos=(19, 4), span=(2, 1),flag=wx.EXPAND|wx.BOTTOM)
        self.Bind(wx.EVT_BUTTON, self.OnCancel, button4)
        
        grid.AddGrowableCol(2)
        
        grid.AddGrowableRow(6)   
          
        self.SetSizer(grid)
        
        self.panelLog = umacHtmlLog.umacHtmlLog().getLogging('umacHtmlPanel')
        
    def OnCancel(self, event):
        wx.Exit()
        
    def OnSelectDBType(self, event):
        item = event.GetSelection()
        self.type_creat_db = self.dbTypeEng[item]
        
    def OnSelectLangType(self, event):
        item = event.GetSelection()
        self.type_lang = self.langTypeEng[item]
        
    def OpenExcelFile(self, event):
        dialog = wx.FileDialog(self,"Open file...",os.getcwd(),style=wx.OPEN,wildcard="*.xlsx")
        if dialog.ShowModal() == wx.ID_OK:
            self.src_ExcelFile_Path = dialog.GetPath()
            self.excelFileTc.Clear()
            self.excelFileTc.AppendText(self.src_ExcelFile_Path)
        dialog.Destroy()
        
    def OpenHtmlFile(self, event):
        dialog = wx.FileDialog(self,"Open file...",os.getcwd(),style=wx.OPEN,wildcard="*.html")
        if dialog.ShowModal() == wx.ID_OK:
            self.src_HtmlFile_Path = dialog.GetPath()
            self.htmlFileTc.Clear()
            self.htmlFileTc.AppendText(self.src_HtmlFile_Path)
        dialog.Destroy()

   
    def OnRun(self,event):
        if self.src_ExcelFile_Path is '':
            self.resultTc.AppendText(u'请选择需要分析的功能文件.\r\n')
            return
        if self.src_HtmlFile_Path is '':
            self.resultTc.AppendText(u'请选择需要分析的Html数据文件.\r\n')
            return
        dirName = os.path.dirname(self.src_HtmlFile_Path)       
        htmlFileName = os.path.splitext(os.path.basename(self.src_HtmlFile_Path))[0]

        self.mid_ExcelFile_Path = dirName + '\\middle.xlsx'
        self.dest_DbFile_Path   = dirName + '\\' +htmlFileName + '.db'
        self.dest_ExcelFile_Path = dirName + '\\' +htmlFileName +'.xlsx'
                
        if self.type_creat_db is '':
            self.resultTc.AppendText(u'请选择建库方式.\r\n')
            return
        
#增加版本语言     
#         if self.type_lang is '':
#             self.resultTc.AppendText(u'请选择版本语言.\r\n')
#             return
#         

#         lang = 0
#         print self.type_lang
#         if self.type_lang is 'Chinese':
#             lang = 1
        
        #print self.type_creat_db
        if self.type_creat_db == 'NO':
            #print os.path.exists(self.dest_DbFile_Path)
            if os.path.exists(self.dest_DbFile_Path):
                pass
            else:
                self.resultTc.AppendText(u'需要分析的数据库文件不存在，请先建库！\r\n')
                return
        
        self.panelLog.info('Start analyze excel file...')
        excelOp = xlop.xlsOP(self.src_ExcelFile_Path,dirName)
        excelOp.parseRuleXls()
        #excelOp.writeTmpXlsx(self.mid_ExcelFile_Path)
      
        
        if self.type_creat_db =='allTable' or self.type_creat_db == 'partialTable':
            self.panelLog.info('Start create DB...')
            umacDB = umacHtmlDBInterface.umacHtmlDBInterface(self.src_HtmlFile_Path,self.mid_ExcelFile_Path,self.dest_DbFile_Path)        
            umacDB.create_DB(self.type_creat_db)

        self.panelLog.info('Start analyze data...')
        htmlExcel = umacHtmlExcel.umacHtmlExcel(self.mid_ExcelFile_Path,self.dest_DbFile_Path,self.dest_ExcelFile_Path)
        htmlExcel.execute()
      
        self.resultTc.AppendText(u'分析结果已保存至文件:'+self.dest_ExcelFile_Path+'\r\n')
        self.panelLog.info('Finish!')
    
if __name__ == '__main__':
    app = wx.App(False)
    frame = umacHtmlFrame.umacHtmlFrame(None, u'umac功能开启分析系统')
    panel = umacHtmlPanel(frame)
    frame.Show()
    app.MainLoop()
