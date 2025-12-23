#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      Fox_Hou
#
# Created:     19/08/2015
# Copyright:   (c) Fox_Hou 2015
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import http
import re
from http import client
from http import HTTPStatus


class Sfisws:
    def __init__(self, host=None, url=None):
        self.__programid = "TSP_ATSHH"
        self.__pwd = "pap_ahga"
        self.__header = {"Content-type": "text/xml", "charset": "UTF-8", "Accept": "text/plain", "action":"http://www.pegatroncorp.com/SFISWebService/GetDatabaseInformation"}
        self.__host = host
        self.__url = url
        self.__raw_result = ""

    def setHost(self, host):
        self.__host = host

    def setUrl(self, url):
        self.__url = url

    def __ws_call(self, function_body):
        body = function_body
        status = -1
        result = []
        httpClient = None

        try:
            httpClient = client.HTTPConnection(self.__host, client.HTTP_PORT, timeout=5)
            httpClient.request ("POST", self.__url, body, self.__header)
            response = httpClient.getresponse()
            status = response.status

            if (status == HTTPStatus.OK):
                reading = response.read().decode()
                reading = reading.replace('\n', ' ')

                searchObj = re.search(r'<\w+Result>(.*)</\w+Result>', reading, re.M|re.I)
                if searchObj:
                    result = searchObj.group(1).split('\x7f')
                    self.__raw_result = searchObj.group(1)
                else:
                    result = ['-1', reading]
            else:
                result = ['-2', 'response status:{} reason:{}'.format(status, response.reason)]

        except Exception as e:
            result = ['-3', e]
        finally:
            if httpClient:
                httpClient.close()
        return status, result


    def GetRawResult(self):
        return self.__raw_result

    def GetDatabaseInfo(self):
        body = "<soap12:Envelope xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" xmlns:xsd=\"http://www.w3.org/2001/XMLSchema\" xmlns:soap12=\"http://www.w3.org/2003/05/soap-envelope\">\
                    <soap12:Body>\
                        <GetDatabaseInformation xmlns=\"http://www.pegatroncorp.com/SFISWebService/\" />\
                    </soap12:Body>\
                </soap12:Envelope>"

        status, result = self.__ws_call(body)
        return status, result


    def Loginout(self, op, pwd, device, tsp, stat):
        body = "<soap12:Envelope xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" xmlns:xsd=\"http://www.w3.org/2001/XMLSchema\" xmlns:soap12=\"http://www.w3.org/2003/05/soap-envelope\">\
                    <soap12:Body>\
                        <WTSP_LOGINOUT xmlns=\"http://www.pegatroncorp.com/SFISWebService/\">\
                            <programId>{0}</programId>\
                            <programPassword>{1}</programPassword>\
                            <op>{2}</op>\
                            <password>{3}</password>\
                            <device>{4}</device>\
                            <TSP>{5}</TSP>\
                            <status>{6}</status>\
                        </WTSP_LOGINOUT>\
                    </soap12:Body>\
                </soap12:Envelope>".format(self.__programid, self.__pwd, op, pwd, device, tsp, stat)

        status, result = self.__ws_call(body)
        return status, result


    def ChkRoute(self, isn, device, chk_flag, chk_data, type):
        body = "<soap12:Envelope xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" xmlns:xsd=\"http://www.w3.org/2001/XMLSchema\" xmlns:soap12=\"http://www.w3.org/2003/05/soap-envelope\">\
                    <soap12:Body>\
                        <WTSP_CHKROUTE xmlns=\"http://www.pegatroncorp.com/SFISWebService/\">\
                            <programId>{0}</programId>\
                            <programPassword>{1}</programPassword>\
                            <ISN>{2}</ISN>\
                            <device>{3}</device>\
                            <checkFlag>{4}</checkFlag>\
                            <checkData>{5}</checkData>\
                        <type>{6}</type>\
                        </WTSP_CHKROUTE>\
                    </soap12:Body>\
                </soap12:Envelope>".format(self.__programid, self.__pwd, isn, device, chk_flag, chk_data, type)

        status, result = self.__ws_call(body)
        return status, result


    def Repair(self, type, isn, dev, reason, duty, ngrp, tsp):
        body = "<soap12:Envelope xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" xmlns:xsd=\"http://www.w3.org/2001/XMLSchema\" xmlns:soap12=\"http://www.w3.org/2003/05/soap-envelope\">\
                    <soap12:Body>\
                        <WTSP_REPAIR xmlns=\"http://www.pegatroncorp.com/SFISWebService/\">\
                            <programId>{0}</programId>\
                            <programPassword>{1}</programPassword>\
                            <TYPE>{2}</TYPE>\
                            <ISN>{3}</ISN>\
                            <DEV>{4}</DEV>\
                            <REASON>{5}</REASON>\
                            <DUTY>{6}</DUTY>\
                            <NGRP>{7}</NGRP>\
                            <TSP>{8}</TSP>\
                        </WTSP_REPAIR>\
                    </soap12:Body>\
                </soap12:Envelope>".format(self.__programid, self.__pwd, type, isn, dev, reason, duty, ngrp, tsp)

        status, result = self.__ws_call(body)
        return status, result


    def Result(self, isn, error, device, tsp, data, status, cpk_flag):
        body = "<soap12:Envelope xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" xmlns:xsd=\"http://www.w3.org/2001/XMLSchema\" xmlns:soap12=\"http://www.w3.org/2003/05/soap-envelope\">\
                    <soap12:Body>\
                        <WTSP_RESULT xmlns=\"http://www.pegatroncorp.com/SFISWebService/\">\
                            <programId>{0}</programId>\
                            <programPassword>{1}</programPassword>\
                            <ISN>{2}</ISN>\
                            <error>{3}</error>\
                            <device>{4}</device>\
                            <TSP>{5}</TSP>\
                            <data>{6}</data>\
                            <status>{7}</status>\
                            <CPKFlag>{8}</CPKFlag>\
                        </WTSP_RESULT>\
                    </soap12:Body>\
                </soap12:Envelope>".format(self.__programid, self.__pwd, isn, error, device, tsp, data, status, cpk_flag)

        status, result = self.__ws_call(body)
        return status, result


    def GetVersion(self, isn, device, type, chk_data, chk_data2):
        body = "<soap12:Envelope xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" xmlns:xsd=\"http://www.w3.org/2001/XMLSchema\" xmlns:soap12=\"http://www.w3.org/2003/05/soap-envelope\">\
                    <soap12:Body>\
                        <WTSP_GETVERSION xmlns=\"http://www.pegatroncorp.com/SFISWebService/\">\
                            <programId>{0}</programId>\
                            <programPassword>{1}</programPassword>\
                            <ISN>{2}</ISN>\
                            <device>{3}</device>\
                            <type>{4}</type>\
                            <ChkData>{5}</ChkData>\
                            <ChkData2>{6}</ChkData2>\
                        </WTSP_GETVERSION>\
                    </soap12:Body>\
                </soap12:Envelope>".format(self.__programid, self.__pwd, isn, device, type, chk_data, chk_data2)

        status, result = self.__ws_call(body)
        return status, result

    def GetIMAC(self, isn, device, status, imacnum):
        body = "<soap12:Envelope xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" xmlns:xsd=\"http://www.w3.org/2001/XMLSchema\" xmlns:soap12=\"http://www.w3.org/2003/05/soap-envelope\">\
                    <soap12:Body>\
                        <WTSP_GETIMAC xmlns=\"http://www.pegatroncorp.com/SFISWebService/\">\
                            <programId>{0}</programId>\
                            <programPassword>{1}</programPassword>\
                            <device>{2}</ISN>\
                            <ISN>{3}</device>\
                            <status>{4}</type>\
                            <imacnum>{5}</ChkData>\
                        </WTSP_GETIMAC>\
                    </soap12:Body>\
                </soap12:Envelope>".format(self.__programid, self.__pwd, device, isn, status, imacnum)

        status, result = self.__ws_call(body)
        return status, result

    def GetI1394(self, isn, device, status, i1394num):
        body = "<soap12:Envelope xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" xmlns:xsd=\"http://www.w3.org/2001/XMLSchema\" xmlns:soap12=\"http://www.w3.org/2003/05/soap-envelope\">\
                    <soap12:Body>\
                        <WTSP_GETI1394 xmlns=\"http://www.pegatroncorp.com/SFISWebService/\">\
                            <programId>{0}</programId>\
                            <programPassword>{1}</programPassword>\
                            <device>{2}</ISN>\
                            <ISN>{3}</device>\
                            <status>{4}</type>\
                            <I1394NUM>{5}</ChkData>\
                        </WTSP_GETI1394>\
                    </soap12:Body>\
                </soap12:Envelope>".format(self.__programid, self.__pwd, device, isn, status, i1394num)

        status, result = self.__ws_call(body)
        return status, result

    def SsdInputData(self, device, data, type):
        body = "<soap12:Envelope xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" xmlns:xsd=\"http://www.w3.org/2001/XMLSchema\" xmlns:soap12=\"http://www.w3.org/2003/05/soap-envelope\">\
                    <soap12:Body>\
                        <WTSP_SSD_INPUTDATA xmlns=\"http://www.pegatroncorp.com/SFISWebService/\">\
                            <programId>{0}</programId>\
                            <programPassword>{1}</programPassword>\
                            <device>{2}</device>\
                            <data>{3}</data>\
                            <type>{4}</type>\
                        </WTSP_SSD_INPUTDATA>\
                    </soap12:Body>\
                </soap12:Envelope>".format(self.__programid, self.__pwd, device, data, type)

        status, result = self.__ws_call(body)
        return status, result
    def MO_input(self,device,MO):
        body = "<soap12:Envelope xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" xmlns:xsd=\"http://www.w3.org/2001/XMLSchema\" xmlns:soap12=\"http://www.w3.org/2003/05/soap-envelope\">\
                    <soap12:Body>\
                        <WTSP_DEVIF_MO xmlns=\"http://www.pegatroncorp.com/SFISWebService/\">\
                            <programId>{0}</programId>\
                            <programPassword>{1}</programPassword>\
                            <device>{2}</device>\
                            <MO>{3}</MO>\
                        </WTSP_DEVIF_MO>\
                    </soap12:Body>\
                </soap12:Envelope>".format(self.__programid, self.__pwd, device,MO)
        status, result = self.__ws_call(body)
        return status, result

def main():

    sfis = Sfisws('10.176.33.13', '/SFISWebservice/SFISTSPWebservice.asmx')
    isn='EF-AOILOC-0'+'\u007f'+'254236620005955'
    status, result = sfis.SsdInputData('101806',isn,'0')

    if (status == HTTPStatus.OK):
        if len(result) == 2:

            print("Result : ", result[0])
            print("Database Information : ", result[1])
            print(result)
        else:
            print(result)
    else:
        print(status)
        print(result)

##    status, result = sfis.Loginout("S09224144", "1", "101806", "SPADE_SMOKE", 5)
##
##    if (status == http.OK):
##        print("Result : {0}".format(result[0]))
##        print("Message : {0}".format(result[1].decode("utf-8")))
##        print("Other : {0}".format(result[2].decode("utf-8")))
##
##    pass

if __name__ == '__main__':
    main()
