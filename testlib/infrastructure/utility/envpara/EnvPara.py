# coding=utf-8
import re
import sys
from types import DictType
from robot.api import logger
from testlib.infrastructure.resource.resource.service.DependenceManager import DomainObjectInjecter


class Singleton(object):
    def __new__(cls, *args, **kw):
        if not hasattr(cls, '_instance'):
            orig = super(Singleton, cls)
            cls._instance = orig.__new__(cls, *args, **kw)
        return cls._instance


class EnvPara(Singleton):
    '''
    load env dataset
    '''
    _DEVICE_ID_IN_ENV = 'id'
    _DEVICE_TYPE_IN_ENV = 'type'
    _PARENT_ID_IN_ENV = 'parentId'
    _TOOL_ID_TAIL_IN_ENV = 'ToolId'

    _DEVICES_IN_EVN = 'devices'
    _LINKS_IN_EVN = 'links'

    _LINK_TYPE_REQ_IN_EVN = 'reqType'
    _LINK_TYPE_IN_EVN = 'link'
    _LINK_DEVICE_ID_IN_ENV = 'id'
    _LINK_NODES_IN_EVN = 'nodes'

    _LINK_NAME_IN_EVN = 'name'
    _LINK_DEVICE_IN_EVN = 'device'
    _LINK_PORT_IN_EVN = 'port'
    _CREATE_LINK_IN_EVN = 'createLink'
    CREATED_DEVICES = []

    def load_env_para(self, para):
        '''
            load env para in sence before starting testing
        '''
        self._device_params = para
        pass

    # def load_config_para(self, config):
    # self.config = config
    #     self._device_params = {}
    #     # for device in self.config[self._DEVICES_IN_EVN]:
    #     # self._device_params[device[self._DEVICE_ID_IN_ENV]] = device
    #     for device in self.config[self._LINKS_IN_EVN]:
    #         self._device_params[device[self._DEVICE_ID_IN_ENV]] = device

    def get_attribute(self, deviceId, attributeName, defaultValue=None):
        '''
            get device attribute value by device id
            if attributeName == None or "" return deviceId's value
            Demo:
            |${attributeValue}=|get_attribute|'enodeb1'|'enodebIp'|
        '''
        return self._get_attribute(deviceId, attributeName, defaultValue, True)

    def _get_attribute(self, deviceId, attributeName, defaultValue=None, reportWarn=True):
        if self._check_device_id(deviceId) is None:
            return None

        if attributeName == "" or attributeName == None:
            logger.debug(deviceId + ':' + attributeName + '=' + str(self._device_params[deviceId]))
            return self._device_params[deviceId]
        deviceAttributeValue = self._get_device_attr(self._device_params[deviceId], attributeName)

        if deviceAttributeValue is None:
            if reportWarn:
                logger.debug('return default value:' + deviceId + ':' + str(attributeName) + '=None')
                logger.debug(self._device_params[deviceId])
            else:
                logger.debug('return default value:' + deviceId + ':' + attributeName + '=None')
                logger.warn(self._device_params[deviceId])
            return defaultValue

        logger.debug(deviceId + ':' + attributeName + '=' + str(deviceAttributeValue))
        return deviceAttributeValue

    def _check_device_id(self, deviceId):
        '''
        '''
        if deviceId not in self._device_params.keys():
            logger.debug('''There is no device(deviceid=\'%s\') in environment data.''', deviceId)
            return None
        return deviceId

    def _get_device_attr(self, envDataSet, attributeName):
        deviceAttributes = envDataSet
        for attributeKey in deviceAttributes.keys():
            if attributeName == attributeKey:
                return deviceAttributes[attributeName]
            elif type(deviceAttributes[attributeKey]) is DictType:
                attributeValue = self._get_device_attr(deviceAttributes[attributeKey], attributeName)
                if attributeValue is not None:
                    return attributeValue
            else:
                continue
        else:
            return None


    def get_link_devices(self, deviceId, toolType=''):
        '''
        get devices list in the link,which links with deviceId.
        success return device list
        fail return None
        Demo:
        |@{deviceList}=|get_link_devices|'rru1'|'HOC'|
        '''
        if self._check_device_id(deviceId) is None:
            return None
        deviceInLinkList = []
        for deviceName in self._device_params.keys():
            if type(self._device_params[deviceName]) is DictType and self._is_link_node(
                    self._device_params[deviceName]):
                nodes = self._device_params[deviceName][self._LINK_NODES_IN_EVN]
                if len(nodes) < 2:
                    continue
                self._add_node_to_toolList(deviceInLinkList, deviceId, toolType, nodes[0], nodes[1])
                self._add_node_to_toolList(deviceInLinkList, deviceId, toolType, nodes[1], nodes[0])

        if len(deviceInLinkList) > 0:
            return deviceInLinkList
        else:
            logger.info('''There is no device link to \'%s\'.''', deviceId)
            return None

    def _add_node_to_toolList(self, deviceInLinkList, deviceId, toolType, linkNode1, linkNode2):
        if linkNode1.get(self._LINK_DEVICE_IN_EVN, None) == deviceId:
            device = linkNode2.get(self._LINK_DEVICE_IN_EVN, None)
            deviceType = self._get_attribute(device, self._DEVICE_TYPE_IN_ENV, None, False)
            if toolType == '':
                deviceInLinkList.append(device)
            elif deviceType == toolType:
                deviceInLinkList.append(device)
            else:
                pass

    def get_link_attribute(self, srcDeviceId, dstDeviceId, dstAttributeName='port', defaultValue=None):
        '''
        get devices atribute value in the link
        success: return rru1.linkAttributeValue,bpl.linkAttributeValue
        fail: return None,None
        Demo:
        |${rru1OptPort}|${bplOptPort}|get_link_attribute|'rru1' |bpl'|
        '''
        for deviceName in self._device_params.keys():
            if type(self._device_params[deviceName]) is DictType and self._is_link_node(
                    self._device_params[deviceName]):
                nodes = self._device_params[deviceName][self._LINK_NODES_IN_EVN]
                srcDev, srcAttName = self.__get_device_port(nodes, srcDeviceId)
                dstDev, dstAttName = self.__get_device_port(nodes, dstDeviceId)
                if srcDev is not None and dstDev is not None:
                    if srcAttName is not None:
                        srcAttValue = self.get_attribute(srcDeviceId, srcAttName)
                    else:
                        srcAttValue = None
                    if dstAttName is not None:
                        dstAttValue = self.get_attribute(dstDeviceId, dstAttName)
                    else:
                        dstAttValue = None
                    return srcAttValue, dstAttValue
        else:
            return None, None

    def _is_link_node(self, dictDataSet):
        # if self._LINK_TYPE_REQ_IN_EVN in dictDataSet.keys() and \
        #            self._LINK_TYPE_IN_EVN == dictDataSet[self._LINK_TYPE_REQ_IN_EVN]:
        if self._LINK_NODES_IN_EVN in dictDataSet.keys():
            return True
        else:
            return False

    def __get_device_port(self, deviceList, deviceNameIn):

        for node in deviceList:
            if type(node) is DictType:
                deviceName = node.get(self._LINK_DEVICE_IN_EVN, None)
                deviceAttName = node.get(self._LINK_PORT_IN_EVN, None)
                if deviceName == deviceNameIn:
                    return deviceName, deviceAttName
        else:
            return None, None

    def _get_devices_by_type(self, deviceTypeToSearch):
        devicesInSence = []
        for deviceName in self._device_params.keys():
            if type(self._device_params[deviceName]) is DictType:
                deviceTypeInEnv = self._get_attribute(deviceName, self._DEVICE_TYPE_IN_ENV, reportWarn=False)
                if deviceTypeInEnv is not None:
                    matchObj = re.search(deviceTypeToSearch, deviceTypeInEnv, re.IGNORECASE)
                    if matchObj is not None:
                        devicesInSence.append(deviceName)

        if len(devicesInSence) > 0:
            logger.debug('Type: ' + deviceTypeToSearch + ' devices list is' + str(devicesInSence))
            return devicesInSence
        else:
            logger.info('Type: ' + deviceTypeToSearch + ' devices list is None')
            return None

    def __get_parent(self, deviceId):
        if self._check_device_id(deviceId) is None:
            return None
        parentId = self._get_attribute(deviceId, self._PARENT_ID_IN_ENV)

        if parentId is None:
            logger.info('''There is no parentId attribute in  device (deviceid=\'%s\') in environment data.''',
                        deviceId)
            return None

        for deviceName in self._device_params.keys():
            if type(self._device_params[deviceName]) is DictType:
                if (parentId in self._device_params[deviceName].values()):
                    if self._DEVICE_ID_IN_ENV in self._device_params[deviceName].keys():
                        if self._device_params[deviceName][self._DEVICE_ID_IN_ENV] == parentId:
                            return deviceName
        else:
            return None

    # def get_devices_by_type(self, type):
    #     devicesList = self.config[self._DEVICES_IN_EVN]
    #     typeDeviceList = []
    #     for device in devicesList:
    #         if type == device[self._DEVICE_TYPE_IN_ENV]:
    #             typeDeviceList.append(device)
    #     return typeDeviceList

    # def get_children_devices(self, parentId):
    #     linkList = self.config[self._LINKS_IN_EVN]
    #     childrenIdList = []
    #     for link in linkList:
    #         if self._CREATE_LINK_IN_EVN == link[self._DEVICE_TYPE_IN_ENV]:
    #             if parentId == link[self._LINK_NODES_IN_EVN][0][self._LINK_DEVICE_IN_EVN]:
    #                 childrenIdList.append(link[self._LINK_NODES_IN_EVN][1][self._LINK_DEVICE_IN_EVN])
    #     linksDevices = []
    #     for id in childrenIdList:
    #         for index in range(len(self.config['devices'])):
    #             if self.config['devices'][index]['id'] == id:
    #                 linksDevices.append(self.config['devices'][index])
    #     return linksDevices

    # def get_hop_devices(self):
    #     hopDeviceList = []
    #     deviceList = self.config[self._DEVICES_IN_EVN]
    #     for device in deviceList:
    #         if not self._is_have_parent(device):
    #             hopDeviceList.append(device)
    #     return hopDeviceList

    # def _is_have_parent(self, device):
    #     linkList = self.config[self._LINKS_IN_EVN]
    #     for link in linkList:
    #         if self._CREATE_LINK_IN_EVN == link[self._DEVICE_TYPE_IN_ENV]:
    #             if device[self._DEVICE_ID_IN_ENV] == link[self._LINK_NODES_IN_EVN][1][self._LINK_DEVICE_IN_EVN]:
    #                 return True
    #     return False

    # def _get_root_device(self):
    #     rootDeviceList = []
    #     deviceList = self.config[self._DEVICES_IN_EVN]
    #     for device in deviceList:
    #         if not self._is_have_parent(device):
    #             rootDeviceList.append(device)
    #     return rootDeviceList

    def get_root_device_for_create(self):
        rootDeviceList = []
        deviceList = self._get_root_device()
        for device in deviceList:
            deviceType = device[self._DEVICE_TYPE_IN_ENV].split('/')[0]
            if deviceType in self.DEVICE_DICT.keys():
                # device[self._DEVICE_TYPE_IN_ENV] = deviceType
                rootDeviceList.append(device)
        return rootDeviceList

    def get_first_device_from_link(self, link_name):
        for k in self._device_params:
            if self._LINK_NAME_IN_EVN in self._device_params[k] and \
               self._device_params[k][self._LINK_NAME_IN_EVN]==link_name:
                link_name = k
        link = self._device_params.get(link_name)
        if self._check_nodes_of_link_by_link(link):
            return self._get_first_device_from_nodes_of_link(self._get_link_nodes(link))
        return None

    def get_link_by_first_and_second_device(self, first_device, second_device):
        try:
            for link_name in self._device_params.keys():
                if self._check_nodes_of_link_by_link(self._device_params[link_name]):
                    nodes = self._get_link_nodes(self._device_params[link_name])
                    if self._get_first_device_from_nodes_of_link(
                            nodes) == first_device and self._get_second_device_from_nodes_of_link(
                            nodes) == second_device:
                        return self._device_params[link_name]['name'] # link_name
            return None
        except Exception:
            return None

    def _check_nodes_of_link_by_link(self, link):
        if type(link) is DictType and self._is_link_node(link):
            return self._check_nodes_of_link_by_nodes(self._get_link_nodes(link))
        return False

    def _check_nodes_of_link_by_nodes(self, nodes):
        if nodes is not None and type(nodes) is list and len(nodes) == 2:
            return True
        return False

    def _get_first_device_from_nodes_of_link(self, nodes):
        return nodes[0][self._LINK_DEVICE_IN_EVN]

    def _get_second_device_from_nodes_of_link(self, nodes):
        return nodes[1][self._LINK_DEVICE_IN_EVN]

    def _get_link_nodes(self, link):
        return link[self._LINK_NODES_IN_EVN]

    def get_devices_from_link(self, link_name):
        return self._device_params[link_name]['nodes']

    def get_obj_dependent_defs(self):
        from testlib.infrastructure.resource.resource.service.DependenceManager import UniqueModelType

        nodes = {};
        lnks = []
        for dvc_alias in self._device_params:
            n = self._device_params[dvc_alias]
            if not self._is_link_node(n):
                t = n['type']
                if 'loadType' in n.keys(): t = UniqueModelType(t, n['loadType']).get_type()
                # nodes-> {alias: unique_type, object_def, dependence_alias, dependence_unique_type)]
                nodes[dvc_alias] = [t]  # [[t, None, None, None]]
            else:
                lnks.append(n)

        def duplicated_prop(owner, obj, prop):
            for o in owner[1:]:
                if o[0] == prop:
                    logger.warn('!! Duplicated property %s\'s%s, ignored!!' % (obj, prop))
                    return True
            return False

        for k in lnks:
            # find property of dependence 
            obj, prop = None, k['nodes'][0]['device']
            for n in k['nodes']:
                if prop:
                    obj = prop;
                    prop = None
                    continue
                if obj is None:
                    continue
                owner = nodes[obj]
                prop = n['device']
                if owner is None:
                    continue
                # evaluate alias and type
                if duplicated_prop(owner, obj, prop):
                    continue
                owner.append([prop, nodes[prop][0]])
        return nodes

    def inject_domain_objects(self):
        logger.debug('Begin to inject domain objects')
        do = DomainObjectInjecter(self)
        self.relies = do.repose_objs()
        logger.debug('Injected domain objects success!')

    def release_domain_objects(self):
        if not hasattr(self, 'relies'):
            logger.warn('Injected domain objects is empty!')
            return
        logger.debug('Ready to release injected domain objects!')
        stacked_repos = []
        while self.relies:
            o3 = self.relies.pop()
            if o3[1] not in stacked_repos:
                stacked_repos.append(o3[1])
            if o3[-1]:
                logger.debug('- %s is closing...' % o3[0])
                o = o3[1].find(o3[0])
                getattr(o, o3[-1])()
            if o3[1]:
                o3[1].delete(o3[0])
        for repo in stacked_repos:
            repo.stack_pop()

    # Create domain objects automatically
    def create_domain_objects(self, deviceDefPath):
        from testlib.infrastructure.resource.resource.adapter import yaml

        devices = yaml.load(file(deviceDefPath, 'rb').read())['DEVICE_DICT']
        nodes = [];
        omits = []
        for dvc in self._device_params:
            n = self._device_params[dvc]
            if not self._is_link_node(n):
                k = n['type']
                if 'loadType' in n.keys(): k = k + '-' + n['loadType']
                nodes.append((dvc, k))
            elif n['linkType'] == 'use':
                omits.append(n['nodes'][1]['device'])
        for node in nodes:
            if node[0] not in omits:
                if node[1] in devices:  # self.DEVICE_DICT
                    module = devices[node[1]]['module']
                    clsName = devices[node[1]]['class']
                    creater = devices[node[1]]['creater']
                    deleter = devices[node[1]]['deleter'] if 'deleter' in devices[node[1]] else None
                    __import__(module)
                    getattr(getattr(sys.modules[module], clsName)(), creater)(node[0])
                    # Add created device to list to destroy after execution of cases
                    dvc_module_cls_del = [node[0], module, clsName, deleter]
                    self.CREATED_DEVICES.append(dvc_module_cls_del)

    # Delete domain objects automatically after a case has been executed
    def delete_domain_objects(self):
        if len(self.CREATED_DEVICES) < 1:
            return
        for dvc in self.CREATED_DEVICES:
            print 'delete'
            if None is dvc[-1]:
                continue
            __import__(dvc[1])
            env = getattr(sys.modules[dvc[1]], dvc[2])()
            if hasattr(env, dvc[-1]):
                getattr(env, dvc[-1])(dvc[0])
        self.CREATED_DEVICES = []

    def set_case_variables(self, variables):
        self.variables = variables

    def get_case_variable(self, dollar_wrapped_name):
        return self.variables.get(dollar_wrapped_name)

    def _get_links_nodes(self):
        links_nodes = []
        for key, value in self._device_params.items():
            if not self._is_link_node(value):
                continue
            links_nodes.append(value)
        return links_nodes

    def _get_device(self, deviceid):
        return self._device_params[deviceid]

    def _get_second_device_names_by_first_device(self, first_device):
        second_device_names = []
        for link_node in self._get_links_nodes():
            if first_device != self._get_first_device_from_nodes_of_link(link_node[self._LINK_NODES_IN_EVN]):
                continue
            second_device_names.append(self._get_second_device_from_nodes_of_link(link_node[self._LINK_NODES_IN_EVN]))
        return second_device_names

    def get_second_device_by_first_device(self, first_device):
        second_device_names = self._get_second_device_names_by_first_device(first_device)
        if not second_device_names:
            return None
        return self._get_device(second_device_names[0])
