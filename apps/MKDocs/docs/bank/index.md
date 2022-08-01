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

[/](http://127.0.0.1:8080/) ***GET方法***，提供銀行端前端頁面，由於過往使用flask預設的`Jinja2`模板引擎。

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
    
}
```