from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from comtypes import CLSCTX_ALL
import screen_brightness_control as sbc
import logging

logger = logging.getLogger(__name__)

class SystemController:
    def __init__(self):
        self.init_volume_control()
        
    def init_volume_control(self):
        try:
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            self.volume = interface.QueryInterface(IAudioEndpointVolume)
        except Exception as e:
            logger.error(f"Could not initialize volume control: {e}")
            self.volume = None
            
    def set_brightness(self, value):
        try:
            sbc.set_brightness(value, display=0)
        except Exception as e:
            logger.error(f"Could not set brightness: {e}")
            
    def set_volume(self, value):
        try:
            if self.volume:
                self.volume.SetMasterVolumeLevelScalar(value, None)
        except Exception as e:
            logger.error(f"Could not set volume: {e}") 