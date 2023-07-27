# SSH
## Test for weak SSH RSA keys
```sh
ssh-keyscan -t rsa [ip] | sed "s/^[^ ]* //" > /tmp/[ip].pub
ssh-keygen -e -m pem -f /tmp/[ip].pub > /tmp/[ip].pem
./RsaCtfTool.py --publickey /tmp/[ip].pem
```
