
import asyncio
import random
import requests
import json
import logging
import time
import os

logging.basicConfig(filename='app.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('app.log') 


async def authenticate(serverIP, userName,password):
    start=time.perf_counter()
    #logging.warning('Authentication Started:')
    
    url = "http://" + serverIP +"/v1/authentication"
    #payload = "{\n\"username\" : \"pted_iqb2\",\n\"password\" : \"password\"\n}"
    payload = "{\n\"username\" : \""+userName+"\",\n\"password\" : \""+password+"\"\n}"
    #payload = {"username": userName,"password" : password}
    print(payload)
    print(url)
    response = requests.post(url, data = payload)
    json = response.json()
    print(json)
    logger.warning('Authentication time difference:'+str(time.perf_counter() - start))
    #print(json["token"])
    authResponse={"status_code":response.status_code,"authtoken":json["token"],"serverIP":serverIP}
    #return json["token"]
    return authResponse


    # Upload Files:  NOTE: You must specify the MIME type for each file.    

async def uploadFiles(authResponse,liID,directoryPath):
     start=time.perf_counter()
     for dirpath,dirs, files in os.walk(directoryPath):
           print(dirpath)
           randstr=str(time.time())
           randstr=randstr.replace(".","_")
           filenamelist=[randstr+file for file in files]
           newlist=[]
           for file in files:
               concatstr=('files', (randstr+file, open(dirpath+'\\'+file,'rb'), 'application/pdf'))
               newlist.append( concatstr)
     authtoken = authResponse['authtoken']
     uploadurl = "http://" + authResponse['serverIP'] + "/IQBot/gateway/organizations/1/projects/" + liID + "/files/upload/1"
     data = {}
     headers = {'x-authorization': authtoken}
     fileName='File_'+str(time.time())+".pdf"
     #files = [('files', (fileName, open('E:\\Projects\\Python\\PDFtoIMage\\PDFImages\\0011_2020-08-27_154408.pdf','rb'), 'application/pdf'))]
     files = []
     response = requests.post(uploadurl, data=data, headers=headers, files=newlist)
     #print (response)
     print (response.status_code);
     uploadResponse={"status_code":response.status_code,"liID":liID,"serverIP":authResponse['serverIP'],"authtoken":authtoken,"fileName":fileName,"filenamelist":filenamelist}
     logger.warning('Upload files time difference:'+str(time.perf_counter() - start))
     return uploadResponse



# Get list of files processed for a given learning instance 
async def getListofFilesSuccessfullyProcessed(uploadResponse):
    start=time.perf_counter()
    #print("getListofFilesSuccessfullyProcessed")
    #print(uploadResponse)
    token = uploadResponse['authtoken']
    successurl = "http://" + uploadResponse['serverIP'] + "/IQBot/gateway/learning-instances/" + uploadResponse['liID']+ "/files/list?docType=SUCCESS"
    data = {}
    data_json = json.dumps(data)
    #await asyncio.sleep(15)
    #time.sleep(90)
    filenamelist=uploadResponse['filenamelist']
    headers = {'Content-Type':'application/json',"X-Authorization":token}
    while len(filenamelist)>0:
           print('length of list'+str(len(filenamelist)))
           response = requests.get(successurl, data=data_json, headers=headers)
           output = response.json()
           for filename in filenamelist:
               for outputFileName in output:
                   if filename in outputFileName:
                       logger.warning('Found------'+filename+"-----------"+str(time.perf_counter() - start))
                       filenamelist.remove(filename)
    
    return output   



SERVER_IP="*******.ap-south-1.compute.amazonaws.com"
USER_NAME="*******"
PASSWORD="password1"
LI_ID="4ebd6e56-ee4a-4ba8-8349-1814cfacde3b"
FILE_DIRECTORY="E:\\Projects\\Python\\PDFtoIMage\\PDFImages"

async def run():
    number = await getListofFilesSuccessfullyProcessed(await uploadFiles(await authenticate(SERVER_IP,USER_NAME,PASSWORD),LI_ID,FILE_DIRECTORY))
    print('success:', number)
    # except ValueError as exc:
    # try:
    #     number = await charlie(await bravo(await alpha(42)))
    # except ValueError as exc:
    #     print('error:', exc.args[0])
    # else:
    #     print('success:', number)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())
    loop.close()