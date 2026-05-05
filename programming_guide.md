# USB Relay PRO (4-Port) Programming Guide

Source: https://wiki.diustou.com/en/USB_Relay_PRO

---

## Communication Protocol

Commands are 4 bytes sent in hexadecimal format over serial (USB or UART).

| Byte | Name            | Description                              |
|------|-----------------|------------------------------------------|
| 1    | Start Flag      | Always `0xA0`                            |
| 2    | Channel Address | `0x01`–`0x04` for channels 1–4; `0x0F` for all channels |
| 3    | Operation       | `0x00` = OFF, `0x01` = ON, `0x02` = Query status |
| 4    | Checksum        | `(Byte1 + Byte2 + Byte3) & 0xFF`         |

**Baud rate:** 115200 bps (UART); adaptive (USB)

---

## Commands — USB Relay PRO (TC, 4, CB, Opto)

### Switch Control

| Action              | HEX Command       |
|---------------------|-------------------|
| Turn ON channel 1   | `A0 01 01 A2`     |
| Turn OFF channel 1  | `A0 01 00 A1`     |
| Turn ON channel 2   | `A0 02 01 A3`     |
| Turn OFF channel 2  | `A0 02 00 A2`     |
| Turn ON channel 3   | `A0 03 01 A4`     |
| Turn OFF channel 3  | `A0 03 00 A3`     |
| Turn ON channel 4   | `A0 04 01 A5`     |
| Turn OFF channel 4  | `A0 04 00 A4`     |
| Turn ON all         | `A0 0F 01 B0`     |
| Turn OFF all        | `A0 0F 00 AF`     |

### Query Status

| Action                  | HEX Command   |
|-------------------------|---------------|
| Query channel 1 status  | `A0 01 02 A3` |
| Query channel 2 status  | `A0 02 02 A4` |
| Query channel 3 status  | `A0 03 02 A5` |
| Query channel 4 status  | `A0 04 02 A6` |
| Query all channels      | `A0 0F 02 B1` |

---

## Device Response Behaviour

All commands — including ON/OFF control commands — immediately trigger a status response from the device. Responses are ASCII lines terminated with `\r\n` (`0D 0A`), in the format `CHn:ON` or `CHn:OFF`.

### Single-channel control or query

Any command targeting one channel (ON, OFF, or Query) returns exactly **1 line** for that channel.

**Example — turn ON channel 1:**
- Send (hex): `A0 01 01 A2`
- Receive (ASCII): `CH1:ON`
- Receive (hex): `43 48 31 3A 4F 4E 0D 0A`

**Example — query channel 3 (currently OFF):**
- Send (hex): `A0 03 02 A5`
- Receive (ASCII): `CH3:OFF`
- Receive (hex): `43 48 33 3A 4F 46 46 0D 0A`

### All-channel control or query (`0x0F`)

Any command using the all-channel address (`0x0F`) always returns **exactly 8 lines**, one per channel, regardless of how many physical relays the device has.

**Example — turn OFF all channels (4-port device):**
- Send (hex): `A0 0F 00 AF`
- Receive (ASCII):
  ```
  CH1:OFF
  CH2:OFF
  CH3:OFF
  CH4:OFF
  CH5:OFF
  CH6:OFF
  CH7:OFF
  CH8:OFF
  ```

> **Implementation notes:**
> - After a single-channel ON/OFF command, always read and discard the 1 returned status line before the next operation.
> - After an all-channel ON/OFF command, always read and discard all 8 returned lines.
> - When parsing a status response, always extract the channel number from the `CHn` prefix and verify it matches the channel you queried. Do not assume the response belongs to the channel of the last command.

---

## Checksum Calculation

```python
checksum = (0xA0 + channel + operation) & 0xFF
```

Examples:
- ON channel 1:  `(0xA0 + 0x01 + 0x01) & 0xFF = 0xA2`
- OFF channel 1: `(0xA0 + 0x01 + 0x00) & 0xFF = 0xA1`
- Query ch 4:    `(0xA0 + 0x04 + 0x02) & 0xFF = 0xA6`
- All ON:        `(0xA0 + 0x0F + 0x01) & 0xFF = 0xB0`
- All OFF:       `(0xA0 + 0x0F + 0x00) & 0xFF = 0xAF`
