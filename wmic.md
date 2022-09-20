# Get SIDs of domains
```console
wmic group where name="Domain Admins" get name,sid,domain
```

# List antimalware solutions
```console
wmic /namespace:\\root\SecurityCenter2 path AntiVirusProduct get * /value
```
