# Linux
## Listen shares
```sh
smbclient -L 10.129.68.132
```

## Recursively download a file share
```sh
smbget --user=guest -R smb://<ip>/share/
```
