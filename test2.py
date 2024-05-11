import cv2
import ctypes
import numpy as np
from ctypes import *
from GigECamera_Types import *
from MVGigE import *

def main():
    # Initialize the library and camera
    MVInitLib()
    MVUpdateCameraList()
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
    
    # Capture a single frame
    if MVSingleGrab(hcam.hCam, hImage, 1000).status != MVSTATUS_CODES.MVST_SUCCESS:
        print("Failed to capture image")
        return
    
    image_info = IMAGE_INFO()  # This would need proper initialization and usage
    if not image_info.pImageBuffer:
        print("Image buffer is NULL")
        return

    # Assuming the image buffer is accessible and correctly populated
    buffer_type = (c_ubyte * (width * height))
    image_buffer = buffer_type.from_address(addressof(image_info.pImageBuffer.contents))
    image_array = np.ctypeslib.as_array(image_buffer, shape=(height, width))

    # Display the original image
    cv2.imshow("Original Image", image_array)
    cv2.waitKey(0)

    # Convert to grayscale if Bayer pattern
    gray_image = cv2.cvtColor(image_array, cv2.COLOR_BAYER_GR2GRAY)

    # Apply Gaussian Blur for noise reduction
    denoised_image = cv2.GaussianBlur(gray_image, (5, 5), 0)

    # Binarization
    _, binary_image = cv2.threshold(denoised_image, 128, 255, cv2.THRESH_BINARY)

    # Find contours and calculate the centroid of the largest spot
    contours, _ = cv2.findContours(binary_image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    largest_contour = max(contours, key=cv2.contourArea)
    M = cv2.moments(largest_contour)
    cx = int(M['m10']/M['m00'])
    cy = int(M['m01']/M['m00'])

    # Draw and display processed images
    cv2.circle(binary_image, (cx, cy), 5, (255, 0, 0), -1)
    cv2.imshow("Processed Image", binary_image)
    cv2.waitKey(0)

    # Cleanup
    cv2.destroyAllWindows()
    MVStopGrab(hcam.hCam)
    MVCloseCam(hcam.hCam)
    MVTerminateLib()

if __name__ == "__main__":
    main()
