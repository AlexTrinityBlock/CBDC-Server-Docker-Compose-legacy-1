# Scripts\activate.bat
# flask run --port 7070  --host=0.0.0.0
# pip install -r requirements.txt 
from unittest import result
import flask
from flask_cors import CORS
import SQLiteUtil
import uuid
import json
import CryptUtil
import VerifyUtil
import DepositUtil
import os
from flask import render_template,Flask,session,request,abort, redirect, url_for
from datetime import timedelta

app = flask.Flask(__name__)
CORS(app)
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=1)
app.config['SECRET_KEY'] = os.urandom(24)

publicKeyBase64=CryptUtil.bytesToBase64String(CryptUtil.readBytes("PublicKey.pem"))
privateKeyBase64=CryptUtil.bytesToBase64String(CryptUtil.readBytes("PrivateKey.pem"))

@app.route('/',methods=['GET'])
def homePage():
    NotDepositedYetCurrencys=SQLiteUtil.getCurrencyNotYetDepositForFrontEnd()
    CurrencysDeposited=SQLiteUtil.getCurrencyDepositedForFrontEnd()
    CurrencyDepositFail=SQLiteUtil.getCurrencyDepositFailForFrontEnd()
    binaryStrings = SQLiteUtil.getBinaryStringForFrontEnd()
    return render_template('index.html',NotDepositedYetCurrencys=NotDepositedYetCurrencys,CurrencysDeposited=CurrencysDeposited,CurrencyDepositFail=CurrencyDepositFail,binaryStrings=binaryStrings) 

@app.route('/deposit',methods=['GET'])
def deposit():
    DepositUtil.Deposit()
    return redirect('/')

@app.route('/store/public-key/',methods=['GET'])
def getStorePublicKey():
    result={
        "PublicKey":publicKeyBase64
    }
    return result

@app.route('/start-transaction/get-binary-string',methods=['GET'])
def StartTransaction():
    result:dict()
    session["RandomBinaryString"]=None
    session["ClientStart"]=None
    session["ClientStart"]="True"
    session["RandomBinaryString"]=VerifyUtil.randomBinaryString(10)
    SQLiteUtil.insertBinaryString(session["RandomBinaryString"])
    return session["RandomBinaryString"]

@app.route('/get-currency',methods=['POST'])
def getCurrency():
    # if session.get("RandomBinaryString")==None:return "Please get your session and Random Binary String First"
    CurrencyAndBankSignatureList=json.loads(request.values['CurrencyAndBankSignature'])
    HiddenUserInfoList=request.values['HiddenUserInfoList']
    
    for i in range(len(CurrencyAndBankSignatureList)):
        CurrencyAndBankSignature=CurrencyAndBankSignatureList[i]
        cipherCurrency=CurrencyAndBankSignature["CipherCurrency"]
        currency=CryptUtil.Base64RSADecrypt(cipherCurrency,privateKeyBase64)
        print(currency,HiddenUserInfoList)
        SQLiteUtil.insertTrade(HiddenUserInfoList,currency)
    return '{"Status":"Sucsess"}'

@app.route('/refresh-database',methods=['GET'])
def refreshDatabase():
    SQLiteUtil.createNewDatabase()
    return redirect("/")

if __name__ == '__main__':
    app.run()
