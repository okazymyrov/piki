# References
* [UberGuidoZ - Flipper](https://github.com/UberGuidoZ/Flipper)

# Bad USB
## Overwrite input layout with en-US
```powershell
$OldList = Get-WinUserLanguageList
Set-WinUserLanguageList -Force -LanguageList (New-WinUserLanguageList -Language en-US)
Set-WinUserLanguageList -Force -LanguageList $OldList
```

## References
* [Flipper Zero Bad USB](https://docs.flipperzero.one/bad-usb)
* [I-Am-Jakoby - Flipper Zero BadUSB](https://github.com/I-Am-Jakoby/Flipper-Zero-BadUSB)
* [UNC0V3R3D - The Ultimate Flipper Zero Badusb Collection](https://github.com/UNC0V3R3D/Flipper_Zero-BadUsb)
* [Flipper Zero Bad USB hack5 payloads](https://github.com/nocomp/Flipper_Zero_Badusb_hack5_payloads)
