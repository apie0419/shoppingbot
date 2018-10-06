## A ShoppingBot on Line Platform

### How To Run Service

#### 進入工作資料夾

```
cd shoppingbot
```

#### 建立 Bot Server 的 Image

```
sudo docker build -t="bot" .
```

#### 開啟 Service(背景執行)

```
sudo docker-compose up -d
```

### How to Get SSL Certificate

**必須要有 Domain Name 才能申請，因為 Line 需要第三方認證的SSL，若不需要可以考慮使用 openssl 就沒有 Domain Name 的限制**

#### Step 1 - Download certbot

Reference : https://certbot.eff.org/

#### Step 2 - Create Configuration

example.com 是 Domain Name

```
sudo mkdir /etc/letsencrypt/configs
sudo vim /etc/letsencrypt/configs/example.com.conf
```

example.com.conf

Reference : https://certbot.eff.org/docs/using.html#certbot-command-line-options

```
domains = example.com
email = your-email@example.com
rsa-key-size = 2048
text = True


authenticator = standalone //有其他模式可以選，standalone mode 是在我們沒有用 nginx, apache 等架站軟體時使用的模式
```

#### Step3 - Create Certificate

記得先將防火牆 80 port 開啟，因為certbot需要透過 80 port 自己開啟連結來確認 Domain Name 是否屬於這台機器，因此要在真正使用這個 Domain Name 的機器上註冊

```
sudo certbot -c /etc/letsencrypt/configs/example.com.conf certonly
```

完成後即可在 /etc/letsencrypt/live/example.com/ 下看到證書
若不能進入資料夾，要先將資料夾權限更改

```
sudo chmod 755 /etc/letsencrypt/live/
```

#### Step4 - Copy Certificate

```
cp /etc/letsencrypt/live/example.com/fullchain.pem shoppingbot/app/cert.pem
cp /etc/letsencrypt/live/example.com/privatekey.pem shoppingbot/app/key.pem
```

完成後記得將 /etc/letsencrypt/live/example.com/ 權限設定回去

```
sudo chmod 700 /etc/letsencrypt/live/
```

#### Step5 - Auto Renew Certificate

因為 Certbot 的證書只有 3個月 因此要設定自動更新

```
sudo crontab -e
```

輸入

```
* * * * */2 /bin/sh route/shoppingbot/app/update_certificate.sh (route 替換為放 shopping 的路徑)
```