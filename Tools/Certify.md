# [Find information about all registered CAs](https://github.com/GhostPack/Certify#usage)
```batchfile
Certify.exe cas /domain:<domain> /hideAdmins /showAllPermissions /skipWebServiceChecks
```
# Find vulnerable certificate templates via domain name:
```batchfile
Certify.exe find /domain:<domain> /vulnerable
```

# Find vulnerable certificate templates using an LDAP server:
```batchfile
Certify.exe find /ldapserver:<server.domain.local> /vulnerable
```

