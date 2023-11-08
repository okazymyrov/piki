# Wi-Fi

## Discover APs
```
sudo bettercap
set wifi.interface wlan0mon
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
