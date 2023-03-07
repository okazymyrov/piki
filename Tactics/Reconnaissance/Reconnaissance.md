# Ping 10.0.0.0/8 and return all available routers (assuming that x.1 is a router)
```sh
masscan  --rate 1000000 --ping -oG ./10.x.x.x.8 10.0.0.0/8
cat ./10.x.x.x.8 | grep "Timestamp" | cut -d " " -f 3 | grep -e "\.1$" | sort
```

# Find live network devices and the corresponding MACs (unprivileged scanning)
```batchfile
FOR /L %i IN (1,1,254) DO @ping -n 1 -w 20 10.0.0.%i | FIND /i "TTL"
arp -a
```

# Check a user in Microsoft tenant
```
https://login.microsoftonline.com/getuserrealm.srf?login=user@<example.com>&xml=1
```

# [SpideFoot](https://github.com/smicallef/spiderfoot)
