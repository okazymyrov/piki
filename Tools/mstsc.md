# Use MSTSC as in the shadow mode

## [Get Session ID](https://github.com/okazymyrov/piki/blob/master/Tools/cmd.md#get-a-list-of-logged-user-sessions-from-a-remote-computer)

## Initiate Remote Connection
⚠️ require elevated 

### View mode
```batch
mstsc /v:[server] /shadow:[ID]
```

### Control mode
```batch
mstsc /v:[server] /shadow:[ID] /control
```
