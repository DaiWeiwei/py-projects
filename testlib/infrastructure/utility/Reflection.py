# coding=utf-8


class Reflection:
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'
    
    @staticmethod 
    def create_obj(packetName, className, *args):
        module = __import__(packetName, globals(), locals(), [className])
        obj = getattr(module, className)         
        return obj(*args)  

    @staticmethod 
    def invoke(obj, methodName, *args):
        method = getattr(obj, methodName)
        return method(*args)
    
if __name__ == '__main__':
    obj = Reflection.create_obj('domain.cell.Cp', 'Cp', 'aaa')
    Reflection.invoke(obj, 'get_cpid')

