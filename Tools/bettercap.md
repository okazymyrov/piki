# Wi-Fi

> [!IMPORTANT]  
> Please use [the native method](https://github.com/okazymyrov/piki/blob/master/Systems/Wi-Fi.md#set-a-wi-fi-card-into-monitor-mode) to enable monitore mode since airmon-ng may cause errors in bettercap.
> to enable monitor mode as airmon-ng may cause errors in bettercap.

## References
* [Bettercap - Wi-Fi](https://www.bettercap.org/modules/wifi/)

## Discover APs and capture handshakes/PMKID
```
sudo bettercap
set wifi.interface wlan0
wifi.recon on
wifi.show
```

## Comma separated list of channels to hop on
```
wifi.recon.channel 1,6,11,100
```

## wifi.show

> [!NOTE]
> Show current wireless stations list (default sorting by RSSI)

### Clear our view and present an updated list of nearby Wi-Fi networks
```
set ticker.commands 'clear; wifi.show'
ticker on
```

### Defines a regular expression filter for wifi.show
```
set wifi.show.filter ^Berlin
```

### Defines sorting field and direction for wifi.show
```
set wifi.show.sort clients desc
```

# Bluetooth (BLE)

## References
* [Bettercap - Bluetooth LE](https://www.bettercap.org/modules/ble/)

## Enable reconnaissance / Discover devices around
```
ble.recon on
```
⚠️ Most commands require `ble.recon on`.

## Show discovered devices
```
ble.show
```

## Enumerate BLE device
```
ble.enum [MAC]
```

## Send HEX_DATA to a device
```
ble.write [MAC] [UUID] [HEX_DATA]
```
