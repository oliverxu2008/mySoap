#!/usr/bin/env python

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
totalNum = 100
soap_url = 'http://10.40.8.30/CDBProvisioningV5/CDBProvisioningV5'


def setText_xml(ltree, path, text):
    # define a function set the ELement's text for the matached item by using lxml.elementtree
    # path = ltree.find('//byMobileIMSI')

    if text != '':
        if ltree.find(path) != None:
            elem = ltree.find(path)    
            elem.text = text

def soap_r(url, imsi):
    # read the facility from CDB w IMSI as the key
    
    headers = {"Content-Type": "text/xml", "charset": "UTF-8"}
    fname = 'query.xml'
    
    data = """
    <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:v5="http://unico.com/clp/dal/service/provision/v5">
       <soapenv:Header><wsse:Security xmlns:wsse="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd" xmlns:wsu="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd" soapenv:mustUnderstand="1"><wsse:UsernameToken wsu:Id="UsernameToken-7CFCA8E862984F4F5515014838890569"><wsse:Username>racemed</wsse:Username><wsse:Password Type="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-username-token-profile-1.0#PasswordText">nopassword</wsse:Password><wsse:Nonce EncodingType="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-soap-message-security-1.0#Base64Binary">80ltNpwfjQE/I8IlE/C8vA==</wsse:Nonce><wsu:Created>2017-07-31T06:51:29.056Z</wsu:Created></wsse:UsernameToken></wsse:Security></soapenv:Header>
       <soapenv:Body>
          <v5:ListEntitiesRequest>
             <returnEntityType>SERVICE_FACILITY</returnEntityType>
             <!--Optional:-->
             <serviceCriteria>
                <!--You have a CHOICE of the next 4 items at this level-->
                <byKey>
                   <byMobileIMSI>505720200001042</byMobileIMSI>
                </byKey>
             </serviceCriteria>
          </v5:ListEntitiesRequest>
       </soapenv:Body>
    </soapenv:Envelope>
    """
    
    
    ltree = lt.fromstring(data)
    setText_xml(ltree, './/byKey/byMobileIMSI', imsi)
        
    # set the updated value back to string       
    data2 = lt.tostring(ltree)
    
    # send out the request
    res = requests.post(url, data=data2, headers=headers)
    print "\n# cmd code: %s" %(str(res.status_code))
    #print "\n# cmd response: \n%s \n" %(res.text)
    
    ltree = lt.fromstring(res.text)
    data3 = lt.tostring(ltree, pretty_print=True)
    print "\n# cmd response: \n%s \n" %(data3)
    
    ltree_result = lt.fromstring(res.text)
    xpath = './/facility/byName'
    elem = ltree_result.find(xpath)
    if elem != None:  
        print 'IMSI:{}, facility:{}'.format(imsi, elem.text)
    else:
        print 'IMSI:{}, facility:{}'.format(imsi, 'NOT Found')
    
def main():
    
    ifile = open(csv_file, 'rb')
    reader = csv.reader(ifile)
    
    # define the end time 
    time1 = time.time()
    print '\n# ' + time.ctime()
    
    rowNum = 0
    for row in reader:
        imsi =  row[2]
        imsi = str(imsi)
        if rowNum < totalNum:
            soap_r(soap_url, imsi)
        else:    
            break
        rowNum +=1
    
    ifile.close()
    
    # define the end time 
    time2 = time.time()
        
    duration = time2 - time1
    print '\n# ' + time.ctime()
    print '# The duration for this test is: ' + str(duration) + ' seconds'
    
if __name__ == "__main__":
    main()    
    