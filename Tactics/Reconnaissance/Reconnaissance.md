# Check if a domain exists in a Microsoft 365 tenant

## GET
```
https://login.microsoftonline.com/getuserrealm.srf?login=[domain]&xml=1
```

# Check a user in Microsoft tenant

## POST
```python
import requests
body = '{"Username":"[username]@[domain]"}'
response = requests.post("https://login.microsoftonline.com/common/GetCredentialType", data=body).json()
if response["IfExistsResult"] == 0:
    print("Valid User")
```

# [MFASweep](https://github.com/dafthack/MFASweep)
```powershell
Invoke-MFASweep -Username <username> -Password <password> -Recon -IncludeADFS
```

# [SpideFoot](https://github.com/smicallef/spiderfoot)

# [TeamsEnum](https://github.com/lucidra-security/TeamsEnum)
