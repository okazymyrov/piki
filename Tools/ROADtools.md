# [Installation](https://github.com/dirkjanm/ROADtools)
## Windows
```console
pip install roadrecon
pip install roadtx
REM Add Python scripts to PATH
REM For example, %USERPROFILE%\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.10_qbz5n2kfra8p0\LocalCache\local-packages\Python310\Scripts
```

# [ROADtools Token eXchange (roadtx)](https://github.com/dirkjanm/ROADtools/wiki/ROADtools-Token-eXchange-(roadtx))
## Use a refresh token to request a token for the Microsoft Graph
```console
roadtx gettokens --refresh-token "<token>" -r msgraph
```
