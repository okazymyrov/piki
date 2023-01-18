# ZIP files
## Extract hashes from a zip file
```sh
zip2john <zip> > <zip_hash.txt>
```
## Crack 
```sh
john --wordlist=/usr/share/wordlists/rockyou.txt <zip_hash.txt>
```
