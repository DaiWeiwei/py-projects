# coding=utf-8
import logging
from testlib.infrastructure.utility.envpara.EnvPara import Singleton
from types import DictType
import re


class EnvConst(Singleton):
    ''' 
    load env dataset   
    '''
    CLOUD_JSON_DESC = "Description"
    CLOUD_JSON_NAME = "name"
    CLOUD_JSON_VALUE = "value"
    CLOUD_JSON_ATTR = "attributes"
    CLOUD_JSON_ELEM = "elements"

    CONFIG_TAG_NEID = "neId"
    CONFIG_TAG_RADIOMODE = "radioMode"
    CONFIG_TAG_IP = "ip"
    CONFIG_TAG_ID = "id"
    CONFIG_TAG_SUBNETID = "subnetId"
    CONFIG_TAG_USERNAME = "userName"
    CONFIG_TAG_PASSWORD = "password"
    CONFIG_TAG_NTPSERVERIP = "ntpServerIp"
    CONFIG_TAG_TYPE = "type"
    CONFIG_TAG_SLOT = "slot"
    CONFIG_TAG_UEDATACARDID = "ueDataCardId"
    CONFIG_TAG_UEPCIP = "uePcIp"
    CONFIG_TAG_PDNIP = "pdnIp"
    CONFIG_TAG_CONTROLIP = "controlIp"
    CONFIG_TAG_RACK = "rack"
    CONFIG_TAG_FREQDL = "freqDl"

