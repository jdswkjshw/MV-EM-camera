# debug mode
import cv2
import numpy as np
from ctypes import *
from GigECamera_Types import *
from MVGigE import *

def main():
    # Initialize the library
    if MVInitLib() != MVSTATUS_CODES.MVST_SUCCESS:
        print("Library initialization failed")
        return

    # Update camera list
    if MVUpdateCameraList() != MVSTATUS_CODES.MVST_SUCCESS:
        print("Failed to update camera list")
        return

    hcam = MVOpenCamByIndex(0)
    if hcam.status != MVSTATUS_CODES.MVST_SUCCESS:
        print("Failed to open camera")
        return

    # Prepare to capture
    # Omitting MVStartGrabWindow since we're using OpenCV for display
    #MVSetTriggerMode(camera_info.hCam, TriggerModeEnums.TriggerMode_On)  # Set trigger mode if needed

    # 创建一个图像对象用于接收相机图像
    width = MVGetWidth(hcam.hCam).width
    height = MVGetHeight(hcam.hCam).height
    pixel_format_enum = MVGetPixelFormat(hcam.hCam).pixelFormat
    print("Width:", width, "Height:", height, "Pixel Format Enum:", pixel_format_enum)

    # Determine bits per pixel based on the pixel format
    bpp = 24  # Default to 24 for color images, adjust based on actual format
    if pixel_format_enum in [MV_PixelFormatEnums.PixelFormat_Mono8, MV_PixelFormatEnums.PixelFormat_BayerRG8]:
        bpp = 8  # Adjust this based on actual supported formats

    hImage = MVImageCreate(width, height, bpp).himage
   # For BayerGR8, use 8 bits per pixel
    bpp = 8
    hImage = MVImageCreate(width, height, bpp).himage
    if hImage is None or isinstance(hImage, MVSTATUS_CODES):
        print("Failed to create image object")
        return

    # Set camera to free run mode for continuous capture
    #if MVSetTriggerMode(hcam.hCam, TriggerModeEnums.TriggerMode_Off) != MVSTATUS_CODES.MVST_SUCCESS:
     #   print("Failed to set trigger mode")
      #  return
    MVGigE.MVSingleGrab.restype = c_int
    # Capture a single frame
    grab_status=MVSingleGrab(hcam.hCam, hImage, 1000).status
    if MVSingleGrab(hcam.hCam, hImage, 1000).status != MVSTATUS_CODES.MVST_SUCCESS:
        print("Failed to capture image")
        print(f"Failed to capture image, error code: {grab_status}")
        return

    # Assuming image capture is successful from here onwards...
    print("Image captured successfully!")

    # Clean up
    MVStopGrab(hcam.hCam)
    MVCloseCam(hcam.hCam)
    MVTerminateLib()

if __name__ == "__main__":
    main()
