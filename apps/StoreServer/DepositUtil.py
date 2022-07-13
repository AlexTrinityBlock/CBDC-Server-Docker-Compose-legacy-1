import CryptUtil
import SQLiteUtil
import requests
import json

BankDepositURL='http://10.5.0.2:8080/deposit'
BankPublicKeyURL:str='http://10.5.0.2:8080/public-key/user/withdraw'

def Deposit():
    CurrencyWithoutDepositedList=SQLiteUtil.findCurrencyWithoutDeposited()
    requestSessionObject=requests.Session()
    BankBase64PublicKey=CryptUtil.getServerBase64Publickey(BankPublicKeyURL)
    result=[]
    for element in CurrencyWithoutDepositedList:
        currency=element["digital_currency"].encode("utf-8")
        cipherCurrency=CryptUtil.Base64RSAEncrypt(CryptUtil.bytesToBase64String(currency),BankBase64PublicKey)
        resultElement={"CipherCurrency":cipherCurrency,"hidden_user_info":element["hidden_user_info"]}
        result.append(resultElement)

    print("Number of Deposit data",len(result))

    for i in range(len(result)):
        responseObeject = requestSessionObject.post(BankDepositURL,data={"Deposit":json.dumps(result[i])})
        print(responseObeject.text,"\n")
        #If it's valid coin save record to Database
        if responseObeject.text=="Success":
            SQLiteUtil.setDepositedByCurrency(CurrencyWithoutDepositedList[i]["digital_currency"].encode("utf-8"))
        else:
            SQLiteUtil.setDepositFailByCurrency(CurrencyWithoutDepositedList[i]["digital_currency"].encode("utf-8"))


