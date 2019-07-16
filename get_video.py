# -*- coding: utf-8 -*- 
import requests
import re
import json
import time
import random
import logging
from Crypto.Cipher import AES

def log_setting(path='video.log'):
    logging.basicConfig(level='INFO',  
                    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',  
                    datefmt='%a, %d %b %Y %H:%M:%S',  
                    filename=path,  
                    filemode='a') 
def log_write(text):
    logging.info(text)

def get_video_page(video_id,headers,cookies):
    base_url='https://huke88.com/course/'
    video_url=base_url+video_id+'.html'
    res = requests.get(video_url,headers=headers,cookies=cookies)
    return res.text

def get_m3u8_url_and_video_name(video_id,headers,cookies):
    data = {
     'exposure': '0',
     'studySourceId': '0',
     'confirm': '0',
     'async': 'false',
     }
    m3u8_api_url='https://asyn.huke88.com/video/ajax-video-play'
    flag = True
    n = 0
    while flag:
        video_page=get_video_page(video_id,headers,cookies)
        re_csrf_token = re.compile(r'content=\"[0-9a-zA-Z=]{56}\"')
        csrf_token_list = re_csrf_token.findall(video_page)
        if len(csrf_token_list) == 0:
            n+=1
            if n >= 2:
                exit('cookie异常，请检测m3u8获取')
        else :
            flag = False
    csrf_token = csrf_token_list[0].split('"')[1]
    data['_csrf-frontend']=csrf_token
    data['id']=video_id
    re_video_titel = re.compile(r'<title>.*</title>')
    video_titel = re.split('<title>|<\/title>',re_video_titel.findall(video_page)[0])[1]
    res = requests.post(m3u8_api_url,headers=headers,data=data,cookies=cookies)
    m3u8_dict=json.loads(res.content)
    output_list=[]
    output_list.append(m3u8_dict["video_url"]) 
    output_list.append(video_titel) 
    if len(output_list) !=2 :
         exit('获取数据异常')
    return output_list

def get_m3u8_data(url):
    myheader = {'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8','User-Agent':'Chrome/75.0.3770.100'}
    res = requests.get(url,headers=myheader)
    return res.text

def get_video_list(m3u8_data):
    mydata = m3u8_data
    mydata_list = mydata.split()
    video_list = []
    for i in mydata_list:
        if re.match(r'^/',i):
            video_list.append(i)
    return video_list

def get_video_key():
    myheader = {'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8','User-Agent':'Chrome/75.0.3770.100'}
    url = 'https://asyn.huke88.com/video/decrypt'
    key = requests.get(url,headers=myheader).text
    return key

def main(video_id,headers,cookies):
    url,file_name = get_m3u8_url_and_video_name(video_id,headers,cookies)
    file_name = video_id+'_sys_'+file_name+'.ts'
    m3u8_data = get_m3u8_data(url)
    video_list = get_video_list(m3u8_data)
    key = get_video_key()
    myheader = {'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8','User-Agent':'Chrome/75.0.3770.100'}
    base_url = 'https://m3u8.huke88.com'
    cryptor = AES.new(key.encode('utf-8'), AES.MODE_CBC)
    for i in video_list:
       download_url = base_url+i
       print(download_url)
       data = requests.get(download_url,headers=myheader).content
       with open(file_name,'ab') as f:
           f.write(cryptor.decrypt(data))

if __name__ == '__main__':
   myheader = {'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
               'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36',
               'Referer': 'https://huke88.com',
               'Origin': 'https://huke88.com'
               }
   cookies = {'_identity-usernew': 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'}
   video_id = input('请输入需要下载的id：')
   main(video_id,myheader,cookies)
