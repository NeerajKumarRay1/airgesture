import pyautogui
import win32api
import win32con
import logging
from ctypes import windll

class SystemControl:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.screen_width, self.screen_height = pyautogui.size()
        self.smoothed_x = None
        self.smoothed_y = None
        self.smoothing_factor = 0.3
        self.last_click_time = 0
        self.click_cooldown = 0.5  # seconds

    def move_cursor(self, x, y):
        try:
            # Apply exponential smoothing
            self.smoothed_x = self.apply_exponential_smoothing(x, self.smoothed_x, self.smoothing_factor)
            self.smoothed_y = self.apply_exponential_smoothing(y, self.smoothed_y, self.smoothing_factor)
            
            # Convert normalized coordinates to screen coordinates
            screen_x = int(self.smoothed_x * self.screen_width)
            screen_y = int(self.smoothed_y * self.screen_height)
            
            # Move cursor
            pyautogui.moveTo(screen_x, screen_y, duration=0.1)
            self.logger.debug(f"Moving cursor to ({screen_x}, {screen_y})")
        except Exception as e:
            self.logger.error(f"Error moving cursor: {str(e)}")

    def perform_click(self):
        try:
            current_time = time.time()
            if current_time - self.last_click_time >= self.click_cooldown:
                pyautogui.click()
                self.last_click_time = current_time
                self.logger.debug("Performed click")
        except Exception as e:
            self.logger.error(f"Error performing click: {str(e)}")

    def adjust_volume(self, delta):
        try:
            for _ in range(abs(delta)):
                if delta > 0:
                    win32api.keybd_event(win32con.VK_VOLUME_UP, 0, 0, 0)
                    win32api.keybd_event(win32con.VK_VOLUME_UP, 0, win32con.KEYEVENTF_KEYUP, 0)
                else:
                    win32api.keybd_event(win32con.VK_VOLUME_DOWN, 0, 0, 0)
                    win32api.keybd_event(win32con.VK_VOLUME_DOWN, 0, win32con.KEYEVENTF_KEYUP, 0)
            self.logger.debug(f"Adjusted volume by {delta}")
        except Exception as e:
            self.logger.error(f"Error adjusting volume: {str(e)}")

    def adjust_brightness(self, delta):
        try:
            # Get current brightness
            brightness = windll.kernel32.GetDeviceGammaRamp(-1, None)
            # Adjust brightness (0-100)
            new_brightness = max(0, min(100, brightness + delta))
            # Set new brightness
            windll.kernel32.SetDeviceGammaRamp(-1, new_brightness)
            self.logger.debug(f"Adjusted brightness by {delta}")
        except Exception as e:
            self.logger.error(f"Error adjusting brightness: {str(e)}")

    def scroll(self, delta):
        try:
            pyautogui.scroll(delta)
            self.logger.debug(f"Scrolled by {delta}")
        except Exception as e:
            self.logger.error(f"Error scrolling: {str(e)}")

    def apply_exponential_smoothing(self, new_value, smoothed_value, smoothing_factor):
        if smoothed_value is None:
            return new_value
        return smoothing_factor * new_value + (1 - smoothing_factor) * smoothed_value 