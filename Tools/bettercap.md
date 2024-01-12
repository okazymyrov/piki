# Wi-Fi

> [!IMPORTANT]  
> Please use [the native method](https://github.com/okazymyrov/piki/blob/master/Systems/Wi-Fi.md#set-a-wi-fi-card-into-monitor-mode) to enable monitore mode since airmon-ng may cause errors in bettercap.
> to enable monitor mode as airmon-ng may cause errors in bettercap.

## Discover APs
```
sudo bettercap
set wifi.interface wlan0
wifi.recon on
wifi.show
```

# Bluetooth (BLE)

## References
* [BLUETOOTH LE](https://www.bettercap.org/modules/ble/)

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
