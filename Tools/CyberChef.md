# User password to NTLM

```
#recipe=Encode_text('UTF-16LE%20(1200)')MD4()
```

# Machine password (hex) to NTLM
```
#recipe=From_Hex('Auto')MD4()
```

# Microsoft TOTP
```
#recipe=To_Upper_case('All')From_Base32('A-Z2-7%3D',true)Generate_TOTP('',32,6,0,30)&input=eHB2bjJycm1qcG5idm5qaw
```

# English text in Greek letters
```
#recipe=To_Lower_case()Substitute('abdefiklmnopstuvwxyz','αβδεφικλμηορςτυνωχγζ')&input=cGVudGVzdCB3aWtp
```

# Decrypt the administrator password for a running Windows instance 
```
#recipe=From_Base64('A-Za-z0-9%2B/%3D',true,false)RSA_Decrypt('-----BEGIN RSA PRIVATE KEY-----','','RSAES-PKCS1-V1_5','SHA-1')
```

<details><summary>How to retrieve the encrypted administrator password?</summary>
<p>

In AWS CloudShell:
```sh
ii="i-..." # The ID of the Windows instance 
aws ec2 get-password-data --instance-id ${ii} | jq .PasswordData
```

</p>
</details>
