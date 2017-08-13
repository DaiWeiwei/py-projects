#coding:utf-8

class uMacFunctionCharactor:
    def __init__(self,name,cell_pos,func_cmd_list):
        self._name = name
        self._cell_pos = cell_pos
        self._func_cmd_list = func_cmd_list
        #功能开启有用例、功能开启没用例、功能没开启
        self.function_open_status = ''
        '''
        match_cmd:该功能特性需要满足的匹配命令
        下面这种，表示满足A and (B | C),则表示该功能特性打开
        [ [A],
          [B,C]
        ]
        '''
        self._match_cmd_list = self._parse_cmd_list(self._func_cmd_list)
        #print self._match_cmd_list

    def _parse_cmd_list(self,cmd_list):
        result_cmd_list =[]
        for cmd in cmd_list:
            temp_cmd_list = cmd.split(' or ')
            result_cmd_list.append(temp_cmd_list)
        return result_cmd_list

    @property
    def cmd_list(self):
        return self._match_cmd_list
    @property
    def cell_pos(self):
        return self._cell_pos

    def _is_merged_cell(self):
        return (self._cell_pos[0] + 1 < self.cell_pos[1])

    def __str__(self):
        ls = []
        ls.append('name:'+self._name)
        ls.append('cell pos:'+str(self._cell_pos))
        if self._is_merged_cell():
            ls.append('merged cell')
        ls.append('cmd:')
        for cmd in self.cmd_list:
            try:
                ls.append('   {0}'.format(','.join(cmd)))
            except:
                pass
        ls.append(u'des:{0}'.format(self.function_open_status))
        ls = [' '*4 + s for s in ls]
        return '\n'.join(ls)

if __name__ == '__main__':
    uMacFunctionCharactor('',None,['show license:7013=on or show license:6006=on','show license:7013=on or show license:6006=on','aaa'])


