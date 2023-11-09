# Use MSTSC as in the shadow mode

## Get Session ID
```batch
query session /server:[server]
```

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
