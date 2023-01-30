# Cloudflare Tunnel client
## HTTP Tunnel
```sh
./cloudflared tunnel --url http://localhost:8000
```

## HTTPS Tunnel
```sh
./cloudflared tunnel --no-tls-verify --url https://<url>/
```

## RDP tunnel
```sh
# jump server
./cloudflared tunnel --no-tls-verify --url rdp://<target_rdp_server>:3389
# client
./cloudflared access rdp --hostname <url_from_the_previous_command> --url rdp://localhost:13389
# connect to localhost:13389 in an rdp client
```

## SMB tunnel
```sh
# jump server
cloudflared.exe tunnel --url smb://<sever_with_smb_share>:445
# client
cloudflared.exe access tcp --hostname rainbow-alignment-risk-harold.trycloudflare.com --url localhost:8445
# connect to smb://localhost:8445 in an smb client
```

# SSH
## Reverse SSH tunnel
```sh
```
