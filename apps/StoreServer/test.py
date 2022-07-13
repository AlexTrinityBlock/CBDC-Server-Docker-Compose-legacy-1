from urllib import response
import CryptUtil
import SQLiteUtil
import DepositUtil

if __name__ == '__main__':
    # CryptUtil.RSAKeyPairFilesGenerator()
    # SQLiteUtil.createNewDatabase()
    # SQLiteUtil.insertTrade("AAA","BBB")
    # publicKeyBase64=CryptUtil.bytesToBase64String(CryptUtil.readBytes("PublicKey.pem"))
    # print(publicKeyBase64)
    # SQLiteUtil.getCurrencyNotYetDepositForFrontEnd()
    # DepositUtil.Deposit()
    publicKeyBase64=CryptUtil.bytesToBase64String(CryptUtil.readBytes("PublicKey.pem"))
    privateKeyBase64=CryptUtil.bytesToBase64String(CryptUtil.readBytes("PrivateKey.pem"))

    CryptUtil.Base64RSAEncrypt("ABC",publicKeyBase64)