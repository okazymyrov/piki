# Dictionaries
- https://weakpass.com/
- [OneRuleToRuleThemStill](https://github.com/stealthsploit/OneRuleToRuleThemStill)
- [password_cracking_rule (replaced by OneRuleToRuleThemStill)](https://github.com/NotSoSecure/password_cracking_rules)

# Kerberoasting
```sh
hashcat --session=kerb -m13100 -a0 [path to hashes] /usr/share/wordlists/rockyou.txt
```

# NTLM
```sh
hashcat --session=ntlm -m1000 -a0 [path to hashes] /usr/share/wordlists/rockyou.txt -r OneRuleToRuleThemAll.rule
```

# NTLMv2
```sh
hashcat --session=ntlmv2 -m 5600 -a 0 [path to hashes] /usr/share/wordlists/rockyou.txt 
```

# MD5
```sh
hashcat --session=md5 -m 0 -a 0 [path to hashes] /usr/share/wordlists/rockyou.txt 
```

# PDF
```sh
# ./pdf2hashcat.py ./file.pdf > [path to hashes]
hashcat --session=md5 -m 10500 -a 3 [path to hashes] ?d?d?d?d?d
```


# Restore a session
```sh
hashcat --session=<name> --restore
```

# Show username, hash and password
```sh
# NTLM
hashcat -m1000 [path to hashes] --username --show
```
