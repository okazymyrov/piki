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

## Find Domain Controllers
### PowerShell
#### Domain controllers of the logged on account
```powershell
([System.DirectoryServices.ActiveDirectory.Domain]::GetCurrentDomain()).DomainControllers
```

#### Domain controllers of the machine
```powershell
([System.DirectoryServices.ActiveDirectory.Domain]::GetComputerDomain()).DomainControllers
```

## Find LDAP servers

```batchfile
nltest /dclist:<domain>
nslookup -type=srv _ldap._tcp.dc._msdcs.<domain>
```

## ldapsearch
```sh
ldapsearch -LLL -x -H ldap://<ip> -b '' -s base '(objectclass=*)'
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

## Get Service Principal Names
```powershell
$search = New-Object DirectoryServices.DirectorySearcher([ADSI]"")
$search.filter = "(&(objectCategory=person)(objectClass=user)(servicePrincipalName=*))"
$results = $search.Findall()
foreach($result in $results)
{
	$userEntry = $result.GetDirectoryEntry()
	Write-host "User : " $userEntry.name "(" $userEntry.distinguishedName ")"
	Write-host "SPNs"        
	foreach($SPN in $userEntry.servicePrincipalName)
	{
		$SPN       
	}
	Write-host ""
}
```

## Check credentials over LDAP
```powershell
# credential format domain\username:password
$filename = "credentials.txt"
$ldap = 'LDAP://<ip>'

Get-Content $filename | ForEach-Object {
	$username = $_.split(":")[0]
	$password = $_.split(":")[1]

	if ($username[0] -ne "#")
	{
		$domain = New-Object System.DirectoryServices.DirectoryEntry($ldap,$username,$password)

		if ($domain.name -eq $null)
		{
			write-host "- $username"
		}
		else
		{
			write-host "+ $username"
		}
	}
}
```

## Find computers with enabled unconstrained delegation
```powershell
([adsisearcher]"(&(objectCategory=computer)(userAccountControl:1.2.840.113556.1.4.803:=524288))").FindAll().Properties.samaccountname
```

#  Convert password to NTLM

## Text-based password
```console
python -c "import hashlib,binascii; print (binascii.hexlify(hashlib.new('md4', '<password>'.encode('utf-16le')).digest()))"
```

# [Kerberos cheatsheet](./KerberosAttacksCheatsheet.md)

#  The credentials specified are for remote access only
```batchfile
runas /netonly /user:<domain>\<user> cmd.exe
net view \\<dc>.<domain.local>\
```

# [Displays the Resultant Set of Policy (RSoP)](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/gpresult)

## Displays RSoP summary data for the current user
```batchfile
gpresult /R
```

## Displays RSoP summary data for the current user and saves the report in HTML format
```batchfile
gpresult /H .\Downloads\gpresult.mxq.html
```
