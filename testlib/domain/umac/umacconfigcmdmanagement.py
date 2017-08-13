#coding:utf-8

import re

OP_TYPE_CONTAINS = 0#包含，key=value
OP_TYPE_CONTAINS_NAME_BUT_NOT_EQ_VALUE = 1 #key!=value
OP_TYPE_CONTAINS_NAME = 2 #key

class UmacConfigCmdParasRow:
    def __init__(self):
        self.paras = {}

    def set_value(self,name,value):
        name = name.strip()
        value = value.strip()
        self.paras[name] = value

    def clear(self):
        self.paras.clear()

    def has_para(self):
        return len(self.paras) > 0

##    def contains(self,rhs):
##        return self._compare(rhs, OP_TYPE_CONTAINS)
##
##    def has_para_name_but_not_equal_value(self,rhs):
##        return self._compare(rhs, OP_TYPE_CONTAINS_NAME_BUT_NOT_EQ_VALUE)
##
##    def has_para_name(self,rhs):
##        return self._compare(rhs, OP_TYPE_CONTAINS_NAME)
##
##    def _compare(self, rhs, op_type):
##        if len(self.paras) < len(rhs.paras):
##            return False
##        for k,v in rhs.paras.items():
##            if k not in self.paras:
##                return False
##            if op_type == OP_TYPE_CONTAINS:
##                if v != self.paras.get(k,None):
##                    return False
##            elif op_type == OP_TYPE_CONTAINS_NAME_BUT_NOT_EQ_VALUE:
##                if v == self.paras.get(k,None):
##                    return False
##            elif op_type == OP_TYPE_CONTAINS_NAME:
##                pass
##        return True
    def __str__(self):
        ls = []
        for k,v in self.paras.items():
            ls.append('{0} = {1}'.format(k,v))
        return ','.join(ls)

class UmacConfigCmd:
    def __init__(self,_cmd):
        self.cmd = _cmd
        self.cmd_name = ''
        self.k_eq_v = UmacConfigCmdParasRow()
        self.k_not_eq_v = UmacConfigCmdParasRow()
        self.k_no_v = UmacConfigCmdParasRow()

    def analysis(self):
        cmd = self.cmd
        if len(cmd) == 0:
            return False
        cmd_k_v = cmd.split(':')
        self.cmd_name = cmd_k_v[0].strip(' ')
        if len(cmd_k_v) > 1:
            paras = ',{0},'.format(cmd_k_v[1].rstrip(' ;,'))
            self._analysis_k_equal_v(paras)
            self._analysis_k_not_equal_v(paras)
            self._analysis_k_no_v(paras)
        return True

    def _analysis_k_equal_v(self,cmd_paras):
        return self._analysis_cmd_paras(r"(\w+)\s*=\s*([^,]*)",cmd_paras,self.k_eq_v)

    def _analysis_k_not_equal_v(self,cmd_paras):
        return self._analysis_cmd_paras(r"(\w+)\s*!=\s*([^,]*)",cmd_paras,self.k_not_eq_v)

    def _analysis_k_no_v(self,cmd_paras):
        cmd_paras = re.sub(r'(?<=,)\s*(\w+)\s*(?=,)',r'\1=pstt_exist_key',cmd_paras)
        return self._analysis_cmd_paras(r"(\w+)=(pstt_exist_key)",cmd_paras,self.k_no_v);

    def _analysis_cmd_paras(self,pattern,cmd_paras, config_cmd_para_row):
        config_cmd_para_row.clear()
        result = re.findall(pattern,cmd_paras)
        if not result:
            return False
        for item in result:
            config_cmd_para_row.set_value(item[0],item[1])
        return True

    def contains(self, rhs):
        '''rhs是否是self的运算子集
           不允许出现 a=b 在k_eq_v里面，在k_not_eq_v里出现a
           如果都没参数，也返回True
        '''
        for k,v in rhs.k_eq_v.paras.items():
            #如果k 在self.k_eq_v,则必须相等
            if k in self.k_eq_v.paras:
                if v != self.k_eq_v.paras[k]:
                    return False
                else:
                    continue
            else:
                #否则，如果k在self.k_not_eq_v,则必须不等
                if k in self.k_not_eq_v.paras:
                    if v == self.k_not_eq_v.paras[k]:
                        return False
                    else:
                        continue
                else:
                    #即不在self.k_eq_v,也不在self.k_not_eq_v，则返回False
                    return False

        for k,v in rhs.k_not_eq_v.paras.items():
            if k in self.k_not_eq_v.paras:
                if v != self.k_not_eq_v.paras[k]:
                    return False
                else:
                    continue
            else:
                if k in self.k_eq_v.paras:
                    if v == self.k_eq_v.paras[k]:
                        return False
                    else:
                        continue
                else:
                    #即不在self.k_eq_v,也不在self.k_not_eq_v，则返回False
                    return False

        for k,_ in rhs.k_no_v.paras.items():
            if k not in self.k_eq_v.paras \
                and k not in self.k_not_eq_v.paras \
                and k not in self.k_no_v.paras:
                    return False
        return True

    def __str__(self):
        ls = []
        ls.append('-'*10)
        ls.append('cmd:'+self.cmd)
        ls.append('cmd name:'+self.cmd_name)
        ls.append('cmd paras:')
        ls.append('  k = v:')
        ls.append("    "+str(self.k_eq_v))
        ls.append('  k != v:')
        ls.append("    "+str(self.k_not_eq_v))
        ls.append('  k:')
        ls.append("    "+str(self.k_no_v))
        ls.append('-'*10)
        return '\n'.join(ls)


class UmacConfigCmdParasTable:
    def __init__(self):
        self.umac_config_cmd_list = []
    def append_umac_config(self, umac_config):
        self.umac_config_cmd_list.append( umac_config )

class UmacConfigCmdManagement:
    def __init__(self):
        self._dict_cmds = {}#cmdname:UmacConfigCmdParasTable

    def append_cmd(self,cmd):
        cmd = cmd.lower()
        if cmd.startswith('ADD MME APN MODIFICATION:'.lower()):
            pass
        umac_config_cmd = UmacConfigCmd(cmd)
        if not umac_config_cmd.analysis():
            #self.log_out.error('append invalid cmd:'.format(cmd))
            return False
        if umac_config_cmd.cmd_name not in self._dict_cmds:
            self._dict_cmds[umac_config_cmd.cmd_name] = UmacConfigCmdParasTable()
        self._dict_cmds[umac_config_cmd.cmd_name].append_umac_config(umac_config_cmd)
        return True
    def is_cmd_exists(self,cmd):
        cmd = cmd.lower()
        umac_config_cmd = UmacConfigCmd(cmd)
        if not umac_config_cmd.analysis():
            #self.log_out.error('not exists invalid cmd:'.format(cmd))
            return False
        if umac_config_cmd.cmd_name not in self._dict_cmds:
            #nself.log_out.error('not exists cmd name:'.format(cmd))
            return False
        umac_config_cmd_paras_table = self._dict_cmds[umac_config_cmd.cmd_name]
        for row_umac_config_cmd in umac_config_cmd_paras_table.umac_config_cmd_list:
            if row_umac_config_cmd.contains(umac_config_cmd):
                #print 'contains:',row_umac_config_cmd
                return True
##            row_k_eq_v = umac_config_cmd_paras_row.k_eq_v
##            row_k_not_eq_v = umac_config_cmd_paras_row.k_not_eq_v
##            row_k_no_v = umac_config_cmd_paras_row.k_no_v
##            if umac_config_cmd.k_eq_v.has_para():
##                #k=v,必须在全集的k=v里面，且不再k!=v里面,待继续思考
##                if not umac_config_cmd_paras_row.contains(umac_config_cmd.k_eq_v):
##                    continue
##            if umac_config_cmd.k_not_eq_v.has_para():
##                if not umac_config_cmd_paras_row.has_para_name_but_not_equal_value(umac_config_cmd.k_not_eq_v):
##                    continue
##            if umac_config_cmd.k_no_v.has_para():
##                if not umac_config_cmd_paras_row.has_para_name(umac_config_cmd.k_no_v):
##                    continue
##            return True
        return False

if __name__ == '__main__':
    umac_config_cmd = UmacConfigCmd("show license : a, b=5 , c!= 2, d")
    r = umac_config_cmd.analysis()
    print umac_config_cmd


