from ast import Str
from codecs import utf_16_be_decode
import json
from urllib import response
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.Cipher import PKCS1_v1_5
from Crypto.Hash import SHA256, SHA1
from Crypto.Signature import pss
from Crypto.Util import Counter
from Crypto.PublicKey import RSA
import hashlib
import base64
import requests

def StringSHA256(KeyStr: str):
    byteString = bytes(KeyStr, "utf-8")
    hashObj = hashlib.sha256()
    hashObj.update(byteString)
    return hashObj.digest()

def BytesSHA256(KeyBytes: bytes):
    hashObj = hashlib.sha256()
    hashObj.update(KeyBytes)
    return hashObj.digest()

def writeBytes(byteMsg, fileName:str):
    with open(fileName, "ab+") as f:
        f.write(byteMsg)
        f.close()

def readBytes(fileName:str):
    result=bytes()
    with open(fileName, "rb") as f:
        result = f.read()
        f.close()
    return result

def RSAKeyPair():
    key = RSA.generate(2048)
    privateKey = key.exportKey()
    publicKey = key.publickey().exportKey()
    keyPair: dict = {"PublicKey":publicKey, "PrivateKey":privateKey}
    return keyPair

def RSAKeyPairFilesGenerator():
    reaKeyPair=RSAKeyPair()
    writeBytes(reaKeyPair["PublicKey"],"PublicKey.pem")
    writeBytes(reaKeyPair["PrivateKey"],"PrivateKey.pem")

def RSAencrypto(data: bytes, publicKey: bytes):
    # cipherRSA = PKCS1_OAEP.new(RSA.importKey(publicKey), hashAlgo=SHA256, mgfunc=lambda x,y: pss.MGF1(x,y, SHA1))
    # cipherRSA =PKCS1_v1_5.new(RSA.importKey(publicKey))
    cipherRSA =PKCS1_OAEP.new(RSA.importKey(publicKey),hashAlgo=SHA256)
    result = cipherRSA.encrypt(data)
    return result

def RSAdecrypto(data: bytes, privateKey: bytes):
    # cipherRSA = PKCS1_OAEP.new(RSA.importKey(privateKey), hashAlgo=SHA256, mgfunc=lambda x,y: pss.MGF1(x,y, SHA1))
    # cipherRSA =PKCS1_v1_5.new(RSA.importKey(privateKey))
    cipherRSA =PKCS1_OAEP.new(RSA.importKey(privateKey),hashAlgo=SHA256)
    result = cipherRSA.decrypt(data)
    return result

def bytesToBase64String(byteString):
    base64_bytes = base64.b64encode(byteString)
    return base64_bytes.decode('utf-8')

def Base64StringToBytes(base64String:str):
    base64_bytes = base64String.encode('utf-8')
    message_bytes = base64.b64decode(base64_bytes)
    return message_bytes

def Base64RSAEncrypt(Base64CiphertText:str,Base64PublicKey:str):
    PublicKeyBytes = Base64StringToBytes(Base64PublicKey)
    CiphertTextBytes =Base64StringToBytes(Base64CiphertText)
    return bytesToBase64String(RSAencrypto(CiphertTextBytes,PublicKeyBytes))

def Base64RSADecrypt(Base64CiphertText:str,Base64PrivateKey:str):
    PrivateKeyBytes = Base64StringToBytes(Base64PrivateKey)
    CiphertTextBytes =Base64StringToBytes(Base64CiphertText)
    result:str=(RSAdecrypto(CiphertTextBytes,PrivateKeyBytes)).decode("utf-8")
    return result

def RSASignature(StringPlainText:str,privateKey:bytes):
    stringSHA256=bytesToBase64String(StringSHA256(StringPlainText))
    signatureBase64String:str=Base64RSAEncrypt(stringSHA256,bytesToBase64String(privateKey))
    return signatureBase64String

def getServerBase64Publickey(PublickeyURL:str):
    requestSessionObject=requests.Session()
    responseText=requestSessionObject.get(PublickeyURL).text
    responseJson=json.loads(responseText)
    return responseJson["PublicKey"]
