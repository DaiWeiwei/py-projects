# -*- coding: utf-8 -*-
from robot.api import logger
import re
import os

class uMacLicense:
    def get_and_save_license(self,umac_dut,license_path):
        license_content = self._get_license(umac_dut)
        self._save_to_file('{0}/license.txt'.format(license_path),license_content)
        analysis_license_content = self._analysis_license(license_content)
        self._save_to_file('{0}/analysis_license.txt'.format(license_path),analysis_license_content)

    def _get_license(self,umac_dut):
        try:
            umac_dut.login_clean()
            cmd = 'SHOW LICENSE;'
            cmd_result = umac_dut.execute_command(cmd)
            return cmd_result.return_string
        except:
            logger.warn("get show license fail")
            return ""
    def _analysis_license(self,license_content):
##        license_content = '''
##        ACK SHOW LICENSE:INFO="0"-"COMBO_MMEGNGP_SGSN"-"2015-03-10"-"9999-12-31"-"combo_mme_gngpsgsn1510B12_IWS"-"combo_mme_gngpsgsn1510B12_IWS"-""-"2915861",ITEMINFO="Register User Number"-"7001"-"10000"&"Max Bearer/PDP Context Number"-"7002"-"10000"&"SGSN Support Direct Tunnel Function"-"7005"-"ON"&"Support UBAS-CHR Function"-"7010"-"ON"&"Support LCS Function"-"7011"-"ON"&"MME Support CSFB Function"-"7012"-"ON"&"Support IPv6 Function"-"7013"-"ON"&"MME Support SRVCC Function"-"7014"-"ON"&"GnGp SGSN Support MOCN Function"-"7015"-"ON"&"2G Online User Number"-"7016"-"10000"&"3G Online User Number"-"7017"-"10000"&"LTE Online User Number"-"7018"-"10000"&"Online User Number"-"7019"-"10000"&"2G Register User Number"-"7020"-"10000"&"3G Register User Number"-"7021"-"10000"&"LTE Register User Number"-"7022"-"10000"&"MME Support CSG Function"-"7023"-"ON"&"MME Support eMBMS Function"-"7024"-"ON"&"MME Support NITZ Function"-"7025"-"ON"&"Max Dynamic eNodeB Number"-"7026"-"100"&"MME Support IPSEC Function"-"7027"-"ON"&"SGSN Support LCS Number"-"7028"-"100"&"MME Support LCS Number"-"7029"-"100"&"MME Support Relay Function"-"7030"-"ON"&"MME Support LIPA Function"-"7031"-"ON"&"MME Support Policy Paging Function"-"7032"-"ON"&"SGSN Support Large Number of Served PLMNs"-"7033"-"ON"&"MME Support TCE Function"-"7034"-"ON"&"Support User IP and Location Relationship Function"-"7035"-"ON"&"MME Support Signaling Storm Restraint"-"7036"-"ON"&"MME Support S102 Interface"-"7037"-"ON"&"MME Support eNB User Plane IP Address Type Optimization"-"7038"-"ON"&"MBR for Uplink of SGSN Supporting(Mbps)"-"7039"-"256"&"MBR for Downlink of SGSN Supporting(Mbps)"-"7040"-"256"&"GBR for Uplink of SGSN Supporting(Mbps)"-"7041"-"256"&"GBR for Downlink of SGSN Supporting(Mbps)"-"7042"-"256"&"MME Support Handover with Optimization to eHRPD"-"7043"-"ON"&"SGSN Support NITZ Function"-"7044"-"ON"&"MME Service Restoration Function"-"7049"-"ON"&"MME Support IWS Function"-"7050"-"ON"&"Maximum IWS Users by Single Module"-"7051"-"100"&"MME Support P-CSCF Restoration Function"-"7052"-"ON"&"MME Support S3 Interface"-"7055"-"ON",SYS_RESULT="0",SYS_LASTPACK="1"
##        '''
        result = re.findall(r'(?:=|&)"([^"]+)"-"(\d+)"-"([^"]+)"',license_content)
        ret_string = []
        for rs in result:
            ret_string.append('%s,%s,%s' % rs)
        return '\n'.join(ret_string)

    def _save_to_file(self,file_name,content):
        with open(file_name,'w') as f:
            f.write(content)

    def parse_license_file(self,licence_file):
        if not os.path.exists(licence_file):
            return []
        ret_list = []
        with open(licence_file,'r') as f:
            content = f.read()
            result_list = re.findall(r"[^,]+,(\d+),(\w+)",content)
            for result in result_list:
                ret_list.append('show license:{0}={1}'.format(result[0],result[1]))
        return ret_list

if __name__ == '__main__':
##    from testlib.infrastructure.device.umac.umac import uMac
##
##    umac_dut = uMac('195.137.81.55','7722','admin','','27')
##    uMacLicense().get_and_save_license(umac_dut,'c:')
    a = ''
    b = ''
    d = {'a':a,'b':b}
    for k in d.keys():
        d[k] = k
    print d
    print a,b
