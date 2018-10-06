/bin/firewall-cmd --zone=public --add-port=80/tcp

/usr/bin/certbot renew --quiet --no-self-upgrade

/bin/cp /ect/letsencrypt/live/example.com/fullchain.pem /home/apie/workspace/shoppingbot/app/cert.pem

/bin/cp /ect/letsencrypt/live/example.com/cert.pem /home/apie/workspace/shoppingbot/app/key.pem

/bin/docker-compose restart

/bin/firewall-cmd --zone=public --remove-port=80/tcp
