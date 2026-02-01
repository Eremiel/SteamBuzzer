#!/usr/bin/env python3

import struct
import time
import sys

def find_steam_deck_controller():
    try:
        import hid
    except ImportError:
        print("Error: hidapi library required. Install with: pip install hidapi")
        sys.exit(1)
    
    # Steam Deck Controller vendor and product IDs
    VALVE_VENDOR_ID = 0x28de
    STEAM_DECK_PRODUCT_ID = 0x1205
    
    devices = hid.enumerate(VALVE_VENDOR_ID, STEAM_DECK_PRODUCT_ID)
    
    for device in devices:
        if device['interface_number'] == 2:  # Haptic interface
            return hid.device()
    
    return None

def send_haptic_pulse(device, pad='both', amplitude=0x8000, period=0x0050, count=4):
    """
    Send haptic pulse to Steam Deck trackpad
    
    Args:
        device: HID device handle
        pad: 'left' (0x01), 'right' (0x00), or 'both'
        amplitude: Vibration strength (0x0000-0xFFFF)
        period: Time period in microseconds
        count: Number of pulses
    """
    HAPTIC_CMD = 0x8f
    HAPTIC_SUBCMD = 0x07
    
    pads = []
    if pad == 'both':
        pads = [0x00, 0x01]  # Right, Left
    elif pad == 'left':
        pads = [0x01]
    else:
        pads = [0x00]
    
    for pad_id in pads:
        # Build haptic message
        message = struct.pack('<BBBHHH',
            HAPTIC_CMD,      # Command
            HAPTIC_SUBCMD,   # Subcommand
            pad_id,          # Pad (0=right, 1=left)
            amplitude,       # Amplitude
            period,          # Period
            count            # Count
        )
        
        # Pad to 64 bytes
        message += b'\x00' * (64 - len(message))
        
        try:
            device.write(message)
        except Exception as e:
            print(f"Error sending haptic command: {e}")

def main():
    print("Steam Deck Haptic Feedback Test")
    print("Press Ctrl+C to exit")
    print("-" * 40)
    
    # Try to find and open the device
    try:
        import hid
    except ImportError:
        print("\nPlease install hidapi:")
        print("  pip install hidapi")
        sys.exit(1)
    
    device = hid.device()
    
    try:
        # Steam Deck Controller IDs
        VALVE_VENDOR_ID = 0x28de
        STEAM_DECK_PRODUCT_ID = 0x1205
        
        device.open(VALVE_VENDOR_ID, STEAM_DECK_PRODUCT_ID)
        print("Connected to Steam Deck controller")
        print()
        
        # Main loop
        pulse_count = 0
        while True:
            pulse_count += 1
            # multiple pulses -> 200ms duration
            # 50us period, repeated 4000 times ≈ 200ms
            send_haptic_pulse(
                device, 
                pad='both',
                amplitude=0x8000,  # Medium strength
                period=0x0032,     # 50 microseconds
                count=4000         # Repeat count for ~200ms
            )
            
            time.sleep(2)  # Wait 2 seconds
            
    except OSError as e:
        print(f"\nError: Could not open Steam Deck controler")
        print(f"Details: {e}")
        print("\nTroubleshooting:")
        print("Make sure you're running on Steam Deck")
        print("You may need root permissions (try: sudo python3 script.py)")
        print("required library is hidapi")
        sys.exit(1)
        
    except KeyboardInterrupt:
        print("\n\nExiting...")
        
    finally:
        device.close()

if __name__ == "__main__":
    main()
