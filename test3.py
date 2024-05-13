import cv2
import os
import ctypes
import datetime
import numpy as np
from ctypes import *
from GigECamera_Types import *
from MVGigE import *

# Assuming 'IMAGE_INFO' and other necessary classes are already imported from 'GigECamera_Types.py'

def save_and_convert_image(hCam, hImage, width, height):
    # Assuming IMAGE_INFO and other classes/functions are imported from GigECamera_Types and MVGigE
    image_info = IMAGE_INFO()

    # Convert Python handle to ctypes type if necessary (depends on how hImage is defined)
    if isinstance(hImage, int):
        hImage_ctype = c_void_p(hImage)  # or c_uint64(hImage) depending on your SDK's requirements
    else:
        hImage_ctype = hImage

    # Call MVInfo2Image with correct references and check for success
    result = MVGigE.MVInfo2Image(hCam, byref(image_info), byref(hImage_ctype))
    if result != MVSTATUS_CODES.MVST_SUCCESS:
        print("Failed to convert image data")
        return None

    # Access the buffer from IMAGE_INFO if available
    if image_info.pImageBuffer:
        # Construct numpy array from the image buffer
        buffer_type = (c_ubyte * image_info.nImageSizeAcq)
        buffer = buffer_type.from_address(addressof(image_info.pImageBuffer.contents))
        image_array = np.ctypeslib.as_array(buffer, shape=(height, width))

        # Convert Bayer GRBG to BGR
        img_bgr = cv2.cvtColor(image_array, cv2.COLOR_BAYER_GR2BGR)

        # Generate a filename with the current system time
        current_time = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        image_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), f"{current_time}.jpg")

        # Save the image to JPG format
        cv2.imwrite(image_path, img_bgr)
        return image_path
    else:
        print("Image buffer is NULL")
        return None

# Usage example (make sure to replace this part in your main function)
def main():
    # Initialize and open camera
    MVInitLib()
    MVUpdateCameraList()
    hcam = MVOpenCamByIndex(0)
    if hcam.status != MVSTATUS_CODES.MVST_SUCCESS:# 首次初始化失败 再次初始化
        MVInitLib()
        MVUpdateCameraList()
        hcam = MVOpenCamByIndex(0)

    # 创建一个图像对象用于接收相机图像
    width = MVGetWidth(hcam.hCam).width
    height = MVGetHeight(hcam.hCam).height
    pixel_format_enum = MVGetPixelFormat(hcam.hCam).pixelFormat
    print("Width:", width, "Height:", height, "Pixel Format Enum:", pixel_format_enum)

   # For BayerGR8, use 8 bits per pixel
    bpp = 8
    hImage = MVImageCreate(width, height, bpp).himage
    # image_info = IMAGE_INFO()

    # 采集单帧图像
    grab_result=MVSingleGrab(hcam.hCam, hImage, 100)
    if grab_result.status != MVSTATUS_CODES.MVST_SUCCESS:
        print("Failed to capture image")
        return

    # Save and convert the image
    image_path = save_and_convert_image(hcam.hCam, hImage, width, height)
    if image_path:
        print(f"Image saved at {image_path}")

    # Cleanup
    MVStopGrab(hcam.hCam)
    MVCloseCam(hcam.hCam)
    MVTerminateLib()

if __name__ == "__main__":
    main()
