# Linux
## Listen shares
```sh
smbclient -L <ip>
```

## Connect to remote share
```sh
smbclient //<ip>/<share>
```

## Samba share enumerator
```sh
smbmap -u guest -d workgroup -H <ip>
```

## Recursively download a file share
```sh
smbget --user=guest -R smb://<ip>/<share>/
```
