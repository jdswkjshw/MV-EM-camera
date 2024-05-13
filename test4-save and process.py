# 放弃直接处理 先保存再读取
import time
import cv2
import os
import ctypes
import datetime
import numpy as np
from ctypes import *
from GigECamera_Types import *
from MVGigE import *
from setCameraProperties import *

def main():
    # Initialize
    MVInitLib()
    MVUpdateCameraList()
    hcam = MVOpenCamByIndex(0)
    if hcam.status != MVSTATUS_CODES.MVST_SUCCESS:# 首次初始化失败 再次初始化
        MVInitLib()
        MVUpdateCameraList()
        time.sleep(2)
        hcam = MVOpenCamByIndex(0)
    if hcam.status != MVSTATUS_CODES.MVST_SUCCESS:
        print('wrong')
    # 创建一个图像对象用于接收相机图像
    width = MVGetWidth(hcam.hCam).width
    height = MVGetHeight(hcam.hCam).height
    pixel_format_enum = MVGetPixelFormat(hcam.hCam).pixelFormat
    print("Width:", width, "Height:", height, "Pixel Format Enum:", pixel_format_enum)

   # For BayerGR8, use 8 bits per pixel
    bpp = 8
    himage = MVImageCreate(width, height, bpp).himage
    # image_info = IMAGE_INFO()

    # 采集单帧图像
    grab_result=MVSingleGrab(hcam.hCam, himage, 100)
    if grab_result.status != MVSTATUS_CODES.MVST_SUCCESS:
        print("Failed to capture image")
        return
    
    # Save the image to the specified path. The file name is idn+.bmp of the image.
    current_time = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    image_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), f"{current_time}.bmp")
    MVImageSave(himage, image_path.encode('utf-8'))

    # Use OpenCV to read the image saved in the previous step
    img = cv2.imread(image_path)

    # Display the original image
    cv2.imshow("Original Image", img)
    cv2.waitKey(0)

    # Apply Gaussian Blur for noise reduction
    blurred_img = cv2.GaussianBlur(img, (5, 5), 0)

    # Binarization
    _, binary_img = cv2.threshold(blurred_img, 128, 255, cv2.THRESH_BINARY)

    # Find contours and calculate the centroid of the largest spot, output the x and y coordinates
    contours, _ = cv2.findContours(binary_img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    largest_contour = max(contours, key=cv2.contourArea)
    M = cv2.moments(largest_contour)
    cx, cy = int(M['m10']/M['m00']), int(M['m01']/M['m00'])

    # Draw and display the processed image
    cv2.circle(img, (cx, cy), 5, (0, 255, 0), -1)
    cv2.imshow("Processed Image", img)
    cv2.waitKey(0)


    # Cleanup
    cv2.destroyAllWindows()
    MVStopGrab(hcam.hCam)
    MVCloseCam(hcam.hCam)
    MVTerminateLib()

if __name__ == "__main__":
    main()
