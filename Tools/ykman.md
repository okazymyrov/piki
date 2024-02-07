# Update the slot ```x``` with a password in the US keyboard
```powershell
& '[full_path]\ykman.exe' otp static -k US [x] $(New-Guid)
```
 
> [!NOTE]
> Cross-language symbols (NO and US) are ```!#%,.```
