# Ping 10.0.0.0/8 and return all routers available (assuming that x.1 is a router)
```console
masscan  --rate 1000000 --ping -oG ./10.x.x.x.8 10.0.0.0/8
cat ./10.x.x.x.8 | grep "Timestamp" | cut -d " " -f 3 | grep -e "\.1$" | sort
```
