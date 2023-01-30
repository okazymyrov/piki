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
# rdp client connets to localhost:13389
```

# SSH
## Reverse SSH tunnel
```sh
```
