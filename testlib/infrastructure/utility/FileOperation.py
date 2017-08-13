import os
import datetime

class FileOperation(object):
    @staticmethod
    def create_directory(dir_path):
        try:
            os.makedirs(dir_path)
        except:
            pass

    @staticmethod
    def get_file_name_of_current_time():
        #return '20160405_111324'
        return str(datetime.datetime.now()).replace('-','').replace(' ','_').replace(':','')[:15]


