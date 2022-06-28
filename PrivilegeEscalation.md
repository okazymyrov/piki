# Unquoted Service Paths

## WMIC
```batchfile
cmd /c wmic service get name,displayname,pathname,startmode |findstr /i "auto" |findstr /i /v "c:\windows\\" |findstr /i /v """
```

## PowerShell
```powershell
$result = $null
$result = Get-WmiObject win32_service | Where-Object {($_.PathName -like '* *') -and ($_.PathName -notlike '*"*') -and ($_.PathName -notlike '*C:\Windows*')} | ForEach-Object { Write $_.PathName }
if ($result -ne $null) { Write $result | Sort -Unique } else { Write "Weak services were not found." }
```

## Specific service
```batchfile
sc qc "<service name>"
```

