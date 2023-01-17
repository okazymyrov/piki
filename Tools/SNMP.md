# snmpwalk
```console
snmpwalk -v1 -c public <ip>
```

# nmap
```console
nmap -p161 -sU -sC <ip>
```

# Get MAC address for all interfaces
```console
snmpwalk -v1 -c public <ip> iso.3.6.1.2.1.2.2.1.6
```
