import serial
import time

class USBRelay:
    """
    Control module for the USB Relay PRO (4-Port).
    Communication Protocol:
    - Command format: [0xA0, channel, operation, checksum]
      - channel: relay number (1-4), or 0x0F for all relays
      - operation: 0x00=OFF, 0x01=ON, 0x02=query status
      - checksum: (0xA0 + channel + operation) & 0xFF
    """

    # Minimum seconds between completing a response read and sending the next command.
    # The device becomes unresponsive if queried too soon after a previous exchange.
    _MIN_INTER_CMD_DELAY = 0.1

    def __init__(self, port='/dev/ttyACM0', baudrate=115200, timeout=1, auto_open=True):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.ser = None
        self._last_read_time = 0.0
        if auto_open:
            self.open()

    def open(self):
        """Opens the serial port."""
        if self.ser is None:
            self.ser = serial.Serial(self.port, self.baudrate, timeout=self.timeout)
        return self

    def close(self):
        """Closes the serial port."""
        if self.ser is not None:
            self.ser.close()
            self.ser = None

    def __enter__(self):
        return self.open()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def _build_command(self, channel, operation):
        """Builds a 4-byte command packet with checksum."""
        return [0xA0, channel, operation, (0xA0 + channel + operation) & 0xFF]

    def _send_command(self, cmd):
        """Internal method to send bytes to the relay."""
        if self.ser is None or not self.ser.is_open:
            raise RuntimeError("Serial port is not open. Use 'with USBRelay() as relay:' or call .open()")
        elapsed = time.time() - self._last_read_time
        if elapsed < self._MIN_INTER_CMD_DELAY:
            time.sleep(self._MIN_INTER_CMD_DELAY - elapsed)
        self.ser.write(bytes(cmd))
        self.ser.flush()

    def _read_status_line(self):
        """Read one status line and return (channel_num, is_on)."""
        line = self.ser.readline().decode('ascii').strip()
        self._last_read_time = time.time()
        if not line:
            raise RuntimeError("No response from device (timeout)")
        ch_part, state = line.split(':')
        return int(ch_part[2:]), state == 'ON'

    def _discard_lines(self, count):
        """Read and discard a fixed number of response lines."""
        for _ in range(count):
            self.ser.readline()
        self._last_read_time = time.time()

    def on(self, relay_num):
        """
        Turns on the specified relay.
        :param relay_num: Relay number (1 to 4)
        """
        if not 1 <= relay_num <= 4:
            raise ValueError("Relay number must be between 1 and 4")
        self._send_command(self._build_command(relay_num, 0x01))
        self._discard_lines(1)

    def off(self, relay_num):
        """
        Turns off the specified relay.
        :param relay_num: Relay number (1 to 4)
        """
        if not 1 <= relay_num <= 4:
            raise ValueError("Relay number must be between 1 and 4")
        self._send_command(self._build_command(relay_num, 0x00))
        self._discard_lines(1)

    def all_on(self):
        """Turns all relays on. Device always returns 8 status lines."""
        self._send_command(self._build_command(0x0F, 0x01))
        self._discard_lines(8)

    def all_off(self):
        """Turns all relays off. Device always returns 8 status lines."""
        self._send_command(self._build_command(0x0F, 0x00))
        self._discard_lines(8)

    def get_status(self, relay_num):
        """
        Queries the device for the current status of the specified relay.
        :param relay_num: Relay number (1 to 4)
        :return: True if ON, False if OFF
        """
        if not 1 <= relay_num <= 4:
            raise ValueError("Relay number must be between 1 and 4")
        self._send_command(self._build_command(relay_num, 0x02))
        ch_num, is_on = self._read_status_line()
        if ch_num != relay_num:
            raise RuntimeError(f"Unexpected response: queried CH{relay_num} but got CH{ch_num}")
        return is_on

    def power_cycle(self, relay_num, delay=5):
        """
        Power cycles the specified relay.
        If current status is ON, turns it OFF, waits, then turns it ON.
        If current status is OFF, just turns it ON.

        :param relay_num: Relay number (1 to 4)
        :param delay: Delay in seconds between OFF and ON
        """
        if not 1 <= relay_num <= 4:
            raise ValueError("Relay number must be between 1 and 4")

        if self.get_status(relay_num):
            self.off(relay_num)
        time.sleep(delay)
        self.on(relay_num)
