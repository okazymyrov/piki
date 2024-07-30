# Simple HTTPS Python 3.X server
```python
# sudo python3
from http.server import HTTPServer, SimpleHTTPRequestHandler
import ssl, os
os.system("openssl req -nodes -x509 -newkey rsa:2048 -keyout /tmp/key.pem -out /tmp/cert.pem -days 365 -subj '/CN=mylocalhost'")
port = 443
httpd = HTTPServer(('0.0.0.0', port), SimpleHTTPRequestHandler)
httpd.socket = ssl.wrap_socket(httpd.socket, keyfile='/tmp/key.pem', certfile="/tmp/cert.pem", server_side=True)
print(f"Server running on https://0.0.0.0:{port}")
httpd.serve_forever()
```

# Simple HTTP Python 3.X server
```sh
python3 -m http.server 8000
```

# Simple HTTP Python 2.X server
```sh
python -m SimpleHTTPServer 8000
```

# Simple HTTP npm server via npx
```sh
npx http-server -p 8000
```

# A PowerShell Server to return the Authorization header
```powershell
$http = [System.Net.HttpListener]::new() 
$http.Prefixes.Add("http://localhost:10080/")
$http.Start()
$context = $http.GetContext()
write-host $context.Request.Headers.GetValues("Authorization")
$buffer = [System.Text.Encoding]::UTF8.GetBytes($context.Request.Headers.GetValues("Authorization"))
$context.Response.ContentLength64 = $buffer.Length
$context.Response.OutputStream.Write($buffer, 0, $buffer.Length)
$context.Response.OutputStream.Close()
```

# [Reverse VNC](https://blog.kennyjansson.com/2018/03/04/reverse-vnc-shell/)
## Server - Linux
```sh
vncviewer -listen 0
```

## Client - Windows
```batchfile
:: https://www.tightvnc.com/download.php
:: the file can be unpacked from MSI using 7z
tvnserver.exe
:: cmd /c tvnserver
tvnserver.exe -controlapp -connect <linux_ip>:5500
```

# [Golang Echo Server](https://github.com/ibihim/echo-server)
```batchfile
git clone https://github.com/ibihim/echo-server
cd echo-server
go build
```
