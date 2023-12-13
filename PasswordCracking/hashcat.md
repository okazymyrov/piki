# Dictionaries
- https://weakpass.com/
- [password_cracking_rule](https://github.com/NotSoSecure/password_cracking_rules)
- [OneRuleToRuleThemStill.rule](OneRuleToRuleThemStill.rule)

# Kerberoasting
```sh
hashcat --session=kerb -m13100 -a 0 [path to hashes] /usr/share/wordlists/rockyou.txt
```

# NTLM
```sh
hashcat --session=ntlm -m1000 -a 0 [path to hashes] /usr/share/wordlists/rockyou.txt -r OneRuleToRuleThemAll.rule
```

# NTLMv2
```sh
hashcat --session=ntlmv2 -m5600 -a 0 [path to hashes] /usr/share/wordlists/rockyou.txt 
```

# MD5
```sh
hashcat --session=md5 -m0 -a 0 [path to hashes] /usr/share/wordlists/rockyou.txt 
```

# Restore a session
```sh
hashcat --session=[name] --restore
```

# Show username, hash and password
```sh
# NTLM
hashcat -m1000 [path to hashes] --username --show
```
