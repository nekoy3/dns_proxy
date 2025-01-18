# dns_proxy
受け取った dns リクエストクエリを複数の upstream サーバにそのまま送信し、 dns 回答クエリを受け取ったら、最も早かったクエリを問い合わせ元に応答する DNS プロキシサーバ。
稼働版は multithread 版のほう

## バグの可能性
毎秒 100 クエリとかの頻度でやり取りを行うと、 SERVFAIL が群発することがある気がする。
状況を再現させてみたいところ

## おしえてAIさん
```
https://github.com/nekoy3/dns_proxy/blob/main/dns_multithread_proxy.py
このコードを実行したところ、SERVFAILが群発することがあるのはなぜか。

予想では、大量のクエリを実行した時、非同期のズレで、リクエストクエリを送信したのに、リクエストクエリが返ってくるとか、トランザクションIDのズレとかかなと思っているが
```
![image](https://github.com/user-attachments/assets/813f70c1-a016-4ca8-988c-1b33d4adf9fd)
![image](https://github.com/user-attachments/assets/babfad32-823d-4dec-848b-ef3a5d5c2a6a)
![image](https://github.com/user-attachments/assets/a5577328-b67d-4ef4-9c96-71ec52357be0)
