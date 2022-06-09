# Trust
## CMD
```batchfile
nltest /trusted_domains
```
## PowerShell
### Domain
```powershell
([System.DirectoryServices.ActiveDirectory.Domain]::GetCurrentDomain()).GetAllTrustRelationships()
```
### Forest
```powershell
([System.DirectoryServices.ActiveDirectory.Forest]::GetCurrentForest()).GetAllTrustRelationships()
```

# LDAP

## Find LDAP servers
```batchfile
nltest /dclist:<domain>
nslookup -type=srv _ldap._tcp.dc._msdcs.<domain>
```

## Connection to a LDAP server with custom credentials 
```powershell
$ip=<ip of a DC>
$credential = Get-Credential -Credential "<domain>\<user>"
$domaininfo = new-object DirectoryServices.DirectoryEntry("LDAP://$ip",$($credential.UserName),$($credential.GetNetworkCredential().password))
$searcher = New-Object System.DirectoryServices.DirectorySearcher($domaininfo)
$searcher.filter = <filter>
$searcher.FindAll()
```

## Get-SamAccountName
```powershell
$SAMAccountName=<user>
$searcher.filter = "(&(objectClass=User)(sAMAccountName=$SAMAccountName))"
$searcher.findAll().Properties
```
## LAPS Passwords
```powershell
$searcher.filter = "(ms-Mcs-AdmPwd=*)"
$searcher.findAll().Properties
```

## Nested Group Membership
```powershell
$searcher.filter = "(memberOf:1.2.840.113556.1.4.1941:=cn=Domain Admins,cn=Users,dc=example,dc=com)"
$searcher.FindAll()
```
