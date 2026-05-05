# USB Relay PRO Python Controller

A professional Python module to control the 4-port USB Relay PRO.

## Description

This library provides an object-oriented interface to control a 4-port USB relay device over a serial connection. It abstracts the low-level hex protocol, providing a simple API to turn individual relays on/off, control all relays simultaneously, and perform power-cycling operations.

## Design

### Architecture
The library is designed around the `USBRelay` class, which manages the lifecycle of the serial connection and maintains the internal state of the relays.

- **Communication**: Uses `pyserial` to communicate at 9600 baud.
- **State Tracking**: Since the USB Relay PRO hardware does not support querying the current state of a relay, the `USBRelay` class maintains an internal state map (`_states`) to track the last commanded state of each port.
- **Resource Management**: Supports both direct object instantiation and the Python context manager (`with` statement) to ensure serial ports are closed properly.

### Protocol Implementation
- **Turn ON**: Sends `0xFF` followed by the relay number (1-4).
- **Turn OFF**: Sends `0xFD` followed by the relay number (1-4).

## Installation

Install the required dependency:
```bash
pip install pyserial
```

## Usage

### Basic Control
```python
from usb_relay import USBRelay

# Initialize the relay (defaults to /dev/ttyACM0 at 9600 baud)
relay = USBRelay()

try:
    # Control individual relays
    relay.on(1)   # Turn on relay 1
    relay.off(1)  # Turn off relay 1
    
    # Bulk control
    relay.all_on()  # Turn all 4 relays on
    relay.all_off() # Turn all 4 relays off
finally:
    relay.close()
```

### Power Cycling
The `power_cycle` method is useful for resetting connected hardware. It checks the internal state: if the relay is ON, it toggles it OFF $\rightarrow$ Delay $\rightarrow$ ON. If it is already OFF, it simply turns it ON.

```python
# Power cycle relay 2 with a 5-second delay
relay.power_cycle(2, delay=5)
```

### Using as a Context Manager
For guaranteed cleanup of the serial port:
```python
from usb_relay import USBRelay

with USBRelay(port='/dev/ttyACM0') as relay:
    relay.on(1)
    # Port is automatically closed when exiting the block
```

## Troubleshooting

**Permission Denied**: If you get a permission error accessing `/dev/ttyACM0`, run:
```bash
sudo chmod 666 /dev/ttyACM0
```
