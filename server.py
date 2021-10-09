#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 11 16:15:58 2020

@author: savas
"""


## depencies

# sudo pip install pandas emoji  mysql-connector-python flask-cors

from flask import Flask
from flask import request, jsonify, Response
from flask_cors import CORS, cross_origin
#from flask_jsonpify import jsonpify



from env import sql_

import mysql.connector

import uuid 
import json

import pandas as pd
app = Flask(__name__)



def dbConnector():
        
        #development and production db
        mydb = mysql.connector.connect(host=sql_['host'],database=sql_['database'],user=sql_['user'],password=sql_['password'])


        #production database
        #mydb = mysql.connector.connect(host='127.0.0.1',database='admin_chatlab',user='admin_chatlab',password='Drd0o13&')

        return mydb

app.config['DEBUG'] = True
CORS(app)
@cross_origin() 



@app.route('/')
def home():
      return 'data process'
  


@app.route('/test')
def test():
      return 'data process test'
  


@app.route("/text", methods=[ 'GET'])
def text():
     if request.method == 'GET':
        _slug = request.args.get('slg')
        mydb= dbConnector()
        cur = mydb.cursor()
        sql = "SELECT data_ FROM veri WHERE data_slug = '%s'""" % (_slug)
        
        cur.execute(sql)

        _text = cur.fetchone()
        cur.close()
        mydb.close()

        if _text:
            return  { 'status':200, 'value':json.loads(_text[0]) }
        else:

            return { 'status':201, 'value':'data not exist' }
       
        
     return { 'status':405, 'val':'methot not allowed' }

@app.route("/veri", methods=['POST', 'GET'])
def veri():
     if request.method == 'POST':
         
        text_ = request.form['text']
        ip_ = request.form['ip']
        slug = uuid.uuid4().hex[:16].lower()

        try:
            veri = dataProcess(text_) 
            d = json.dumps(veri._dict)
        except:
            veri = None
            d = 'bos'

        
        
        if veri:
            
            mydb= dbConnector()
            cur = mydb.cursor()
            try:
                cur.execute("INSERT INTO veri (data_, data_user_ip, data_slug) VALUES (%s, %s, %s)", (d, ip_, slug))
                mydb.commit()
                
                return { 'status':200, 'val':slug }
            except Exception as e:

                result = { 'status':406, 'val':str(e) }
                return result
            finally:
                cur.close()
                mydb.close()
        else:

            mydb= dbConnector()
            cur = mydb.cursor()
            cur.execute("INSERT INTO veri (data_text,data_, data_user_ip, data_slug) VALUES (%s, %s, %s, %s)", (text_, 'error', ip_, slug))
            mydb.commit()
            cur.close()
            mydb.close()

            return { 'status':403, 'val':'data error' }


     return { 'status':405, 'val':'methot not allowed' }


if __name__ == "__main__":
    
    app.run(host='0.0.0.0')