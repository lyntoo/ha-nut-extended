# NUT (Network UPS Tools) — Extended Home Assistant Integration

A drop-in replacement for the built-in Home Assistant NUT integration that adds **UPS control buttons** and a **beeper switch** — features the official integration exposes as device automation actions only, with no UI entities.

---

## What's added over the official integration

| Entity | Type | Description |
|--------|------|-------------|
| **Beeper** | Switch | Enable / disable the UPS beeper. State reflects `ups.beeper.status`. |
| **Quick battery test** | Button | Starts a quick self-test (`test.battery.start.quick`) |
| **Battery test** | Button | Starts a full battery test (`test.battery.start`) |
| **Stop battery test** | Button | Aborts a running battery test (`test.battery.stop`) |
| **Reboot UPS** | Button | Briefly cuts power then restarts (`shutdown.reboot`) |
| **Maintenance shutdown (stay off)** | Button | Shuts down the UPS and keeps it off until manually restarted (`shutdown.stayoff`) |
| **Cut load immediately** | Button | Immediately cuts power to the load (`load.off`) |

All existing sensors, outlet switches, and outlet buttons from the official integration are fully preserved.

> Entities only appear if your UPS driver reports the corresponding command as available. No button or switch is created for unsupported commands.

---

## Compatibility

Works with any UPS supported by a NUT driver. Tested with **CyberPower** via the `usbhid-ups` driver.

---

## Installation

### Manual

1. Copy `custom_components/nut/` into your HA `config/custom_components/` folder
2. Restart Home Assistant

> **No need to remove or reconfigure the existing NUT integration.** The custom component uses the same domain (`nut`) and picks up your existing configuration automatically.

### HACS (Custom Repository)

1. In HACS → **Custom repositories** → add this repo URL → category **Integration**
2. Search for *NUT Extended* and install
3. Restart Home Assistant

---

## Requirements

- Home Assistant with the built-in NUT integration already configured (host, port, username, password)
- NUT server running and reachable
- Username + password configured in the integration (commands require authentication)

---

## Credits

- Original NUT integration: [home-assistant/core](https://github.com/home-assistant/core/tree/dev/homeassistant/components/nut)
- Extended control entities by [@lyntoo](https://github.com/lyntoo)
