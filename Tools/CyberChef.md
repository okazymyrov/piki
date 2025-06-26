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

# Decode decimal passwords (e.g., ms-Mcs-AdmPwd)
```
#recipe=From_Decimal('Space',false)
```

# Parse/convert an Base64 encoded certificate to PEM format
> [!NOTE]
> An example of certificate (i.e., "x5c") can be found on https://login.windows.net/common/discovery/keys
```
#recipe=From_Base64('A-Za-z0-9%2B/%3D',true,false)To_Hex('Space',0)Hex_to_PEM('CERTIFICATE')Parse_X.509_certificate('PEM')
```

# Represent the RSA modulus from an x.509 certificate in decimal format
```
#recipe=Parse_X.509_certificate('PEM')Regular_expression('User%20defined','Modulus((?::%5C%5Cs*%5B0-9a-f%5D%7B2%7D)*)',true,true,false,false,false,false,'List%20capture%20groups')Find_/_Replace(%7B'option':'Regex','string':'%5B:%5C%5Cs%5D'%7D,'',true,false,true,false)From_Base(16)
```

# Represent the RSA modulus from an Base64 encoded certificate in decimal format
```
#recipe=From_Base64('A-Za-z0-9%2B/%3D',true,false)To_Hex('Space',0)Hex_to_PEM('CERTIFICATE')Parse_X.509_certificate('PEM')Regular_expression('User defined','Modulus((?::\\s*[0-9a-f]{2})*)',true,true,false,false,false,false,'List capture groups')Find_/_Replace({'option':'Regex','string':'[:\\s]'},'',true,false,true,false)From_Base(16)
```

# Represent an Base64 encoded RSA modulus in decimal format
> [!NOTE]
> An example of certificate (i.e., "n") can be found on https://login.windows.net/common/discovery/keys
```
#recipe=From_Base64('A-Za-z0-9-_',true,false)To_Hex('None',0)From_Base(16)
```

# Represent an Base64 encoded RSA modulus in decimal format
> [!NOTE]
> Input is in PEM format.
```
#recipe=Public_Key_from_Certificate()PEM_to_Hex()Parse_ASN.1_hex_string(0,100000)Regular_expression('User%20defined','%5C%5Cb(?:%5B0-9a-fA-F%5D%7B2%7D)%7B10,%7D%5C%5Cb%5Cn',true,true,false,false,false,false,'List%20matches')From_Base(16)
```
