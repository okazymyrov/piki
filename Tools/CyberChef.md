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
