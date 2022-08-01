# 銀行端

## 網頁框架

銀行端使用的網頁框架為Python的flask，支援RESTFul API。

[Wiki RESTFul條目](https://zh.wikipedia.org/wiki/%E8%A1%A8%E7%8E%B0%E5%B1%82%E7%8A%B6%E6%80%81%E8%BD%AC%E6%8D%A2)

| GET | POST | PUT | DELETE |
|-----|------|-----|--------|
| 取得資料 | 存入新資料 | 更新舊資料 | 刪除資料 |

## Port

銀行端預設使用`8080`port

## 網頁與API路徑

### 模擬使用者相關

[/](http://127.0.0.1:8080/) ***GET方法***，提供銀行端前端頁面，由於過往使用flask預設的`Jinja2`模板引擎，之後計畫改成基於[Ajax](https://developer.mozilla.org/zh-TW/docs/Web/Guide/AJAX)或者[Fetch](https://developer.mozilla.org/zh-TW/docs/Web/API/Fetch_API)的前後端分離架構。

[/user](http://127.0.0.1:8080/user) ***GET方法***，模擬使用者進行交易的頁面。

[/useCurrency](http://127.0.0.1:8080/useCurrency) ***GET方法***，模擬使用者使用貨幣的API，一觸發會立刻讓銀行發行一枚貨幣，並且同一瞬間在商店使用一枚貨幣。可以到商店和銀行端進行檢查，使用後會重新導向至模擬使用者頁面。

[/double-spenddig](http://127.0.0.1:8080/double-spenddig) ***GET方法***，模擬惡意使用者進行重複支付。可以到商店和銀行端進行檢查，使用後會重新導向至模擬使用者頁面。

### 銀行金鑰取得API

[/public-key/user/withdraw](http://127.0.0.1:8080/public-key/user/withdraw) ***GET方法***，取得銀行公鑰，該金鑰使用於使用者進行提款時，使用者將提款請求內容以公鑰進行加密，發送給銀行。

```json
{
    "PublicKey":"Base64格式的RSA公鑰"
}
```

### 使用者提款API

[/get-currency](http://127.0.0.1:8080/get-currency) ***POST方法***，輸入為用上方銀行公鑰API[/public-key/user/withdraw](http://127.0.0.1:8080/public-key/user/withdraw)取得的公鑰加密的使用者輸入，加密後的輸入內容如下:

```json
{
    "cipher_user_input":"加密後的使用者輸入",
    "user_rsa_public_key":"使用者公鑰",
}
```

`cipher_user_input`中的加密後的使用者內容，如下:

```json
{
    "user_name":"使用者名稱",
    "user_password":"使用者密碼",
    "withdrawal_number":"提領的金額",
}
```

在輸入上述資料後，成功提取的每一枚硬幣，都會以下列格式從銀行返回:

***單一枚貨幣***

```json
{
    "Currency":"加密後轉Base64的數位貨幣UUID",
    "BankSignature":"數位貨幣的銀行私鑰簽章",
}
```

***整批貨幣(好幾枚數位貨幣)***

當提領成功的狀態:

```json
{
    "Status":"Success",
    "cipher_currency": ["單一枚貨幣1","單一枚貨幣2","單一枚貨幣3"]     
}
```

領取失敗:

```json
{
    "Status":"Fail",
}
```

### 存款API

[/deposit](http://127.0.0.1:8080/deposit) ***POST方法***，讓商店得以將貨幣存入銀行。

```json
{
    "Deposit":{
        "hidden_user_info":"重複支付時就，可以用XOR導出使用者ID的驗證碼。",
        "CipherCurrency":"加密後轉Base64的貨幣。",
    }
}
```

### 重置資料庫

[/refresh-database](http://127.0.0.1:8080/refresh-database) ***GET方法***，重置銀行資料庫，用於測試，觸發後跳轉到\銀行首頁。

## Python自製模塊文檔

### AccountUtil.py

用於檢查使用者密碼是否正確，其中會檢查密碼的SHA256。

`checkUserPassword(userName:str,userInputPassword:str)`

* userName: 字串型別，使用者名稱。

* userInputPassword: 字串型別，使用者密碼。

* return: 布林型別，True代表密碼正確，False代表密碼錯誤。

### CryptUtil.py

輔助加密解密工具，還有進行Hash驗證。

`StringSHA256(KeyStr: str)`

* KeyStr: 字串型別，要轉換成SHA256 Hash的字串。

* return: bytes型別，SHA256 Hash。

`BytesSHA256(KeyBytes: bytes)`

* KeyBytes: bytes型別，SHA256 Hash的bytes。

* return: bytes型別，SHA256 Hash。

`writeBytes(byteMsg, fileName:str)`

* byteMsg: bytes型別，要寫入檔案的bytes。

* fileName: 字串型別，要寫入的檔案路徑。

`readBytes(fileName:str)`

* fileName: 字串型別，要讀取的檔案路徑。

* return: bytes型別，讀入的bytes。

`RSAencrypto(data: bytes, publicKey: bytes)`

以RSA進行加密。

* data: bytes型別，要加密的bytes資料。

* publicKey: RSA公鑰。

* return: bytes型別，加密後的bytes資料。

`RSAdecrypto(data: bytes, privateKey: bytes)`

以RSA進行解密。

* data: bytes型別，要解密的bytes資料。

* privateKey: RSA私鑰。

* return: bytes型別，解密後的bytes資料。

`bytesToBase64String(byteString)`

將bytes轉換成Base64。

* byteString: bytes型別，要轉換成Base64的bytes內容。

* return: 字串型別，轉換後的Base64字串。

`Base64StringToBytes(base64String:str)`

將Base64轉換成bytes。

* base64String: 字串型別，要轉換的Base64。

* return: bytes型別，轉換後的bytes。

`Base64RSAEncrypt(Base64CiphertText:str,Base64PublicKey:str)`

將Base64字串RSA加密。

* Base64CiphertText: 字串型別，要加密的Base64字串。

* Base64PublicKey: 字串型別，Base64RSA公鑰。

* return: 字串型別，加密後的Base64字串。

`Base64RSADecrypt(Base64CiphertText:str,Base64PrivateKey:str)`

將Base64字串RSA解密。

* Base64CiphertText: 字串型別，要解密的Base64字串。

* Base64PrivateKey: 字串型別，Base64RSA私鑰。

* return: 字串型別，解密後的Base64字串。

`RSASignature(StringPlainText:str,privateKey:bytes)`

* StringPlainText: 字串型別，簽章的Base64字串。

* privateKey: bytes型別，簽章用的私鑰。

* return: 字串型別，簽章Base64字串。

### CurrencyUtil.py

`newCurrency()`

建立一顆枚的數位貨幣，採取的是極度不容易重複的[UUID](https://zh.wikipedia.org/zh-tw/%E9%80%9A%E7%94%A8%E5%94%AF%E4%B8%80%E8%AF%86%E5%88%AB%E7%A0%81)。

* return: 字串型別，一串通常獨一無二的字串。

`saveCurrencyToBankSQL(currencyUUID:str)`

將貨幣存入銀行的SQL中。

* currencyUUID: 字串型別，要存入SQL的貨幣。

`issueNewCurrency()`

先產生新的數位貨幣，然後存入銀行的SQL中。

* return: 字串型別，新產生的數位貨幣。

### SQLiteUtil.py

`createNewDatabase()`

建立新的SQLite資料庫，其實是個檔案，之後將回移動到MySQL上。

`insertUser(user_name_i:str,balance_i:int,password_hash_i:str,user_uuid_i:str)`

加入新的使用者，並且同時加入密碼的hash, 存款, 使用者UUID。

* user_name_i: 字串型別，使用者名稱。

* balance_i: 整數型別，存款金額。

* password_hash_i: 字串型別，密碼Hash。

* user_uuid_i: 字串型別，使用者UUID。

`insertNewCurrency(currency_i:str)`

加入新發行的數位貨幣字串到資料庫。

* currency_i: 字串型別，發行貨幣字串。

`insertCurrencyTable(currency_i:str,withdrawn_i:int,hidden_user_info_i:str,binary_string_i:str)`

加入已經兌換的數位貨幣到資料庫。

* currency_i: 字串型別，數位貨幣字串UUID。

* withdrawn_i: 數字型別，代表是否被領取。

* hidden_user_info_i: 字串型別，用來提取雙花使用者ID的字串。

* binary_string_i: 字串型別，二進位字串。

`creatExampleUser()`

建立範例使用者Alice與Bob。

Alice的密碼是`abc`，Bob的密碼是`def`。

`getPasswordHashByUserName(userNme:str="")`

用使用者的名稱取得使用者密碼的Hash。

* userNme: 字串型別，使用者名稱。

* return: 字串型別，密碼Hash字串。

`getBalanceByUserName(userName:str="")`

用使用者名稱取得存款。

* userName: 字串型別，使用者名稱。

* return: 字串型別，存款金額。

`updateBalanceByUserName(userName:str="",newBalance:int=None)`

用使用者名稱來更新存款餘額。

* userName: 字串型別，使用者名稱。

* newBalance: 整數型別，新的貨幣餘額。

`decreaseBalanceByUserName(userName:str)`

用使用者名稱，扣款1元。

* userName: 字串型別，使用者名稱。

`getUserIDByUserName(userNme:str="")`

用使用者名稱取得使用者ID。

* userNme: 字串型別，使用者名稱。

* return: 字串型別，使用者ID。

``