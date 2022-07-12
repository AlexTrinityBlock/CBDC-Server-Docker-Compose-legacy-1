import CryptUtil
import AccountUtil
import CurrencyUtil
import SQLiteUtil
import VerifyUtil
import json
from Client import *

if __name__ == '__main__':
    for i in range(1):
        currency=GetCurrency()
        SendToStroe(currency)

    requestSessionObject=requests.Session()
    responseObeject = requestSessionObject.get('http://127.0.0.1:7070/deposit')
