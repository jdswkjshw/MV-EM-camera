import cv2
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

    # Obtain image dimensions and format
    width = MVGetWidth(hcam.hCam).width
    height = MVGetHeight(hcam.hCam).height
    pixel_format_enum = MVGetPixelFormat(hcam.hCam).pixelFormat
    print("Width:", width, "Height:", height, "Pixel Format Enum:", pixel_format_enum)

    # Set bits per pixel based on pixel format
    bpp = 8  # Set to 8 for BayerGR8, adjust if different format
    hImage = MVImageCreate(width, height, bpp).himage

    # Initialize IMAGE_INFO and capture a frame
    image_info = IMAGE_INFO()
    result = MVSingleGrab(hcam.hCam, hImage, 1000)
    if result.status != MVSTATUS_CODES.MVST_SUCCESS:
        print("Failed to capture image")
        return

    # Check if the image buffer is valid
    if not image_info.pImageBuffer:
        print("Image buffer is NULL")
        return

    # Convert the image buffer to a NumPy array
    # Assumption: image_info.nImageSizeAcq gives the total bytes in the buffer
    buffer_type = (c_ubyte * image_info.nImageSizeAcq)
    buffer = buffer_type.from_address(cast(image_info.pImageBuffer, POINTER(c_ubyte)).value)
    image_array = np.ctypeslib.as_array(buffer, shape=(height, width))

    # Convert to grayscale (assuming Bayer pattern)
    gray_image = cv2.cvtColor(image_array, cv2.COLOR_BAYER_GR2GRAY)

    # Apply Gaussian Blur
    denoised_image = cv2.GaussianBlur(gray_image, (5, 5), 0)

    # Binarization
    _, binary_image = cv2.threshold(denoised_image, 128, 255, cv2.THRESH_BINARY)

    # Find contours and calculate the centroid of the largest spot
    contours, _ = cv2.findContours(binary_image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    largest_contour = max(contours, key=cv2.contourArea)
    M = cv2.moments(largest_contour)
    cx = int(M['m10']/M['m00'])
    cy = int(M['m01']/M['m00'])

    # Display the images and centroid
    cv2.circle(gray_image, (cx, cy), 5, (0, 255, 0), -1)
    cv2.imshow("Original Image", gray_image)
    cv2.imshow("Binary Image", binary_image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    # Cleanup
    MVStopGrab(hcam.hCam)
    MVCloseCam(hcam.hCam)
    MVTerminateLib()

if __name__ == "__main__":
    main()
