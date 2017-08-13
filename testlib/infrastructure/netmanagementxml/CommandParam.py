class CommandParam(object):
    def __init__(self):
        self.name = ''
        self.info = ''
        self.type = 0

    def is_enum(self):
        return self.type == '2'

    def parse(self,param_xml):
        if param_xml is None:
            return
        self.name = param_xml.find('name').text
        self.type = param_xml.find('type').text
        self.info = param_xml.find('info').text
