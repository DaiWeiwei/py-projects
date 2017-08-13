#coding:utf-8
import codecs
import re
import sys
reload(sys)
sys.setdefaultencoding('gb18030')

from testlib.infrastructure.utility.mylog import get_log,create_log,release_log

class NodeResult:
    def __init__(self):
        self.type = ''
        self.name = ''
        self.match_cmds = []
        self.result = 0
    def __str__(self):
        ss = u'type = {0}\n    name = {1}\n    match_cmds={2}\n    result = {3}'.format(self.type,self.name,';'.join(self.match_cmds),self.result)
        #print ss
        return ss

class FilterResultAnalysis:
    def __init__(self,file_name):
        self._file_name = file_name
        self._cases_result = []
        self._dirs_result = []
        self.log_out = get_log()

        self.log_out.debug('start analysis filter result',flag = 1)

        self.analysis()

        self.log_out.debug('    after analysis filter result',flag = 0)
        self._print_results('dirs',self._dirs_result)
        self._print_results('cases',self._cases_result)

        self._remove_dirs_without_cases()
        self.log_out.debug('    after remove dirs without cases',flag = 0)
        self._print_results('dirs',self._dirs_result)

    def analysis(self):
        content = ''
        with open(self._file_name,'r') as f:
            content = f.read().lower().replace(';'," ").replace('"',"").replace("'","")
        if not content:
            return

        nodes_filter_result = re.findall('case:.+?--match end--', content, re.DOTALL)
        for filter_result in nodes_filter_result:
            node_result = self._analysis_node_result(filter_result)
            if not node_result:
                continue
            self._cases_result.append(node_result)

        nodes_filter_result = re.findall('dir:.+?--match end--', content, re.DOTALL)
        for filter_result in nodes_filter_result:
            node_result = self._analysis_node_result(filter_result)
            if not node_result:
                continue
            self._dirs_result.append(node_result)

    def _remove_dirs_without_cases(self):
        '''
            删除没有用例的目录信息
        '''
        cases_name = [c.name for c in self._cases_result]
        temp_dirs_result  = []
        for dir_result in self._dirs_result:
            if self._item_of_list_start_with(cases_name,dir_result.name):
                temp_dirs_result.append(dir_result)
        self._dirs_result = temp_dirs_result

    @staticmethod
    def _item_of_list_start_with(ls,start_with_str):
        if not start_with_str:
            return False
        for x in ls:
            if x.startswith(start_with_str):
                return True
        return False

    def _analysis_node_result(self,filter_result):
        node_result = NodeResult()
        m = re.search('(case|dir):(.+)',filter_result)
        if not m:
            return None
        node_result.type = m.group(1)
        node_result.name = '{0}'.format(m.group(2))

        m = re.search(r'match result = (\d)',filter_result)
        if not m:
            return None
        node_result.result = m.group(1)
        if node_result.result != '1':
            return None
        node_result.match_cmds = re.findall(r'\bmatch:(.+)',filter_result)
        return node_result
    def _parse_match_cmds(self):
        match_cmds = self._get_match_cmds()

    def _get_match_cmds(self):
        match_cmds = []
        for result in self._cases_result:
            if not result.match_cmds:
                continue
            match_cmds.extend(result.match_cmds)
        for result in self._dirs_result:
            if not result.match_cmds:
                continue
            match_cmds.extend(result.match_cmds)
        return list(set(match_cmds))

    def get_result(self):
        match_cmds = []
        for result in self._cases_result:
            if not result.match_cmds:
                continue
            match_cmds.extend(result.match_cmds)
        for result in self._dirs_result:
            if not result.match_cmds:
                continue
            match_cmds.extend(result.match_cmds)
        return list(set(match_cmds))

    def _print_results(self,header,results):
        ls = []
        ls.append('%s:\n' %  header)
        for rs in results:
            ls.append(u'{0}'.format(rs))
            ls.append( '-' * 20)
        ls.append('---end------')
        ls = [' '* 4 + s for s in ls]
        self.log_out.debug('\n'.join(ls),flag = 0)

if __name__ == '__main__':
    create_log(r'D:\project_version_valid')
    fr = FilterResultAnalysis(r'D:\project_version_valid\umac\combo_mmegngp_sgsn_27\temp_output\\umac_filter_log.txt')
    print fr.get_result()
    release_log()

