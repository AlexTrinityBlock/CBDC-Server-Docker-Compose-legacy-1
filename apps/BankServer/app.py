# Scripts\activate.bat
# flask run --host=0.0.0.0
#flask run --port 8080  --host=0.0.0.0
# pip install -r requirements.txt 
from ast import Import
from locale import currency
from multiprocessing.connection import Client
import flask
from flask_cors import CORS
import CryptUtil
import AccountUtil
import CurrencyUtil
import SQLiteUtil
import VerifyUtil
import json
import os
from flask import render_template,Flask,session,request,redirect
from datetime import timedelta
from flask import render_template

app = flask.Flask(__name__)
CORS(app)
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=1)
app.config['SECRET_KEY'] = os.urandom(24)

@app.route('/',methods=['GET'])
def homePage():
    #User Info
    UsersInfo:list=SQLiteUtil.getAllUserInfoForFrontEnd()
    CurrencysInfo:list=SQLiteUtil.getCurrencyInfoForFrontEnd()
    DoubleSpendingCurrencysInfo:list=SQLiteUtil.getDoubleSpendingCurrencyInfoForFrontEnd()
    DoubleSpendingUsersInfo:list=SQLiteUtil.getDoubleSpendingUserInfoForFrontEnd()
    return render_template('index.html',UsersInfo=UsersInfo,CurrencysInfo=CurrencysInfo,DoubleSpendingUsersInfo=DoubleSpendingUsersInfo,DoubleSpendingCurrencysInfo=DoubleSpendingCurrencysInfo) 

@app.route('/user',methods=['GET'])
def userPage():
    return render_template('user.html')

@app.route('/useCurrency',methods=['GET'])
def userAPI():
    import Client
    currency=Client.GetCurrency()
    Client.SendToStroe(currency)
    return redirect('/user')

@app.route('/double-spenddig',methods=['GET'])
def doubleSpenddigAPI():
    import Client
    for i in range(2):
        Client.doubleSpending()
    return redirect('/user')

@app.route('/public-key/user/withdraw',methods=['GET'])
def transportPubblicKey():
    result:dict
    try:
        publicKeyBase64=CryptUtil.bytesToBase64String(CryptUtil.readBytes("PublicKey.pem"))
        result={
            "PublicKey":publicKeyBase64
        }
    except:
        result="[server]Public Key no found,try to use CryptUtil.RSAKeyPairFilesGenerator()"
    return json.dumps(result)
    
#領錢
@app.route('/get-currency',methods=['POST'])
def getCurrency():

    result=dict()
    bankPrivateKey:bytes=CryptUtil.readBytes("PrivateKey.pem")
    
    cipher_user_input:str=request.values['cipher_user_input']
    
    #解密失敗終止流程
    try:
        user_rsa_public_key=CryptUtil.Base64StringToBytes(request.values['user_rsa_public_key'])
        plain_user_input=(CryptUtil.RSAdecrypto(CryptUtil.Base64StringToBytes(cipher_user_input),bankPrivateKey)).decode("utf-8")
    except Exception as e:
        result={
            "Status":"Decrypt fail"            
        }
        return json.dumps(result)

    user_input_json=json.loads(plain_user_input)
    user_name=user_input_json["user_name"]
    if AccountUtil.checkUserPassword(user_name,user_input_json["user_password"]):
        currencyList=list()
        cipherCurrencyList=list()

        for i in range(user_input_json["withdrawal_number"]):
            currencyList.append(CurrencyUtil.issueNewCurrency())
            SQLiteUtil.decreaseBalanceByUserName(user_name)

        for plainCurrency in currencyList:
            cipherCurrency:bytes=CryptUtil.RSAencrypto(bytes(plainCurrency,"utf-8"),user_rsa_public_key)
            CurrencyBase64=CryptUtil.bytesToBase64String(cipherCurrency)
            CurrencyBase64Signature=CryptUtil.RSASignature(CurrencyBase64,bankPrivateKey)
            cipherCurrencyElement={
                "Currency":CurrencyBase64,
                "BankSignature":CurrencyBase64Signature
            }
            cipherCurrencyList.append(cipherCurrencyElement)

        result={
            "Status":"Success",
            "cipher_currency": cipherCurrencyList     
        }
    else:
        result={
            "Status":"Fail"            
        }
    return json.dumps(result)

#存錢
@app.route('/deposit',methods=['POST'])
def deposit():
    try:
        bankPrivateKey=CryptUtil.bytesToBase64String(CryptUtil.readBytes("PrivateKey.pem"))
        DepositJson:dict=json.loads(request.values['Deposit'])
        HiddenUserInfoList=DepositJson["hidden_user_info"]
        Currency=CryptUtil.Base64RSADecrypt( DepositJson["CipherCurrency"],bankPrivateKey)    
        #Check if it's valid coin
        if VerifyUtil.checkIfCurrencyDeposited(Currency) or  not (VerifyUtil.checkCurrencyIsReal(Currency)):
            print("Coin: ",Currency,"is Deposited")
            double_spendiner=VerifyUtil.findUserInfoFromHiddenInfoByCurrency(Currency,HiddenUserInfoList)
            SQLiteUtil.setDoubleSpenderbyUserID(double_spendiner)
            SQLiteUtil.setCurrencyDoubleSpending(Currency)
            return "Fail"
        else:
            SQLiteUtil.setCurrencyDeposited(Currency,HiddenUserInfoList)
            return "Success"
    except Exception as e :
        return "Decrypt fail"

#重置資料庫
@app.route('/refresh-database',methods=['GET'])
def refreshDatabase():
    SQLiteUtil.createNewDatabase()
    SQLiteUtil.creatExampleUser()
    SQLiteUtil.insertNewCurrency("5d37e4ff-9549-4569-9fb5-1d35e5801c3a")
    return redirect("/")

if __name__ == '__main__':
    app.run()

