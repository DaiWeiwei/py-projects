#-------------------------------------------------------------------------------
# Name:        ??1
# Purpose:
#
# Author:      Administrator
#
# Created:     31-03-2015
# Copyright:   (c) Administrator 2015
# Licence:     <your licence>
#-------------------------------------------------------------------------------

class umacHtmlCondition:
    #??????
    tableName = ''
    fieldName = ''
    condition = ''
    expResult = ''
    queResult = []

    #??????
    def __init__(self):
        tableName = ''
        fieldName = ''
        condition = ''
        expResult = ''
        queResult = []

    def get_query_sql(self):
        querySql = ''
        if self.fieldName is None or self.condition is None:
            if self.fieldName is None and self.condition is None:
                querySql = 'SELECT * FROM '+self.tableName
            elif self.fieldName is None:
                querySql = 'SELECT * FROM '+self.tableName+' WHERE '+self.condition
            else:
                querySql = 'SELECT '+' "'+self.fieldName+'" FROM '+self.tableName
        else:
            querySql = 'SELECT '+' "'+self.fieldName+'" FROM '+ self.tableName+' WHERE '+self.condition

        return querySql

def main():
    print ''

if __name__ == '__main__':
    main()
