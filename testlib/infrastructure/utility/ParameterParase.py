# coding=utf-8
import string


class ParameterParase(object):
    def __init__(self, parm):
        self._result = {}
        self._parase('', parm)

    @property
    def result(self):
        return self._result.items()

    def _parase(self, path, parameter):
##        if parameter.is_field():
##            self._save_value(path, parameter)
##        elif len(parameter.value) == 0:
##             self._save_value(path, parameter)
##        else:
##            for name, value in parameter.items():
##                new_path = self._get_param_path(path, name)
##                parameter = Parameter(value)
##                self._parase(new_path, parameter)

        for name, value in parameter.items():
            new_path = self._get_param_path(path, name)
            parameter = Parameter(value)
            if parameter.is_field_or_empty_struct_field():
                self._save_value(new_path, parameter)
            else:
                self._parase(new_path, parameter)

    def _save_value(self, path, parameter):
        if parameter.is_none():
            return
        self._result[path] = parameter.value

    def _get_param_path(self, path, name):
        if name == '_value':
            return path
        if path:
            return '%s.%s' % (path, name)
        else:
            return name


class Parameter(object):
    def __init__(self, _dict):
        self.parameter = _dict
        if '_value' in self.parameter:
            self.value =self.parameter['_value']
            del self.parameter['_value']
        else:
            self.value= 'None'

    def is_none(self):
        return self.value== 'None'

    def is_field_or_empty_struct_field(self):
        return len(self.value) == 0 or len(self.items())==0

##    def is_field(self):
##        return len(self.items) == 0

##    @property
##    def value(self):
##        return str(self.parameter.get('_value','${None}'))

    def items(self):
        return self.parameter.items()
