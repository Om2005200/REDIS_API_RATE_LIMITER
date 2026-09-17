import requests as rq
import pandas as pd
import csv 
import json
from datetime import datetime,timedelta
import time
from sqlalchemy import text

from  fastapi import FastAPI,APIRouter,HTTPException,status,Depends,BackgroundTasks,Request
from typing import List,Annotated
from sqlmodel import select,desc
from fastapi.responses import JSONResponse
from sqlmodel import SQLModel
from models import API_TEST
from concurrent.futures import ProcessPoolExecutor
from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import create_async_engine,AsyncSession
#from schemas import USERDATABASE,ORDER_DATABASE
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm,OAuth2PasswordBearer,oauth2
import random
from sqlalchemy.orm import sessionmaker
import jwt
from redis.asyncio import Redis 
import redis
import websockets 
from redis.asyncio import Redis
import asyncio
import httpx




api_testings=FastAPI()

router=APIRouter()
@api_testings.on_event('startup')
async def startup():
    api_testings.state.redis=Redis(host='localhost',port=6379,decode_responses=True)


@api_testings.on_event('shutdown')
async def shutdown_event():
    await api_testings.state.redis.close()


class API_TESTINGS:
    """ THIS CODE IS DESIGNED TO TEST THE VARIOUS API CONDITIONS"""



    def __init__(self):
        pass




                    
    def ip_file(self):
        try:
            with open(r'C:\Users\dasho\ip_files','r') as x:
                data=json.load(x)
                if data is None:
                    data=[]
                return data


        except FileNotFoundError:
            with open(r'C:\Users\dasho\ip_files','w') as k:
                json.dump([],k,indent=4) 


            return []


    def storing_the_router_ip_data(self):
        try:
            with open(r'C:\Users\dasho\server_side_ip_files','r') as kl:
                data=json.load(kl)
                if data is None:
                    data=[]
                return data 
            
               

        except FileNotFoundError:
            with open(r'C:\Users\dasho\server_side_ip_files','w') as lk:
                json.dump([],lk,indent=4)
            return []



        

        
        



a=API_TESTINGS()



class HELPERS:



     

    async def getting_the_ip(self,request:Request):
        ip=request.client.host
        return ip


    async def sliding_window_counter(self,request:Request,client_data:json):
        server_data=client_data
        client_local_history=[]
        rq_limit=100
        tacoma=[]
        numbers = [
            1, 2, 3, 4, 5, 6, 7, 8, 9, 10,
            11, 12, 13, 14, 15, 16, 17, 18, 19, 20,
            21, 22, 23, 24, 25, 26, 27, 28, 29, 30,
            31, 32, 33, 34, 35, 36, 37, 38, 39, 40,
            41, 42, 43, 44, 45, 46, 47, 48, 49, 50,
            51, 52, 53, 54, 55, 56, 57, 58, 59, 60,
            61, 62, 63, 64, 65, 66, 67, 68, 69, 70,
            71, 72, 73, 74, 75, 76, 77, 78, 79, 80,
            81, 82, 83, 84, 85, 86, 87, 88, 89, 90,
            91, 92, 93, 94, 95, 96, 97, 98, 99, 100
        ]
        static_ip_file=await api_testings.state.redis.get('client_history')
        #static_ip_file_load=json.loads(static_ip_file)
        if static_ip_file is None:
            static_ip_file_load=[]
        else:
            static_ip_file_load=json.loads(static_ip_file)

        current_time=int(datetime.now().timestamp())
        for datss in static_ip_file_load:
            client_ip=datss['CLIENT_IP']
            client_local_history.append(client_ip)



        

        

        for server in server_data:
            server_ip=server['IP']

            total_incoming_requests=server['TOTAL_REQUESTS']
            
            if server_ip in client_local_history:
                for datas in static_ip_file_load:
                    client_check=datas['CLIENT_IP']
                    prev_rq=datas['TOTAL_DATA']
                    if client_check==server_ip:

                        current_requests=total_incoming_requests
                        past_requests=prev_rq
                        for li in numbers:
                            if li//60==0:
                                tacoma.append(li)
                        for snap in tacoma:
                            diff=current_time-snap
                            if diff%60==0:
                                current_window_1=diff


                                looking_back=current_time-60
                                value_2=current_window_1-looking_back
                                value_finder=value_2/60
                                prev_window_value=past_requests*value_finder
                                total_requests=prev_window_value+current_requests
                                if total_requests>rq_limit:
                                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail='API LIMIT EXCEEDED')
                                datas['TOTAL_DATA']=total_requests
                                await api_testings.state.redis.set('client_history',json.dumps(static_ip_file_load),ex=86400)
                                #return total_requests
                            



            else:
                current_requests=total_incoming_requests
                past_requests=0
                for li in numbers:
                    if li//60==0:
                        tacoma.append(li)
                for snap in tacoma:
                    diff=current_time-snap
                    if diff%60==0:
                        current_window_1=diff
                        looking_back=current_time-60
                        value_2=current_window_1-looking_back
                        value_finder=value_2/60
                        prev_window_value=past_requests*value_finder
                        total_requests=prev_window_value+current_requests
                        if total_requests>rq_limit:
                            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail='API LIMIT EXCEEDED')
                       
                        new_data={
                            'CLIENT_IP':server_ip,
                            'TOTAL_DATA':total_requests
                        }
                        static_ip_file_load.append(new_data)
                        await api_testings.state.redis.set('client_history',json.dumps(static_ip_file_load),ex=86400)


                    




                        

h=HELPERS()




@router.get('/get/response/')
async def getting_the_required_response(request:Request,user_model:API_TEST):
    get_client_ip=await h.getting_the_ip(request)
    #api_testings.state(get_client_ip)
    rq_count=await api_testings.state.redis.get(get_client_ip)
    client_history={
        'IP':get_client_ip,
        'TOTAL_REQUESTS':rq_count
    }

    client_data=await api_testings.state.redis.set('client_data',json.dumps(client_history),ex=1440)
    client_data=[client_history]
    api_limit_checker=await h.sliding_window_counter(client_data,client_data)
    #window_checker=await h.sliding_window_counter(api_limit_checker)


    if api_limit_checker is not None:
        if user_model=='YOUR_NAME':

            return JSONResponse(content={
                'message':'HELLO_USER'
            })
    

api_testings.include_router(router)
