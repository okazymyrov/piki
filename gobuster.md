# Brute force directories
```sh
gobuster dir -u <domain or ip> -w /usr/share/wordlists/dirbuster/directory-list-1.0.txt
```
# Search for specific file extensions in all directories
```sh
gobuster dir -x ".php" -u <domain or ip> -w /usr/share/wordlists/dirb/common.txt
```
