from ctypes.wintypes import INT
import sqlite3
import os
from itsdangerous import json
import sqlalchemy
import CryptUtil
from sqlalchemy.orm import Session
from sqlalchemy import Table, Column, Integer, String, MetaData
import json

engine = sqlalchemy.create_engine('sqlite:///./database/bank.db')
connection = engine.connect()
meta = sqlalchemy.MetaData()

#User DataTable
userTable = Table(
'USER', meta, 
Column('id', Integer, primary_key = True,autoincrement=True), 
Column('user_name', String), 
Column('balance', Integer), 
Column('double_spending', Integer), 
Column('password_hash', String), 
Column('user_uuid', String)
)

#CURRENCY datatable
currencyTable=Table(
'CURRENCY', meta, 
Column('id', Integer, primary_key = True,autoincrement=True), 
Column('currency', String), 
Column('deposited', Integer), 
Column('hidden_user_info', String), 
Column('binary_string', String),
Column('double_spending', Integer)
)

def createNewDatabase():
    if os.path.isfile("./database/bank.db"):
        os.remove("./database/bank.db")        
    SQLQuery:str
    with open("./database/schema","r", encoding = 'utf-8') as f:
        SQLQuery=f.read()
    conn=None
    conn = sqlite3.connect("./database/bank.db")
    c = conn.cursor()
    c.executescript(SQLQuery)
    conn.close()

#https://www.tutorialspoint.com/sqlalchemy/sqlalchemy_quick_guide.htm
def insertUser(user_name_i:str,balance_i:int,password_hash_i:str,user_uuid_i:str):
    ins = userTable.insert().values(user_name=user_name_i,balance=balance_i,password_hash=password_hash_i,user_uuid=user_uuid_i)
    conn = engine.connect()
    conn.execute(ins)

def insertNewCurrency(currency_i:str):
    ins = currencyTable.insert().values(currency=currency_i)
    conn = engine.connect()
    conn.execute(ins)

def insertCurrencyTable(currency_i:str,withdrawn_i:int,hidden_user_info_i:str,binary_string_i:str):
    ins = userTable.insert().values(currency=currency_i,withdrawn=withdrawn_i,hidden_user_info=hidden_user_info_i,binary_string=binary_string_i)
    conn = engine.connect()
    conn.execute(ins)

def creatExampleUser():
    insertUser("Alice",100,CryptUtil.bytesToBase64String(CryptUtil.StringSHA256("abc")),"30a1bf87-b0e1-4921-a0b8-8c602af1f391")
    insertUser("Bob",100,CryptUtil.bytesToBase64String(CryptUtil.StringSHA256("def")),"06705e5f-083f-4c1c-bafe-38075d9a51e0")

def getPasswordHashByUserName(userNme:str=""):
    s=userTable.select().where(userTable.c.user_name==userNme)
    conn = engine.connect()
    results = conn.execute(s)
    returnResult=None
    for result in results:
        print(result)
        returnResult=result[4]
    return returnResult

def getBalanceByUserName(userName:str=""):
    s=userTable.select().where(userTable.c.user_name==userName)
    conn = engine.connect()
    results = conn.execute(s)
    returnResult=None
    for result in results:
        returnResult=result[2]
    return returnResult

def updateBalanceByUserName(userName:str="",newBalance:int=None):
    s=userTable.update().where(userTable.c.user_name==userName).values(balance=newBalance)
    conn = engine.connect()
    conn.execute(s)

def decreaseBalanceByUserName(userName:str):
    oldBalance=getBalanceByUserName(userName)
    if oldBalance >0:
        updateBalanceByUserName(userName,oldBalance-1)
    else:
        raise Exception("Balance = 0")

def getUserIDByUserName(userNme:str=""):
    s=userTable.select().where(userTable.c.user_name==userNme)
    conn = engine.connect()
    results = conn.execute(s)
    returnResult=None
    for result in results:
        returnResult=result[0]
    return returnResult

def getDepositedStatusByCurrency(currency:str):
    s=currencyTable.select().where(currencyTable.c.currency==currency)
    conn = engine.connect()
    results = conn.execute(s)
    returnResult=None
    for result in results:
        returnResult=result[2]
    return returnResult

def setCurrencyDeposited(currency:str,HiddenUserInfoListString:str):
    s=currencyTable.update().where(currencyTable.c.currency==currency).values(deposited=1,hidden_user_info=HiddenUserInfoListString)
    conn = engine.connect()
    conn.execute(s)

def setCurrencyDoubleSpending(currency:str):
    s=currencyTable.update().where(currencyTable.c.currency==currency).values(double_spending=1)
    conn = engine.connect()
    conn.execute(s)


def getHiddenUserInfoByCurrency(currency:str):
    s=currencyTable.select().where(currencyTable.c.currency==currency)
    conn = engine.connect()
    results = conn.execute(s)
    returnResult=None
    for result in results:
        returnResult=result[3]
    return returnResult

def setDoubleSpenderbyUserID(doubleSpenderID:str):
    print("Set",doubleSpenderID)
    s=userTable.update().where(userTable.c.user_uuid==doubleSpenderID).values(double_spending=1)
    conn = engine.connect()
    conn.execute(s)

def getAllUserInfoForFrontEnd():
    s=userTable.select()
    conn = engine.connect()
    results = conn.execute(s)
    returnResult=list()
    for result in results:
        resultList=list(result)
        returnResult.append([resultList[5],resultList[1],resultList[2]])
    return returnResult

def getCurrencyInfoForFrontEnd():
    s=currencyTable.select().where(currencyTable.c.double_spending!=1)
    conn = engine.connect()
    results = conn.execute(s)
    returnResult=list()
    for result in results:
        resultList=list(result)
        isDeposited=""
        if resultList[2]==1:isDeposited="Yes"
        else:isDeposited="No"
        
        try:
            HiddenUserInfoList=json.loads(resultList[3])
            returnResult.append([resultList[1],HiddenUserInfoList[0][:30]+"...",isDeposited])
        except:
            returnResult.append([resultList[1],"Not Deposited Yet",isDeposited])
            pass

    return returnResult

def getDoubleSpendingCurrencyInfoForFrontEnd():
    s=currencyTable.select().where(currencyTable.c.double_spending==1)
    conn = engine.connect()
    results = conn.execute(s)

    returnResult=list()
    for result in results:
        resultList=list(result)
        isDeposited=""
        if resultList[2]==1:isDeposited="Yes"
        else:isDeposited="No"
        
        try:
            HiddenUserInfoList=json.loads(resultList[3])
            returnResult.append([resultList[1],HiddenUserInfoList[0][:30]+"...",isDeposited])
        except:
            returnResult.append([resultList[1],"Not Deposited Yet",isDeposited])
            pass

    return returnResult

def getDoubleSpendingUserInfoForFrontEnd():
    s=userTable.select().where(userTable.c.double_spending==1)
    conn = engine.connect()
    results = conn.execute(s)
    returnResult=list()
    for result in results:
        resultList=list(result)
        returnResult.append([resultList[5],resultList[1]])
    return returnResult

def getNumberOfCurrency(currency:str):
    s=currencyTable.select().where(currencyTable.c.currency==currency)
    conn = engine.connect()
    results = conn.execute(s)
    counter=0
    for result in results:
        counter+=1
    return counter