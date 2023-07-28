# Prerequsite
 1. DNS record for [domain]
 2. Open HTTP port for [domain]

# Reqest certificate
```sh
certbot certonly --non-interactive --agree-tos --email [e-mail] --standalone --preferred-challenges http -d [domain]
```

# Revoke certificate
```sh
certbot revoke --cert-path /etc/letsencrypt/archive/[domain]/cert1.pem
```