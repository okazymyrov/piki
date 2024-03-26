# Check a user in Microsoft tenant

## GET
```
https://login.microsoftonline.com/getuserrealm.srf?login=[username]@[domain]&xml=1
```

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
