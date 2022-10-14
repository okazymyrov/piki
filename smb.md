# Linux
## List shares
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

## Execute commands over SMB
```sh
smbmap -u '<user>' -p '<password>' -H <ip> -x 'command "path" <options>'
```

## Recursively download a file share
```sh
smbget --user=guest -R smb://<ip>/<share>/
```

# Windows

## List shares
```batchfile
net view \\<ip> /all
```
