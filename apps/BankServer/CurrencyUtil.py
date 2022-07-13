import uuid
import SQLiteUtil

def newCurrency():
    return str(uuid.uuid4())

def saveCurrencyToBankSQL(currencyUUID:str):
    SQLiteUtil.insertNewCurrency(currencyUUID)

def issueNewCurrency():
    newCurrencyUUID=newCurrency()
    saveCurrencyToBankSQL(newCurrencyUUID)
    return newCurrencyUUID