# coding:utf-8
from testlib.domain.ExternalExcelConfigData import ExternalExcelConfigData


class FileService:
    # 返回 状态为open的pstt目录名称
    # status_excel_file: 内含 功能名称 ，状态
    # pstt_dir_name_excel_file: 内含 功能名称，pstt目录名称
    # project_name: 项目名称，即umac,xgw
    # 通过功能名称做关联，把状态=open的pstt目录名称返回
    @staticmethod
    def get_pstt_dir_names_from_external_excel_config_data(status_excel_file, pstt_dir_name_excel_file, project_name):
        eec = ExternalExcelConfigData(status_excel_file,
                                      pstt_dir_name_excel_file,
                                      project_name)
        return eec.get_pstt_dir_names()
