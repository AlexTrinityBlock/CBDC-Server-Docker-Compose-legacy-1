from ctypes.wintypes import INT
import sqlite3
import os
from itsdangerous import json
import sqlalchemy
import CryptUtil
from sqlalchemy.orm import Session
from sqlalchemy import Table, Column, Integer, String, MetaData
from sqlalchemy.orm import sessionmaker
import json

engine = sqlalchemy.create_engine('sqlite:///./database/store.db')
connection = engine.connect()
meta = sqlalchemy.MetaData()

#User DataTable
storeWalletTable = Table(
'STOREWALLET', meta, 
Column('id', Integer, primary_key = True,autoincrement=True), 
Column('hidden_user_info', String), 
Column('digital_currency', String),
Column('deposited', Integer),
Column('deposit_fail', Integer)
)

binaryStringTable = Table(
'BINARYSTRINGS', meta, 
Column('id', Integer, primary_key = True,autoincrement=True), 
Column('binary_string', String),
)

def createNewDatabase():
    if os.path.isfile("./database/store.db"):
        os.remove("./database/store.db")        
    SQLQuery:str
    with open("./database/schema","r", encoding = 'utf-8') as f:
        SQLQuery=f.read()
    conn=None
    conn = sqlite3.connect("./database/store.db")
    c = conn.cursor()
    c.executescript(SQLQuery)
    conn.close()

def insertTrade(hidden_user_info_i:str,digital_currency_i:str):
    ins = storeWalletTable.insert().values(hidden_user_info=hidden_user_info_i,digital_currency=digital_currency_i)
    conn = engine.connect()
    conn.execute(ins)

def insertBinaryString(binary_string_i:str):
    ins = binaryStringTable.insert().values(binary_string=binary_string_i)
    conn = engine.connect()
    conn.execute(ins)

def findCurrencyWithoutDeposited():
    Session = sessionmaker(bind=engine)
    session=Session()
    returnResult=list()
    for instance in session.query(storeWalletTable).filter_by(deposited=0):
        if instance.deposited !=1:
            returnResult.append({"hidden_user_info":instance.hidden_user_info,"digital_currency":instance.digital_currency})
    return returnResult

def setDepositedByCurrency(currency:bytes):
    currency=currency.decode("utf-8")
    print("Set",currency,"Deposited")
    s=storeWalletTable.update().where(storeWalletTable.c.digital_currency==currency).values(deposited=1)
    conn = engine.connect()
    conn.execute(s)

def setDepositFailByCurrency(currency:bytes):
    currency=currency.decode("utf-8")
    print("Set",currency,"Deposited")
    s=storeWalletTable.update().where(storeWalletTable.c.digital_currency==currency).values(deposit_fail=1)
    conn = engine.connect()
    conn.execute(s)

def getCurrencyNotYetDepositForFrontEnd():
    s=storeWalletTable.select().where(storeWalletTable.c.deposited==0,storeWalletTable.c.deposit_fail==0)
    conn = engine.connect()
    results = conn.execute(s)
    returnResult=list()
    for result in results:
        currency=result[2]
        hiddenUserInfo=json.loads(result[1])
        hiddenUserInfo=hiddenUserInfo[0][:30]+"..."
        resultList=list(result)
        returnResult.append([currency,hiddenUserInfo])
    return returnResult

def getCurrencyDepositedForFrontEnd():
    s=storeWalletTable.select().where(storeWalletTable.c.deposited==1 , storeWalletTable.c.deposit_fail!=1)
    conn = engine.connect()
    results = conn.execute(s)
    returnResult=list()
    for result in results:
        currency=result[2]
        hiddenUserInfo=json.loads(result[1])
        hiddenUserInfo=hiddenUserInfo[0][:30]+"..."
        resultList=list(result)
        returnResult.append([currency,hiddenUserInfo])
    return returnResult

def getCurrencyDepositFailForFrontEnd():
    s=storeWalletTable.select().where(storeWalletTable.c.deposit_fail==1)
    conn = engine.connect()
    results = conn.execute(s)
    returnResult=list()
    for result in results:
        currency=result[2]
        hiddenUserInfo=json.loads(result[1])
        hiddenUserInfo=hiddenUserInfo[0][:30]+"..."
        returnResult.append([currency,hiddenUserInfo])
    return returnResult

def getBinaryStringForFrontEnd():
    s=binaryStringTable.select()
    conn = engine.connect()
    results = conn.execute(s)
    returnResult=list()
    for result in results:
        binaryString=result[1]
        returnResult.append(binaryString)
    return returnResult