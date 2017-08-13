# coding:utf-8
import xlrd  # testlib.infrastructure.sitePackages.xlrd
from testlib.infrastructure.projectexternalexcelconfig.ExcelConfig import ExcelConfig


class ExternalExcelConfigData:
    def __init__(self, status_excel_file, pstt_dir_name_excel_file, project_name):
        self._status_excel_file = status_excel_file
        self._pstt_dir_name_excel_file = pstt_dir_name_excel_file
        self._project_name = project_name.lower()
        self._excel_config = ExcelConfig(self._project_name)

    def get_pstt_dir_names(self):
        pstt_dir_names = []
        status_book = xlrd.open_workbook(self._status_excel_file)
        pstt_dir_book = xlrd.open_workbook(self._pstt_dir_name_excel_file)
        for sheet_name in self._excel_config.sheet_names:
            status_sheet = self.get_sheet_content(status_book, sheet_name)
            pstt_dir_sheet = self.get_sheet_content(pstt_dir_book, sheet_name)

            function_names_of_status_sheet = self._get_function_names_where_status_is_open(status_sheet)
            dict_of_pstt_dir_sheet = self._get_dict_of_function_names_to_pstt_dir_names(pstt_dir_sheet)

            pstt_dir_names.extend([dict_of_pstt_dir_sheet[name] for name in function_names_of_status_sheet if dict_of_pstt_dir_sheet.has_key(name)])

        return pstt_dir_names

    def _get_function_names_where_status_is_open(self, status_content):
        return [row[2] for row in status_content if row[4] == 'Open']

    def _get_dict_of_function_names_to_pstt_dir_names(self, pstt_dir_content):
        d = {}
        for row in pstt_dir_content:
            d[row[0]] = row[1]
        return d

    def get_excel_content(self, excel_file):
        content = []
        book = xlrd.open_workbook(excel_file)
        for sheet_name in self._excel_config.sheet_names:
            temp = self.get_sheet_content(book, sheet_name)
            if not temp:
                content
            content.append(temp)
        return content

    def get_sheet_content(self, book, sheet_name):
        sheet = book.sheet_by_name(sheet_name)
        if not sheet:
            return None
        content = []
        rows = sheet.nrows
        cols = sheet.ncols
        # print '*'*10
        # print 'sheet name:',sheet_name
        for i in range(1, rows):
            # print ' '*4,sheet.row_values(i)
            content.append(sheet.row_values(i))
        # print '*'*10
        return content


if __name__ == '__main__':
    eec = ExternalExcelConfigData(ur'E:\linxing\ProjectVersionValid\doc\广东江门移动-14.20.P2B3a.xlsx',
                                  ur'E:\linxing\ProjectVersionValid\doc\pstt目录.xlsx',
                                  'umac')
    print eec.get_pstt_dir_names()
