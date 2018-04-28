#!/usr/bin/env python

import os
import sys
import time
import requests
from lxml import etree as lt
import StringIO
import csv 

# define the global parameters
global csv_file
global totalNum
global soap_url

csv_file = 'data.csv'
totalNum = 10
soap_url = 'http://10.40.8.30/CDBProvisioningV6/CDBProvisioningV6'

def log_folder():
    # create the log folder to store the log file: *.log
    # log_folder: TER_0907_09h
    # return the log_folder name
    
    mon = time.localtime().tm_mon
    day = time.localtime().tm_mday
    hour = time.localtime().tm_hour
    
    if mon < 10:
        mon = '0' + str(mon)

    if day < 10:
        day = '0' + str(day)
    
    if hour < 10:
        hour = '0'+ str(hour)
	
    pfx = "TER_"
    
    # folder_name: TER_0907_h09_REG_01
    log_folder = pfx + str(mon) + str(day) + '_' + str(hour) + 'h'

    if not os.path.exists("./TER_Auto/" + log_folder):
        os.makedirs("./TER_Auto/" + log_folder)
             
    return log_folder

   
class Logger(object):
    #Lumberjack class - duplicates sys.stdout to a log file
    #source: https://stackoverflow.com/q/616645
    #source: https://stackoverflow.com/questions/616645/how-do-i-duplicate-sys-stdout-to-a-log-file-in-python/2216517#2216517
    # Usage:
    # Log=Logger('my.log')
    # print('works all day')
    # Log.close()
    
    def __init__(self, filename="Red.Wood", mode="a", buff=0):
        self.stdout = sys.stdout
        self.file = open(filename, mode, buff)
        sys.stdout = self

    def __del__(self):
        self.close()

    def __enter__(self):
        pass

    def __exit__(self, *args):
        self.close()

    def write(self, message):
        self.stdout.write(message)
        self.file.write(message)

    def flush(self):
        self.stdout.flush()
        self.file.flush()
        os.fsync(self.file.fileno())

    def close(self):
        if self.stdout != None:
            sys.stdout = self.stdout
            self.stdout = None

        if self.file != None:
            self.file.close()
            self.file = None

def setText_xml(ltree, path, text):
    # define a function set the ELement's text for the matached item by using lxml.elementtree
    # path = ltree.find('//byMobileIMSI')

    if text != '':
        if ltree.find(path) != None:
            elem = ltree.find(path)    
            elem.text = text

def query_Facility(url, imsi):
    # read the facility from CDB w IMSI as the key
    
    headers = {"Content-Type": "text/xml", "charset": "UTF-8"}
    
    data = """
    <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:v6="http://unico.com/clp/dal/service/provision/v6">
       <soapenv:Header><wsse:Security xmlns:wsse="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd" xmlns:wsu="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd" soapenv:mustUnderstand="1"><wsse:UsernameToken wsu:Id="UsernameToken-7CFCA8E862984F4F5515014838890569"><wsse:Username>racemed</wsse:Username><wsse:Password Type="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-username-token-profile-1.0#PasswordText">nopassword</wsse:Password><wsse:Nonce EncodingType="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-soap-message-security-1.0#Base64Binary">80ltNpwfjQE/I8IlE/C8vA==</wsse:Nonce><wsu:Created>2017-07-31T06:51:29.056Z</wsu:Created></wsse:UsernameToken></wsse:Security></soapenv:Header>
       <soapenv:Body>
          <v6:ListEntitiesRequest>
             <returnEntityType>SERVICE_FACILITY</returnEntityType>
             <serviceCriteria>
                <byKey>
                   <byMobileIMSI>{}</byMobileIMSI>
                </byKey>
             </serviceCriteria>
          </v6:ListEntitiesRequest>
       </soapenv:Body>
    </soapenv:Envelope>
    """.format(imsi)
    
    #ltree = lt.fromstring(data)
    #setText_xml(ltree, './/serviceCriteria/byKey/byMobileIMSI', imsi)
        
    # set the updated value back to string       
    #data2 = lt.tostring(ltree)
    
    #
    print "\n# Request: \n%s" %(data)
    
    # send out the request
    res = requests.post(url, data=data, headers=headers)
    print "\n# cmd code: %s" %(str(res.status_code))
    print "\n# cmd response: \n%s \n" %(res.text)
    
    
    ltree = lt.fromstring(res.text)
    data3 = lt.tostring(ltree, pretty_print=True)
    print "\n# cmd response: \n%s \n" %(data3)
    
    ltree_result = lt.fromstring(res.text)
    xpath = './/facility/byName/text()'
    facilities = ltree_result.xpath(xpath)
    #print facilities
    if 'ONENUM_OK' in facilities:
        print 'IMSI:{}, facility:{}'.format(imsi, 'ONENUM_OK')
    else:
        print 'IMSI:{}, facility:{}'.format(imsi, 'NOT Found')
    
def query_IMSI(url, imsi):
    # query the subscriber paymenttype data from CDB w IMSI as the key
    
    headers = {"Content-Type": "text/xml", "charset": "UTF-8"}
       
    data = """
    <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:v6="http://unico.com/clp/dal/service/provision/v6">
        <soapenv:Header><wsse:Security xmlns:wsse="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd" xmlns:wsu="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd" soapenv:mustUnderstand="1"><wsse:UsernameToken wsu:Id="UsernameToken-7CFCA8E862984F4F5515014838890569"><wsse:Username>racemed</wsse:Username><wsse:Password Type="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-username-token-profile-1.0#PasswordText">nopassword</wsse:Password><wsse:Nonce EncodingType="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-soap-message-security-1.0#Base64Binary">80ltNpwfjQE/I8IlE/C8vA==</wsse:Nonce><wsu:Created>2017-07-31T06:51:29.056Z</wsu:Created></wsse:UsernameToken></wsse:Security></soapenv:Header>
        <soapenv:Body>
          <v6:GetEntitiesRequest>
             <serviceCriteria>
                <!--Optional:-->
                <byMobileIMSI>{}</byMobileIMSI>
             </serviceCriteria>
          </v6:GetEntitiesRequest>
        </soapenv:Body>
    </soapenv:Envelope>
    """.format(imsi)
    
    
    #ltree = lt.fromstring(data)
    #setText_xml(ltree, './/serviceCriteria/byMobileIMSI', imsi)
        
    # set the updated value back to string       
    #data2 = lt.tostring(ltree)
    
    #
    print "\n# Request: \n%s" %(data)
    
    # send out the request
    res = requests.post(url, data=data, headers=headers)
    print "\n# cmd code: %s" %(str(res.status_code))
    print "\n# cmd response: \n%s \n" %(res.text)
    
    
    ltree = lt.fromstring(res.text)
    data3 = lt.tostring(ltree, pretty_print=True)
    print "\n# cmd response: \n%s \n" %(data3)
    
    
    ltree_result = lt.fromstring(res.text)
    xpath = './/service/paymentType/text()'
    elems = ltree_result.xpath(xpath) 
    print 'IMSI:{}, paymentType:{}'.format(imsi, elems[0])

def createSub(url, imsi, uid, msisdn_zs):
    # create new record in CDB for subscriber w ONENUM_OK and postpaid payment type 
    
    headers = {"Content-Type": "text/xml", "charset": "UTF-8"}
    
    data = """
    <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:v6="http://unico.com/clp/dal/service/provision/v6">
      <soapenv:Header>
      <wsse:Security soapenv:mustUnderstand="1" xmlns:wsse="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd" xmlns:wsu="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd">
         <wsse:UsernameToken wsu:Id="UsernameToken-5346FADD1C5CBE6FA3150061775015113">
            <wsse:Username>racemed</wsse:Username>
            <wsse:Password Type="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-username-token-profile-1.0#PasswordText">nopassword</wsse:Password>
            <wsse:Nonce EncodingType="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-soap-message-security-1.0#Base64Binary">ncJ4G3sEEMobpy48E6NXzg==</wsse:Nonce>
            <wsu:Created>2017-07-21T06:15:50.151Z</wsu:Created>
         </wsse:UsernameToken>
      </wsse:Security>
   </soapenv:Header>
   <soapenv:Body>
      <v6:ProvisionEntitiesRequest>
         <provisionOperation>
            <operationId>CreateOrEdit</operationId>
            <service>
               <key>
                  <byServiceNumber>{}</byServiceNumber>
               </key>
               <entity>
                  <serviceNumber>{}</serviceNumber>
                  <mobileIMSI>{}</mobileIMSI>
                  <mobileUID>{}</mobileUID>
                  <createDate>2017-07-24Z</createDate>
                  <paymentType>Postpaid</paymentType>
                  <serviceCarrierCode>11</serviceCarrierCode>
                  <serviceProviderId>0002</serviceProviderId>
                  <serviceTechnology>THREE_G</serviceTechnology>
                  <portedFlag>false</portedFlag>
                  <appTermSmsFlag>false</appTermSmsFlag>
                  <serviceTypeNumber>2</serviceTypeNumber>
                  <status>AC</status>
               </entity>
            </service>
         </provisionOperation>
         <provisionOperation>
            <operationId>CreateOrEdit</operationId>
            <serviceFacility>
               <key>
                  <byServiceAndFacility>
                     <service>
                        <byServiceNumber>{}</byServiceNumber>
                     </service>
                     <facility>
                        <byName>ONENUM_OK</byName>
                     </facility>
                  </byServiceAndFacility>
               </key>
               <entity>
                  <facility>
                     <byName>ONENUM_OK</byName>
                  </facility>
                  <service>
                     <byServiceNumber>{}</byServiceNumber>
                  </service>
                  <status/>
                  <attributes/>
               </entity>
            </serviceFacility>
         </provisionOperation>
      </v6:ProvisionEntitiesRequest>
   </soapenv:Body>
</soapenv:Envelope>    
    """.format(msisdn_zs, msisdn_zs, imsi, uid, msisdn_zs, msisdn_zs)

    #ltree = lt.fromstring(data)

    # set msisdn_zs
    #setText_xml(ltree, './/provisionOperation/service/key/byServiceNumber', msisdn_zs)
    #setText_xml(ltree, './/provisionOperation/service/entity/serviceNumber', msisdn_zs)
    #setText_xml(ltree, './/provisionOperation/serviceFacility/key/byServiceAndFacility/service/byServiceNumber', msisdn_zs)
    #setText_xml(ltree, './/provisionOperation/serviceFacility/entity/service/byServiceNumber', msisdn_zs)
    
    # set imsi
    #setText_xml(ltree, './/provisionOperation/service/entity/mobileIMSI', imsi)
    
    # set UID
    #setText_xml(ltree, './/provisionOperation/service/entity/mobileUID', uid)
        
    # set the updated value back to string       
    #data2 = lt.tostring(ltree)
    
    #
    print "\n# Request: \n%s" %(data)
    
    # send out the request
    res = requests.post(url, data=data, headers=headers)
    print "\n# cmd code: %s" %(str(res.status_code))
    print "\n# cmd response: \n%s \n" %(res.text)
    
    
    ltree = lt.fromstring(res.text)
    data3 = lt.tostring(ltree, pretty_print=True)
    print "\n# cmd response: \n%s \n" %(data3)
    
    
    ltree_result = lt.fromstring(res.text)
    xpath = './/resultCode/text()'
    elems = ltree_result.xpath(xpath) 
    print 'createSub for IMSI:{}, resultCode:{}'.format(imsi, elems[0])
    

    
def main():

    home_path =  os.path.dirname(os.path.realpath(csv_file)) 
      
    path = log_folder()  # mkdir TER_0907_9h
    os.chdir("./TER_Auto/" + path)  # cd ./TER_Auto/TER_0907_9h  
    
    logfile = path + '.log'    # touch TER_0907.log
    Log = Logger(logfile)
    
    ifile = open('../../' + csv_file, 'rb')
    reader = csv.reader(ifile)
    
    # define the end time 
    time1 = time.time()
    print '\n# ' + time.ctime()
    
    rowNum = 0
    for row in reader:
        imsi = str(row[2])
        uid = str(row[0]) 
        msisdn_zs = str(row[1])
        
        if rowNum < totalNum:
            print '%7d' %(rowNum+1),
            query_Facility(soap_url, imsi)
            #raw_input('press Enter to continue...')
            #query_IMSI(soap_url, imsi)
            #raw_input('press Enter to continue...')
            #createSub(soap_url, imsi, uid, msisdn_zs)
            raw_input('press Enter to continue...')
            #print
        else:    
            break
        rowNum +=1
    
    ifile.close()
    
    # define the end time 
    time2 = time.time()
        
    duration = time2 - time1
    print '\n# ' + time.ctime()
    print '# The duration for this test is: ' + str(duration) + ' seconds'
    
    # return to the home directory after the test scenario
    # cd ../..
    os.chdir(home_path)
    
    #f_log.close() # close the log file
    Log.close() # close the log file
    
if __name__ == "__main__":
    main()    
    