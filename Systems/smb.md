# Linux
## List shares
```sh
smbclient -L <ip>
```

## Connect to remote share

### URI
```sh
smbclient //<ip>/<share>
```

### Using Administrator
```sh
smbclient -U Administrator \\\\10.129.67.254\\C$
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
