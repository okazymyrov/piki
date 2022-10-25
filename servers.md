# Simple Python 3.X server
```sh
python3 -m http.server 8000
```

# Simple Python 2.X server
```sh
python -m SimpleHTTPServer 8000
```

# Simple npm server via npx
```sh
npx http-server -p 8000
```

# [Reverse VNC](https://blog.kennyjansson.com/2018/03/04/reverse-vnc-shell/)
## Server - Linux
```sh
vncviewer -listen 0
```

## Client - Windows
```batchfile
# https://www.tightvnc.com/download.php
# the file can be unpacked from MSI using 7z
tvnserver.exe
tvnserver.exe -controlservice -connect <linux_ip>:5500
```
