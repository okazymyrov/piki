# Set a Wi-Fi card into monitor mode
```sh
ip link set wlan0 down
airmon-ng check kill
iw dev wlan0 set monitor control
ip link set wlan0 up
```

## Adding a new interface may resolve some errors.
> [!NOTE]  
> [Capturing Wireless LAN Packets in Monitor Mode with iw](https://sandilands.info/sgordon/capturing-wifi-in-monitor-mode-with-iw)
```sh
iw phy phy0 interface add mon0 type monitor
iw dev wlan0 del
ip link set mon0 up
```

# Monitor a specific ESSID
```sh
airodump-ng --essid "<name>" --wps --band abg --manufacture --berlin 3600 -c64,100 -f 2000 -a wlan0
```

# Manually capturing wireless LAN packets
```sh
iw dev mon0 set freq 2437
tcpdump -i mon0 -n -w wireless.cap
```
Supported frequencies and their corresponding values can be found by
```sh
iw phy | grep "MHz \["
```

# Change country
Get the current setup
```sh
iw reg get
```
Set new country
```sh
iw reg set JP
```

# [Discover APs using bettercap](https://github.com/okazymyrov/piki/blob/master/Tools/bettercap.md#discover-aps)

# Hijack an IP address using a MAC address
```sh
ip link set wlan0 down
# macchanger -m [hijacked MAC] wlan0
ip link set dev wlan0 address [hijacked MAC]
ip link set wlan0 up
dhclient wlan0
```
## One-liner
```sh
ip link set wlan0 down; ip link set dev wlan0 address [hijacked MAC]; ip link set wlan0 up; dhclient wlan0
```
