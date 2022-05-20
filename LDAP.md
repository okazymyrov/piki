# General
```powershell
$root = [ADSI]''
$searcher = New-Object -TypeName System.DirectoryServices.DirectorySearcher -ArgumentList ($root)
$searcher.filter = "(&(objectClass=User)(sAMAccountName=$SAMAccountName))"
```

# Get-SamAccountName
```powershell
function Get-SamAccountName
{
  param($SAMAccountName)

  $root = [ADSI]''
  $searcher = New-Object -TypeName System.DirectoryServices.DirectorySearcher -ArgumentList ($root)
  $searcher.filter = "(&(objectClass=User)(sAMAccountName=$SAMAccountName))"
  return $searcher.findAll().Properties
}

Get-SamAccountName -SAMAccountName <username>
```
# LAPS Passwords
```
$root = [ADSI]''
$searcher = New-Object -TypeName System.DirectoryServices.DirectorySearcher -ArgumentList ($root)
$searcher.filter = "(ms-Mcs-AdmPwd=*)"
$searcher.findAll().Properties
```
