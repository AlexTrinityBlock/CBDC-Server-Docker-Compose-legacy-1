from unittest import result
import requests
import json
import CryptUtil
import SQLiteUtil
import string    
import random

#Bank URL
BankPublicKeyURL:str='http://10.5.0.5:8080/public-key/user/withdraw'
BankGetCurrencyURL:str='http://10.5.0.5:8080/get-currency'

#Store URL
StorePublicKey="http://10.5.0.6:8081/store/public-key/"
StoreStartTransactionURL="http://10.5.0.6:8081/start-transaction/get-binary-string"
SendCurrencyToStoreURL="http://10.5.0.6:8081/get-currency"

#UserID
user_name="Alice"
user_uuid="30a1bf87-b0e1-4921-a0b8-8c602af1f391"

#User Key Pair
keyPair=CryptUtil.RSAKeyPair()
UserPublicKey=keyPair["PublicKey"]
UserPrivateKey=keyPair["PrivateKey"]

def randomString(S):
    return  ''.join(random.choices(string.ascii_letters + string.digits, k = S))

def StringXOR(String1:str,String2:str):
    bytes1=String1.encode("utf-8")
    bytes2=String2.encode("utf-8")
    bytesXORed=bytes(a ^ b for a, b in zip(bytes1, bytes2))
    return CryptUtil.bytesToBase64String(bytesXORed)

def GetCurrency():
    #User get bank's public key
    requestSessionObject=requests.Session()
    responseObeject = requestSessionObject.get(BankPublicKeyURL)
    responseJSON=json.loads(responseObeject.text)
    serverPublicKey= CryptUtil.Base64StringToBytes(responseJSON["PublicKey"])
    #User send to bank for withdraw
    user_input={
        "user_name":"Alice",
        "user_password":"abc",
        "withdrawal_number":1
    }
    user_input_bytes=bytes(json.dumps(user_input),"utf-8")
    CipherText=CryptUtil.RSAencrypto(user_input_bytes,serverPublicKey)
    CipherTextB64=CryptUtil.bytesToBase64String(CipherText)
    responseText=requestSessionObject.post(BankGetCurrencyURL,data={'cipher_user_input': CipherTextB64,'user_rsa_public_key':CryptUtil.bytesToBase64String(UserPublicKey)}).text

    #User decrypt bank response
    BanReturnCurrencyJson = json.loads(responseText)
    cipherCurrencyList=BanReturnCurrencyJson["cipher_currency"]
    currencyList=list()

    for currencyAndSigNature in cipherCurrencyList:
        currency=CryptUtil.Base64RSADecrypt(currencyAndSigNature["Currency"],CryptUtil.bytesToBase64String(UserPrivateKey))
        currencyList.append({"Currency":currency,"BankSignature":currencyAndSigNature["BankSignature"]})

    # print("===============Get Currency===============\n",json.dumps(currencyList, indent=4, sort_keys=True),"\n===================================\n")
    return currencyList

#Send to Store
def SendToStroe(currencyList:list=None):
    #init
    storePublicKey=bytes()
    binaryString = str()
    randomStrings=[]

    #Print Currency List
    print(currencyList,"\n")

    #init random number
    for i in range(10):
        randomStrings.append(randomString(36))
    print("Random String\n",randomStrings,"\n")

    #User get store's public key
    requestSessionObject=requests.Session()
    responseObeject = requestSessionObject.get(StorePublicKey)
    responseJSON=json.loads(responseObeject.text)
    storePublicKey= CryptUtil.Base64StringToBytes(responseJSON["PublicKey"])

    #Get binary String
    responseObeject=requestSessionObject.get(StoreStartTransactionURL)
    binaryString=responseObeject.text
    print("Binary String:",binaryString,"\n")

    #XOR  follow Binary String to XOR UserID with Random Value
    resultList=list()
    counter=0
    for binaryChart in binaryString:
        if(binaryChart=="0"):
            resultList.append(randomStrings[counter])
        else:
            resultList.append(StringXOR(randomStrings[counter],user_uuid))
        counter+=1

    #Encrypt currency
    cipherCurrencyList=[]
    
    for currency in currencyList:
        currencyString=currency["Currency"]
        cryptCurrency=CryptUtil.RSAencrypto(currencyString.encode("utf-8"),storePublicKey)
        cryptCurrencyBase64=CryptUtil.bytesToBase64String(cryptCurrency)
        element={"CipherCurrency":cryptCurrencyBase64,"BankSignature":currency["BankSignature"]}
        cipherCurrencyList.append(element)

    result=json.dumps(cipherCurrencyList)
    resultHiddenUserInfo=json.dumps( resultList)
    responseObeject =requestSessionObject.post(SendCurrencyToStoreURL,data={"CurrencyAndBankSignature":result,"HiddenUserInfoList":resultHiddenUserInfo})
    print(responseObeject.text)

def doubleSpending():
    #init
    storePublicKey=bytes()
    binaryString = str()
    randomStrings=[]

    doubleSpendingCurrency=[
        {'Currency': '5d37e4ff-9549-4569-9fb5-1d35e5801c3a', 'BankSignature': 'dAfpq93f6cn8qCBtvgYXO1IGpxd3GDAcLrR5sfmVCx+yVEJ9Ss427z4N0PLDPAfGFCkS/uHykHtX0nCDjYIWT/bponKFHFa59oGMjiSFb1dHaV0WOF0SN+ni8A4XtwZwO2g1xSiMBcl1ZVvIys8Y8R2VMCDlLdUSF5oQoMiTSz+JXpilMjnSvB+ezPdeE/O+O2K4fJBcA0tQcVqZH0EstG7SxpezzfSUgOvljmFJGKCUR92bZ0VmtUvF4EY273n5uJ4lUJVNSGWZvd33hzjlc9jElB7hKg9PnR3uI1NT5J0N/HA/2wHdBFKpkNFui0dOC+33RjklAtJeuzybX6q/qg=='}, 
        # {'Currency': '3fa53627-e658-457d-bcc4-1bca7f655ebc', 'BankSignature': 'BuIsDxUOMSoPmDQ0turs4/96cnwh0pf2GTDiJ+kFrA6ESFFiuINT95Q2+4igvHjIXUspA02dKfMIRn4GC1FYWRuIq8EiRiyYPYdYh2s4yGP3xiSSidcaG+jC80fADkV3OboTLfXIpqusSMk1k9W+xgc1q13EQ9noDBW0COFyYcxmLc71GCX8/UHT1x+1YDodgh7WMzJDlWT+BcC9Im11eeb7rhcOdteBJ3IbGUXlPuWke3Btrad78DRm541+VShdmIMrPxd0J5hwpH45TyTaKNOilP15B1BjoEO2Y+L0JO+CVo7V/PrmANwO+5OiuHAEGMhBmT86Dz6c1zmJSD4fQQ=='}, 
        # {'Currency': '29f08f62-e702-4bad-adda-162851ffaaae', 'BankSignature': 'foxB3KMQ9wo4/yDVHj6g22eJtwhjvxI28LbEdLaLki71A6IQxDKRs7t7WvuKnIKurU41SxDGnZy6YJ0gaIIzOpDIr1hgNAZeVv9X4nlyvwYz+cdq2UrvOd0e68hAuDunfvFYQivE5eZPcD60OfwN6l7JErTmHn5KhP4Wt3MLXhTuJM+FMwHPEapZ/+dOy41iW+JdsfsTKmYrQBe4zH2otxB3GN/AjDZ2I8yZKAPJwf7Pp/9AKppnQVdSYU6l+EgPviZhaUhskrV6bZrweENXyO8Ag+Ba5yl7Hv94Rwe3zJFo4k7FP/p+VeqIYuUHwXlF8E+Q/TZATCg5XC7uvl7xpw=='}
    ]

    doubleSpendingRandomStrings= [
        'o9hvXJCmKBDrokM0f9Lukj7nrGHDAkmIGMIZ', 
        '2SPWxdx54ozthNDcMlpLxRGUbfBO6NTiobpI', 
        'Vkftggy4XpDb3rH1HYT6P0kIt2wjTXkMKgN2', 
        'DWgq2ftxTDynBA7LmIF9CnW0dAcX5x3aeEya', 
        'fYT2OJoaq4kzDVn4CgJi8R2puAk4UVz4J1d9', 
        'fEysjC6i9NzIh5gyPg2K4Xg9Xl2JKgV8IAl0', 
        'Qhih5Dme68XDr14CRnCMlDvjM3zOM0ptBryd', 
        'hf67gMH0ZMSJedMJmC2SfDeV73aTyKmLFePV', 
        'DI98GOezA631OkZ5CTEChw6T2vyYlwNqSVEM', 
        'J24ltAtCKL1ZKDsJddXZWxobBMzmPfrOu3tf'
    ]

    randomStrings=doubleSpendingRandomStrings
    currencyList=doubleSpendingCurrency
    

    #User get store's public key
    requestSessionObject=requests.Session()
    responseObeject = requestSessionObject.get(StorePublicKey)
    responseJSON=json.loads(responseObeject.text)
    storePublicKey= CryptUtil.Base64StringToBytes(responseJSON["PublicKey"])

    #Get binary String
    responseObeject=requestSessionObject.get(StoreStartTransactionURL)
    binaryString=responseObeject.text
    print("Binary String:",binaryString,"\n")

    #XOR  follow Binary String to XOR UserID with Random Value
    resultList=list()
    counter=0
    for binaryChart in binaryString:
        if(binaryChart=="0"):
            resultList.append(randomStrings[counter])
        else:
            resultList.append(StringXOR(randomStrings[counter],user_uuid))
        counter+=1

    #Encrypt currency
    cipherCurrencyList=[]

    for currency in currencyList:
        currencyString=currency["Currency"]
        cryptCurrency=CryptUtil.RSAencrypto(currencyString.encode("utf-8"),storePublicKey)
        cryptCurrencyBase64=CryptUtil.bytesToBase64String(cryptCurrency)
        element={"CipherCurrency":cryptCurrencyBase64,"BankSignature":currency["BankSignature"]}
        cipherCurrencyList.append(element)

    result=json.dumps(cipherCurrencyList)
    resultHiddenUserInfo=json.dumps( resultList)
    responseObeject =requestSessionObject.post(SendCurrencyToStoreURL,data={"CurrencyAndBankSignature":result,"HiddenUserInfoList":resultHiddenUserInfo})
    print(responseObeject.text)

