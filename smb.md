# Linux
## Listen shares
```sh
smbclient -L <ip>
```

## Samba share enumerator
```sh
smbmap -u guest -d workgroup -H <ip>
```

## Recursively download a file share
```sh
smbget --user=guest -R smb://<ip>/share/
```
