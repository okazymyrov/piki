# WinRM
## Brute force users and passwords
```sh
crackmapexec winrm -u [username_or_file] -p [password_or_file] [ip]
```

# SMB
## Execute CMD commands
```sh
crackmapexec smb [-d DOMAIN | --local-auth] -u [user] -p [password] -x 'dir "C:\Users\*.txt" /s' [ip]
```
