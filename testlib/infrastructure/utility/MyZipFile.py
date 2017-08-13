# coding:utf-8
import zipfile
import os.path
import os


class MyZipFile(object):
    def __init__(self, filename, mode='r', basedir=''):
        self.filename = filename
        self.mode = mode
        if self.mode in ('w', 'a'):
            self.zip_file = zipfile.ZipFile(filename, self.mode, compression=zipfile.ZIP_DEFLATED)
        else:
            self.zip_file = zipfile.ZipFile(filename, self.mode)
        self.basedir = basedir
        if not self.basedir:
            self.basedir = os.path.dirname(filename)

    def add_file(self, path, arcname=None):
        path = path.replace('//', '/')
        if not arcname:
            if path.startswith(self.basedir):
                arcname = path[len(self.basedir):]
            else:
                arcname = ''
        self.zip_file.write(path, arcname)

    def add_files(self, paths):
        for path in paths:
            if isinstance(path, tuple):
                self.add_file(*path)
            else:
                self.add_file(path)

    def close(self):
        self.zip_file.close()

    def extract_to(self, path):
        for p in self.zip_file.namelist():
            self.extract(p, path)

    def extract(self, filename, path):
        if not filename.endswith('/'):
            f = os.path.join(path, filename)
            dir_name = os.path.dirname(f)
            if not os.path.exists(dir_name):
                os.makedirs(dir_name)
            file(f, 'wb').write(self.zfile.read(filename))


def create_zip_file(zip_file, file_name, arcname):
    z = MyZipFile(zip_file, 'w')
    z.add_file(file_name,arcname)
    z.close()


def extract_zip_file(zip_file, path):
    z = MyZipFile(zip_file)
    z.extract_to(path)
    z.close()
