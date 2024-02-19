# [Installation](https://github.com/dirkjanm/ROADtools)
## Windows
```batch
pip install roadrecon
pip install roadtx
REM Add Python scripts to PATH
REM For example, %USERPROFILE%\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.10_qbz5n2kfra8p0\LocalCache\local-packages\Python310\Scripts
```

>[!NOTE]
> Per **19.02.24**, Windows Store can be launched from
> ```
> C:\Program Files\WindowsApps\Microsoft.WindowsStore_22312.1401.5.0_x64__8wekyb3d8bbwe
> ```

# [ROADtools Token eXchange (roadtx)](https://github.com/dirkjanm/ROADtools/wiki/ROADtools-Token-eXchange-(roadtx))
## Use a refresh token to request a token for the Microsoft Graph
```sh
roadtx gettokens --refresh-token "[token]" -r msgraph
```
