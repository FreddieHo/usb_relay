import time
from usb_relay import USBRelay

def verify_status(relay, relay_num, expected):
    status = relay.get_status(relay_num)
    if status == expected:
        print(f"  [OK] Relay {relay_num} status is {status}")
    else:
        print(f"  [FAIL] Relay {relay_num} status is {status}, expected {expected}")
        raise AssertionError(f"Relay {relay_num} status mismatch: {status} != {expected}")

def test_relays():
    print("Starting USB Relay PRO test...")

    try:
        relay = USBRelay(port='/dev/ttyACM0')
        print("Connected to relay on /dev/ttyACM0")

        relay.off(1)
        time.sleep(0.5)
        # Test 1: Sequential ON/OFF with status checks
        print("\nTesting individual relays sequentially...")
        for i in range(1, 5):
            print(f"Turning relay {i} ON...")
            relay.on(i)
            verify_status(relay, i, True)
            time.sleep(2)

            print(f"Turning relay {i} OFF...")
            relay.off(i)
            verify_status(relay, i, False)
            time.sleep(2)

        # Test 2: All ON with status checks
        print("\nTurning ALL relays ON...")
        relay.all_on()
        for i in range(1, 5):
            verify_status(relay, i, True)
        time.sleep(1)

        # Test 3: All OFF with status checks
        print("\nTurning ALL relays OFF...")
        relay.all_off()
        time.sleep(1)
        for i in range(1, 5):
            verify_status(relay, i, False)
        time.sleep(1)

        # Test 4: Power Cycle - From OFF
        print("\nTesting power cycle on relay 1 (currently OFF)...")
        # Ensure it's OFF first
        relay.off(1)
        time.sleep(0.5)
#        verify_status(relay, 1, False)
        relay.power_cycle(1, delay=2)
        verify_status(relay, 1, True)
        print("  [OK] Power cycle from OFF successful")

        # Test 5: Power Cycle - From ON
        print("\nTesting power cycle on relay 1 (currently ON)...")
        # It's already ON from previous test
        relay.power_cycle(1, delay=2)
        time.sleep(0.5)
        verify_status(relay, 1, True)
        print("  [OK] Power cycle from ON successful")

        relay.close()
        print("\nAll tests completed successfully!")

    except Exception as e:
        print(f"\nAn error occurred: {e}")
        import traceback
        traceback.print_exc()
        print("\nTroubleshooting tips:")
        print("1. Ensure the device is plugged in and detected at /dev/ttyACM0.")
        print("2. Check permissions: sudo chmod 666 /dev/ttyACM0")
        print("3. Ensure 'pyserial' is installed: pip install pyserial")

if __name__ == "__main__":
    test_relays()
