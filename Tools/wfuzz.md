# Brute force vhosts
```sh
wfuzz -c -f subdomains.txt -w /usr/share/wordlists/seclists/Discovery/DNS/subdomains-top1million-5000.txt -u "<url>" -H "Host: FUZZ.<domain>"
```
