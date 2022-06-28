# In case of issues with TLS
```powershell
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
```


# Download a script from an HTTP server
```powershell
iex(New-Object Net.WebClient).DownloadString('https://raw.githubusercontent.com/microsoft/ExPerfAnalyzer/main/ExPerfAnalyzer.ps1')
```
