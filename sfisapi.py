#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      fox
#
# Created:     31/08/2018
# Copyright:   (c) fox 2018
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import sys
import logging
import threading
from urllib.parse import urlparse

import sfisws
#import setting


class SFISApi():
    """ provide high level SFIS function

    all function return list data
    example:['1', 'PSZASHH0(蘇州PSZASHH0資料庫)']
    list[0] is '1' if successed
    list[0] is '0' if failed
    """
    USER_LIGIN = '1'
    USER_LOGOUT = '2'
    USER_STATUS = '5'
    __sfis = None
    __url = None
    __dev_id = None
    __station_id = None
    __enable_repair = True
    __route_rule = 'N/A'

    def __init__(self, url, devid, stationid):
        self.__url = url
        self.__dev_id = devid
        self.__station_id = stationid

    def sfisobj(self):
        if self.__sfis == None:
            o = urlparse(self.__url)
            self.__sfis = sfisws.Sfisws(o.netloc, o.path)
        return self.__sfis

    def getdbinfo(self):
        status, result = self.sfisobj().GetDatabaseInfo()
        return result

    def login(self, op_id):
        """ login SFIS

        op_id - the user id of authorized
        return example ['1', 'Welcome using Pegatron SFIS:LA0803398(侯世璿)', '侯世璿', 'OP', '']
        """
        self.__op_id = op_id
        return self.relogin()

    def relogin(self):
        status, result =  self.sfisobj().Loginout(self.__op_id, '1', self.__dev_id, self.__station_id, self.USER_LIGIN)
        logging.info('login result:{}'.format(result))
        if result[0] != '1':
            status, result =  self.sfisobj().Loginout(self.__op_id, '1', self.__dev_id, self.__station_id, self.USER_LOGOUT)
            status, result =  self.sfisobj().Loginout(self.__op_id, '1', self.__dev_id, self.__station_id, self.USER_LIGIN)
            if result[0] != '1':
                logging.info('login result:{}'.format(result))
        return result

    def logout(self):
        """ logout SFIS

        return example ['1', 'Thank you for using Pegatron SFIS! (LO)', '侯世璿', 'LOGOUT SFIS', '']
        """
        status, result =  self.sfisobj().Loginout(self.__op_id, '1', self.__dev_id, self.__station_id, self.USER_LOGOUT)
        logging.info('logout result:{}'.format(result))
        return result

    def __chk_route(self, isn):
        status, result =  self.sfisobj().ChkRoute(isn, self.__dev_id, '', '', '1')
        logging.info('chk_route result:{}'.format(result))
        return result

    def __chk_route_rule(self, isn, count):
        ret = 'ok'
        if self.__route_rule == 'N/A':
            return ret
        result = self.get_version(isn, 'MO_D', 'DEVICE', '')
        if result[0]=='1' and result[1]>2:
            devid = result[2]
        if result[0] == '1':
            if self.__route_rule == 'AAB':
                if self.__dev_id == devid:
                    if count%2 == 1:
                        ret = 'not_ok'
                else:
                    if count%2 == 0:
                        ret = 'not_ok'
                if ret == 'not_ok':
                    logging.info('__chk_route_rule(), The route rule is AAB. And the last failure on device id {}'.format(devid))
            elif self.__route_rule == 'ABA':
                if self.__dev_id == devid:
                    if count%2 == 0:
                        ret = 'not_ok'
                else:
                    if count%2 == 1:
                        ret = 'not_ok'
                if ret == 'not_ok':
                    logging.info('__chk_route_rule(), The route rule is ABA. And the last failure on device id {}'.format(devid))
            else:
                ret = 'not_ok'
                logging.info('__chk_route_rule(), SFIS_CHECK_RULE is either [AAB] or [ABA]. Disable the rule if [N/A].')
        else:
            logging.info('__chk_route_rule(), failed to get_version()')
            ret = 'not_ok'
        return ret

    def chk_route(self, isn, repaircount=2):
        result = self.__chk_route(isn)
        if result[0] != '1':
            if self.__enable_repair==True and 'REPAIR OF' in result[1]:
                p = result[1].find('[LF#:')
                q = result[1].find(']', p)
                count = result[1][p+5:q]
                count = 0 if len(count)==0 else int(count)
                if count>0 and count>=repaircount:
                    logging.info('chk_route(), OVER REPAIR COUNT:{}'.format(count))
                    return result
                if self.__chk_route_rule(isn, count) != 'ok':
                    return result
                result = self.repair(isn)
                if result[0] != '1':
                    return result
                result = self.__chk_route(isn)
                if result[0] != '1':
                    return result
            else:
                logging.info('chk_route(), check route fail and no repair.')
        return result

    def repair(self, isn):
        status, result =  self.sfisobj().Repair('1', isn, self.__dev_id, 'ZR', '7C0', 'AUTO2A', self.__station_id)
        logging.info('repair result:{}'.format(result))
        return result

    def get_version(self, isn, ptype, chkdata1, chkdata2, device_id='default'):
        if device_id == 'default':
            device_id = self.__dev_id
        status, result = self.sfisobj().GetVersion(isn, device_id, ptype, chkdata1, chkdata2)
        logging.info('get_version result:{}'.format(result))
        return result
# def GetVersion(self, isn, device, type, chk_data, chk_data2):
    def mo_iput(self ,MO, device_id='default'):
        if device_id == 'default':
            device_id = self.__dev_id
        status, result = self.sfisobj().MO_input(device_id, MO)
        logging.info('mo_iput result:{}'.format(result))
        return result

    def result(self, isn, error, data):
        status, result = self.sfisobj().Result(isn, error, self.__dev_id, self.__station_id, data, '1', '')
        logging.info('test_result result:{}'.format(result))
        return result
    def ssdinputdata(self, data):
        status, result = self.sfisobj().SsdInputData(self.__dev_id, data, '')
        logging.info('test_result result:{}'.format(result))
        return result

def main():
    sfis = SFISApi(setting.WEB_URL, setting.DEVICE_ID, setting.STATION_NAME)
    result = sfis.getdbinfo()
    print(result)
    #result = sfis.login('LA0803398')
    #result = sfis.logout()
    result = sfis.get_version('GF71e20005169389', 'ITEM_ICUST', 'NOCUSTNO,REVERSION', '')
    print(result)
    pass

if __name__ == '__main__':
    main()
