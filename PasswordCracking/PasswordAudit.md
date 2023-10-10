# [Extract password from NTDS.dit](/Systems/NTDS.dit.md)

# Check NTLM hashes agains The Pwned Passwords list
- [The Pwned Passwords list - NTLM (ordered by hash)](https://haveibeenpwned.com/Passwords)
```sh
cut -d ":" -f "4" ./ntlm.txt | tr '[:lower:]' '[:upper:]' > ./t; mv ./t ./ntlm.txt # ntlm.txt is in the hashcat format
cut -d ":" -f "1" ./pwned-passwords-ntlm-ordered-by-hash-v8.txt > ./t; mv ./t ./pwned-passwords-ntlm-ordered-by-hash-v8.txt
```

## hashcat
```sh
hashcat --session=password_audit --potfile-path=./password.audit.potfile -m 99999 --outfile=./ntlm.hibp.txt -a 0 ./ntlm.txt ./pwned-passwords-ntlm-ordered-by-hash-v8.txt
```
## grep
```sh
grep -xFf ./ntlm.txt ./pwned-passwords-ntlm-ordered-by-hash-v8.txt > ./ntlm.hibp.grep.txt
```

# [DPAT](https://github.com/clr2of8/DPAT)
## Perform a domain password audit
```sh
./dpat.py -n ./ntlm.txt -c /home/kali/.local/share/hashcat/hashcat.potfile -d password_audit
```

## Sanitize the report by partially redacting passwords and hashes
```sh
./dpat.py -n ./ntlm.txt -c /home/kali/.local/share/hashcat/hashcat.potfile -d password_audit -s
```

## Include machine accounts
```sh
./dpat.py -n ./ntlm.txt -c /home/kali/.local/share/hashcat/hashcat.potfile -d password_audit -m
```

## Include the krbtgt account
```sh
./dpat.py -n ./ntlm.txt -c /home/kali/.local/share/hashcat/hashcat.potfile -d password_audit -k
```
