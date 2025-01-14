from base64 import encode
import json
from logging import exception
from os import access, write
from re import I
from weakref import proxy
import requests
from urllib import parse
import time
from datetime import datetime
import psycopg2



headers = {
   
    }
access_url='https://api.superjob.ru/2.0/oauth2/refresh_token/?refresh_token='
res_access=requests.get(access_url,headers=headers)
data_access=res_access.json()
headers['Authorization']='Bearer '+str(data_access['access_token'])
url='https://api.superjob.ru/2.0/vacancies/'
params={
    'town': '4',
    'catalogues':'603',
    'page':'0',
    'count':'100',

}

url_t='https://api.superjob.ru/2.0/towns?all=true&id_country=1'
res_t = requests.get(url_t,headers=headers)
data_t = res_t.json()
url_catalogues='https://api.superjob.ru/2.0/catalogues/'
res_catalogues = requests.get(url_catalogues,headers=headers)
data_catalogues = res_catalogues.json()

con = psycopg2.connect(
    database="postgres", 
    user="postgres", 
    )
cur = con.cursor()

for town in data_t['objects']:
    params['town']=town['id']
    for cat in data_catalogues:
        for catolog in cat['positions']:
            params['page']=0
            k = 0
            while True:
                try:
                    params['catalogues']=catolog['key']
                    res = requests.get(url,headers=headers,params=params)
                    data = res.json()
                except Exception:
                    print(Exception)
                for count in range(100):
                    try:
                        ts = int(data['objects'][count]['date_published'])  
                        print(count, data['objects'][count]['profession'])
                        cur.execute('INSERT INTO UNITED_BASE (SITE, NAME, AREA, SALARY_FROM, SALARY_TO, SALARY_VAL, CREATED_AT, ARCHIVED, SHEDULE, ALTERNATE_URL) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ON CONFLICT DO NOTHING;', ('SJ', str.lower(data['objects'][count]['profession']), data['objects'][count]['town']['title'], data['objects'][count]['payment_from'], data['objects'][count]['payment_to'], str.upper(data['objects'][count]['currency']), str(datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')), data['objects'][0]['is_closed'], str.lower(data['objects'][count]['type_of_work']['title']), data['objects'][count]['link']))
                        con.commit()
                        k +=1
                    except:
                        print(exception)
                        print('error')
                        break
                    
                
                params['page']+=1
                print('>>>', data['total'], k, params['page'])
                if k >= data['total']:
                    break

