# Get SIDs of domains
```batchfile
wmic group where name="Domain Admins" get name,sid,domain
```

# List antimalware solutions
```batchfile
wmic /node:localhost /namespace:\\root\SecurityCenter2 path AntiVirusProduct get * /value
```

# Execute commands on remote computer
```batchfile
wmic /node:<computer>.<domain.local> process call create "powershell.exe -Command "ipconfig; systeminfo"
```
