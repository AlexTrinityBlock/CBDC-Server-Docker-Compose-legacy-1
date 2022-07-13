import CryptUtil
import SQLiteUtil

def checkUserPassword(userName:str,userInputPassword:str):
    userPasswordHash=SQLiteUtil.getPasswordHashByUserName(userName)
    userInputPasswordHash=CryptUtil.bytesToBase64String(CryptUtil.StringSHA256(userInputPassword))
    if userPasswordHash==userInputPasswordHash and userInputPassword!="" :return True
    if userName=="" or userInputPassword=="":return False
    return False