import ctypes
import time
import random

class WindowBot:
    # --- Windows Constants (Internal to the class) ---
    WM_KEYDOWN = 0x0100
    WM_KEYUP = 0x0101
    WM_ACTIVATE = 0x0006
    WA_CLICKACTIVE = 2

    def __init__(self, hwnd):
        # Initialize the bot with a specific window handle.
        self.hwnd = hwnd
        self.vk_map = self._build_vk_map()

    def _build_vk_map(self):
        # Creates the dictionary of Virtual Key codes.
        vks = {
            'backspace': 0x08, 
            'tab': 0x09, 
            'enter': 0x0D, 
            'shift': 0x10, 
            'ctrl': 0x11,
            'alt': 0x12, 
            'pause': 0x13, 
            'caps_lock': 0x14, 
            'esc': 0x1B, 
            'space': 0x20,
            'page_up': 0x21, 
            'page_down': 0x22, 
            'end': 0x23, 
            'home': 0x24, 
            'left': 0x25,
            'up': 0x26, 
            'right': 0x27, 
            'down': 0x28, 
            'insert': 0x2D, 
            'delete': 0x2E,
            'f1': 0x70, 
            'f2': 0x71, 
            'f3': 0x72, 
            'f4': 0x73, 
            'f5': 0x74, 
            'f6': 0x75,
            'f7': 0x76, 
            'f8': 0x77, 
            'f9': 0x78, 
            'f10': 0x79, 
            'f11': 0x7A, 
            'f12': 0x7B,
        }
        # Numbers 0-9
        for i in range(10):
            vks[str(i)] = 0x30 + i
        # Letters a-z
        for i in range(26):
            vks[chr(ord('a') + i)] = 0x41 + i
        return vks

    def _get_lparam(self, vk_code, status):
        # Calculates the 32-bit hardware metadata (LParam).
        scan_code = ctypes.windll.user32.MapVirtualKeyW(vk_code, 0)
        if status == "down":
            return 1 | (scan_code << 16)
        else:
            return 1 | (scan_code << 16) | (0xC0 << 24)

    def key_down(self, key):
        # Holds a key down in the background.
        vk = self.vk_map.get(key.lower())
        if self.hwnd and vk:
            # Activate window
            ctypes.windll.user32.PostMessageW(self.hwnd, self.WM_ACTIVATE, self.WA_CLICKACTIVE, 0)
            # Send the press
            ctypes.windll.user32.PostMessageW(self.hwnd, self.WM_KEYDOWN, vk, self._get_lparam(vk, "down"))

    def key_up(self, key):
        #Releases a held key.
        vk = self.vk_map.get(key.lower())
        if self.hwnd and vk:
            ctypes.windll.user32.PostMessageW(self.hwnd, self.WM_KEYUP, vk, self._get_lparam(vk, "up"))

    def press(self, key, duration=0.05):
        # A full down-and-up press.
        jitter = random.uniform(-0.01, 0.01)
        final_duration = duration + jitter
        if final_duration < 0.01: 
            final_duration = 0.01
        self.key_down(key)
        time.sleep(final_duration)
        self.key_up(key)

    def type_string(self, text, interval=0.05):
        #Types an entire string into the window.
        for char in text:
            if char == " ":
                self.press("space")
            else:
                self.press(char)
            time.sleep(interval)