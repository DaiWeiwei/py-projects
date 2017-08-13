import logging

class umacHtmlLog:
    
    log = None
    def __init__(self):
        self.log = None
        
    def getLogging(self,logName):
        self.log = logging.getLogger(logName)
        logging.basicConfig(level=logging.INFO,
                            format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                            datefmt='%m-%d %H:%M',
                            filename='./logg.txt',
                            filemode='w')
        console = logging.StreamHandler()
        console.setLevel(logging.INFO)
        formatter=logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
        console.setFormatter(formatter)
        self.log.addHandler(console)
        
        return self.log
    
def main():
    htmlLog = umacHtmlLog('umacHtmlLog')      
    testLog = htmlLog.getLogging()
    testLog.error('........test1')
    testLog.info('........test2')
    testLog.exception('........test3')
if __name__ == '__main__':
    main()
