# set camera properties
from ctypes import *
from GigECamera_Types import *
MVCamProptySheet=windll.LoadLibrary('./MVCamProptySheet')


class MVSetFrameRate():
    def __init__(self, hCam, fps):
        self.hCam = c_uint64(hCam)
        self.fps=c_double(fps)
        self.init()
    def init(self):
        result = MVCamProptySheet.MVSetFrameRate(self.hCam, self.fps)
        self.status = MVSTATUS_CODES(result)