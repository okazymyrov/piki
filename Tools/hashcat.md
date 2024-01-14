# Dictionaries
- [WEAKPASS](https://weakpass.com/)
- [OneRuleToRuleThemStill.rule](https://github.com/stealthsploit/OneRuleToRuleThemStill)
- [OneRuleToRuleThemAll.rule (replaced by OneRuleToRuleThemStill)](https://github.com/NotSoSecure/password_cracking_rules)

# Kerberoasting
```sh
hashcat --session=kerb -m13100 -a0 [path to hashes] /usr/share/wordlists/rockyou.txt
```

# NTLM
```sh
hashcat --session=ntlm -m1000 -a0 [path to hashes] /usr/share/wordlists/rockyou.txt -r OneRuleToRuleThemStill.rule
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
<details><summary>How do you get the hash from a PDF?</summary>
<p>

* [pdf2hashcat.py](https://github.com/stricture/hashstack-server-plugin-hashcat/blob/master/scrapers/pdf2hashcat.py)

```sh
./pdf2hashcat.py ./file.pdf > [path to hashes]
```

</p>
</details>

```sh
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

# System configuration

## Show system/evironment/backend API info
```sh
hashcat -I
```

## Manual compilation to support GPU on macOS
```sh
git clone https://github.com/hashcat/hashcat.git
mkdir -p hashcat/deps
git clone https://github.com/KhronosGroup/OpenCL-Headers.git hashcat/deps/OpenCL
cd hashcat/ && make
./hashcat --version
./hashcat -b -d [1] -m 1000
```
