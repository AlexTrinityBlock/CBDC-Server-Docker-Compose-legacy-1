from sys import flags
from itsdangerous import json

from sqlalchemy import false
import CryptUtil
import AccountUtil
import CurrencyUtil
import SQLiteUtil
import json
import uuid

def checkIfIsUUID(UUIDString:str):
    try:
        uuid.UUID(UUIDString)
 
        return True
    except ValueError:
        return False

def checkIfCurrencyDeposited(currency:str):
    isDeposited=SQLiteUtil.getDepositedStatusByCurrency(currency)
    if isDeposited == 0:
        return False
    else:
        return True

def findUserInfoFromHiddenInfoByCurrency(currency:str,hiddenInfo:str):
    hiddenInfoString1= SQLiteUtil.getHiddenUserInfoByCurrency(currency)
    hiddenInfoString2=hiddenInfo
    hiddenInfoObject1=json.loads(hiddenInfoString1)
    hiddenInfoObject2=json.loads(hiddenInfoString2)
    
    DoubleSpendingUserResult:str=""

    for i in range(len(hiddenInfoObject1)):
        #Possible1
        hideInfo1=CryptUtil.Base64StringToBytes(hiddenInfoObject1[i])
        hideInfo2=hiddenInfoObject2[i].encode("utf-8")
        XORedInfo=bytes(a ^ b for a, b in zip(hideInfo1, hideInfo2))
        
        try:
            DoubleSpendingUser=XORedInfo.decode("utf-8")
            if checkIfIsUUID(DoubleSpendingUser):DoubleSpendingUserResult=DoubleSpendingUser
        except:
            pass

        #Possible2
        hideInfo1=hiddenInfoObject1[i].encode("utf-8") 
        hideInfo2=CryptUtil.Base64StringToBytes(hiddenInfoObject2[i])
        XORedInfo=bytes(a ^ b for a, b in zip(hideInfo1, hideInfo2))

        try:
            DoubleSpendingUser=XORedInfo.decode("utf-8")
            if checkIfIsUUID(DoubleSpendingUser):DoubleSpendingUserResult=DoubleSpendingUser
        except:
            pass
    
    return DoubleSpendingUserResult

def checkCurrencyIsReal(currency:str):
    if SQLiteUtil.getNumberOfCurrency(currency)==1:
        return True
    else:
        return False

