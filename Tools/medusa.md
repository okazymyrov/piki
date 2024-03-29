# List all modules
```sh
medusa -d
```

# Display module options
```sh
medusa -M ssh -q
```

# NTLM brute force
```sh
# -s: Enable SSL
# -t: Total number of logins to be tested concurrently
# -b: Suppress startup banner
medusa -h "<domain/host>" -s -U <file_with_users> -P <file_with_passwords> -M http -m AUTH:NTLM -m USER-AGENT:"<modern_user_agent>" -m DIR:"<directory>" -m DOMAIN:"<domain_of_users>" -t 10 -b -O <output_files>
```

# Brute force usernames and passwords over FTP
```sh
# -f: Stop scanning host after first valid username/password found.
medusa -h <ip> -U <path_to_usernames> -P <path_to_passwords> -M ftp -n <port> -e ns -f -t 4
```

# Brute force usernames and passwords over web forms
```sh
# -s: Enable SSL
medusa -h <ip> -U <path_to_usernames> -P <path_to_passwords> -n <port> -e ns -M web-form -m FORM:"/login.php" -m DENY-SIGNAL:"Incorrect information" -m FORM-DATA:"POST?Username=&Password=&Submit=Login"
```
