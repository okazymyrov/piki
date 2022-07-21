# Dictioaries
- https://weakpass.com/
- [password_cracking_rule](https://github.com/NotSoSecure/password_cracking_rules)
- [OneRuleToRuleThemAll.rule](https://raw.githubusercontent.com/okazymyrov/piki/master/OneRuleToRuleThemAll.rule)

# Kerberoasting
```sh
hashcat --session=kerb -m13100 -a 0 <path to hashes> /usr/share/wordlists/rockyou.txt
```

# NTLM
```sh
hashcat --session=ntlm -m1000 -a 0 <path to hashes> /usr/share/wordlists/rockyou.txt -r OneRuleToRuleThemAll.rule
```

# NTLMv2
```sh
hashcat --session=ntlmv2 -m5600 -a 0 <path to hashes> /usr/share/wordlists/rockyou.txt 
```

# Restore a session
```sh
hashcat --session=<name> --restore
```

# Show username, hash and password
```sh
hashcat -m1000 <path to hashes> --username --show
```
