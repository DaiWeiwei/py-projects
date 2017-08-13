# coding:utf-8


class ExcelConfig:
    def __init__(self, project_name):
        self._project_name = project_name
        self._status_header_names = []
        self._pstt_dir_header_names = []
        self._sheet_names = []

        self._init_header_names()

    @property
    def status_header_names(self):
        return self._status_header_names

    @property
    def pstt_dir_header_names(self):
        return self._pstt_dir_header_names

    @property
    def sheet_names(self):
        return self._sheet_names

    def _init_header_names(self):
        if self._project_name == 'umac':
            self._status_header_names = [u'需求编号', u'版本号', u'功能名称', u'功能描述', u'当前状态']
            self._pstt_dir_header_names = [u'功能名称', u'目录名称']
            self._sheet_names = ['MME', 'SGSN', u'公共']
        else:
            pass
