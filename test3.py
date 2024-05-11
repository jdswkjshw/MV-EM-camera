from ctypes import *
from MVGigE import *

def main():
    MVInitLib()
    MVUpdateCameraList()
    hcam = MVOpenCamByIndex(0)
    if hcam.status != MVSTATUS_CODES.MVST_SUCCESS:
        print("Failed to open camera")
        return

    # Capture the image
    hImage = MVImageCreate(1280, 960, 8).himage  # Example parameters
    if MVSingleGrab(hcam.hCam, hImage, 1000).status != MVSTATUS_CODES.MVST_SUCCESS:
        print("Failed to capture image")
        return

    # Access the image data
    image_info = IMAGE_INFO()
    MVInfo2Image(hcam.hCam, id(hImage))  # Convert captured data to image
    if not image_info.pImageBuffer:
        print("Image buffer is NULL")
        return

    # Pointer to the image buffer
    pBuffer = image_info.pImageBuffer
    # Perform operations directly on the buffer here
    # For example, modifying pixel values, applying a filter, etc.

    # Clean up
    MVStopGrab(hcam.hCam)
    MVCloseCam(hcam.hCam)
    MVTerminateLib()

if __name__ == "__main__":
    main()
