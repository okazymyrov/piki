![image](https://github.com/okazymyrov/piki/assets/1721372/b58b28eb-aefb-4707-84fb-5e7591f0728a)# User password to NTLM

```
#recipe=Encode_text('UTF-16LE%20(1200)')MD4()
```

# Machine password (hex) to NTLM
```
#recipe=From_Hex('Auto')MD4()
```

# Microsoft TOTP
```
#recipe=To_Upper_case('All')From_Base32('A-Z2-7%3D',true)Generate_TOTP('',32,6,0,30)
```

# English text in Greek letters
```
#recipe=To_Lower_case()Substitute('abdefiklmnopstuvwxyz','αβδεφικλμηορςτυνωχγζ')
```

# Decrypt the administrator password for a running Windows instance in AWS
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

# Encode powershell code to Base64
```
#recipe=Encode_text('UTF-16LE (1200)')To_Base64('A-Za-z0-9%2B/%3D')
```

# Decode Base64 to powershell code
```
#recipe=From_Base64('A-Za-z0-9%2B/%3D',true,false)Decode_text('UTF-16LE (1200)')
```

# Decode $HEX[] (hashcat output) to UTF-8
```
#recipe=Fork('\\n','\\n',false)Find_/_Replace({'option':'Simple string','string':'$HEX['},'',true,false,true,false)Find_/_Replace({'option':'Simple string','string':']'},'',true,false,true,false)From_Hex('None')
```

# Decode Decimal passwords (e.g., ms-Mcs-AdmPwd)
```
#recipe=From_Decimal('Space',false)&input=ODAgOTcgMTE1IDExNSAxMTkgMTExIDExNCAxMDAgNDkgNTAgNTE
```

