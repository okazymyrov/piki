# smbserver
```sh
impacket-smbserver -comment 'public' -smb2support -ip <ip_to_listen> public /tmp
```

# Interact with MSSQL server
## With Windows credentials
```sh
impacket-mssqlclient -port <port> -windows-auth <domain>/<user>:<password>@<ip>
```

## Without Windows credentials
```sh
impacket-mssqlclient -port <port> <user>:<password>@<ip>
```

## Enable xp_cmdshell
```sh
enable_xp_cmdshell 1
```
