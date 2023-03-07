# SMB
## smbserver
```sh
impacket-smbserver -comment 'public' -smb2support -ip <ip_to_listen> public /tmp
```

## smbclient
```sh
impacket-smbclient [[domain/]username[:password]@]<targetName or address>
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

# RDP
## Check credentials over RDP
```sh
impacket-rdp_check -hashes :<ntlm> '<domain>/<user>:@10.165.14.42'
```

# Get the PAC of the specified target user
```sh
impacket-getPac -targetUser <domain_user> -hashes :<ntlm> '<domain>/<user>:@10.165.14.42'
```
