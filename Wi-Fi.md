# Set a Wi-Fi card into monitor mode

```
ip link set wlan0 down
airmon-ng check kill
iw dev wlan0 set monitor control
ip link set wlan0 up
```

Adding a new interface may resolve some errors ([Capturing Wireless LAN Packets in Monitor Mode with iw](https://sandilands.info/sgordon/capturing-wifi-in-monitor-mode-with-iw)).
```
iw phy phy0 interface add mon0 type monitor
iw dev wlan0 del
ip link set mon0 up
```

# Manually capturing wireless LAN packets
```
iw dev mon0 set freq 2437
tcpdump -i mon0 -n -w wireless.cap
```
Supported frequencies and their corresponding values can be found by
```
iw phy | grep "MHz \["
```

# Change country
Get the current setup
```
iw reg get
```
Set new country
```
iw reg set JP
```
