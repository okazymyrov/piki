# References
1. [RsaCtfTool](https://github.com/RsaCtfTool/RsaCtfTool)

# SSH
## Test for weak SSH RSA keys
```sh
ssh-keyscan -t rsa [ip] | sed "s/^[^ ]* //" > /tmp/[ip].pub
ssh-keygen -e -m pem -f /tmp/[ip].pub > /tmp/[ip].pem
./RsaCtfTool.py --publickey /tmp/[ip].pem
```

# x509
```sh
# openssl x509 -inform DER -in [path_to_certificate].der -out [path_to_certificate].pem
python RsaCtfTool.py --publickey [path_to_certificate] --private > [path_to_recovered_key]
```
