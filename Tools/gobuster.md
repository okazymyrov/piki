# Brute force directories
```sh
gobuster dir -u <domain or ip> --threads 100  --delay 500ms -w /usr/share/wordlists/dirbuster/directory-list-2.3-small.txt -o /tmp/gobuster_dir.txt
```
# Search for specific file extensions in all directories
```sh
gobuster dir -x ".php" -u <domain or ip> --threads 100  --delay 500ms -w /usr/share/wordlists/dirb/common.txt -o /tmp/gobuster_dir_file.txt
```
# Bruteforce subdomains based on vhost
```sh
gobuster vhost -u http(s)://<ip> --domain <domain_to_append> --threads 100  --delay 500ms --append-domain --random-agent -w /usr/share/wordlists/seclists/Discovery/DNS/subdomains-top1million-20000.txt -o /tmp/gobuster_vhost.txt
```
