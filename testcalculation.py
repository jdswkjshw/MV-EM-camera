import cv2
import ctypes
import numpy as np
from MVGigE import *


# 假设您已经有了一个函数来从工业相机获取图像
def get_camera_image(hCam, hImage):
    # 这个函数应该使用您提供的相机接口来获取图像
    MVSingleGrab(hCam, hImage, 0)
    pass


# 初始化相机库
if MVInitLib() != MVSTATUS_CODES.MVST_SUCCESS:
    print("Failed to initialize library.")
    exit()



# 更新相机列表并打开相机
r=MVUpdateCameraList()
if (r != MVSTATUS_CODES.MVST_SUCCESS):
        print('查找连接计算机失败！')

num_cameras = MVGetNumOfCameras().num
if num_cameras == 0:
    print("No camera found!")
    exit()

# 获取相机数量
num_of_cameras = MVGetNumOfCameras()
if num_of_cameras.status != MVSTATUS_CODES.MVST_SUCCESS or num_of_cameras.num == 0:
    print("No camera found.")
    exit()

hCam = MVOpenCamByIndex(0).hCam

# 创建一个图像对象用于接收相机图像
width = MVGetWidth(hCam).width
height = MVGetHeight(hCam).height
pf = MVGetPixelFormat(hCam).pixelFormat  # 获取图像格式

hImage = MVImageCreate(width, height,int(pf.value)).himage


s=MVSingleGrab(hCam, hImage, 10)
if s != MVSTATUS_CODES.MVST_SUCCESS:
    print("Failed to grab image.")
    exit()

# 使用 ctypes 来获取图像数据
image_data_ptr = ctypes.cast(hImage, ctypes.POINTER(ctypes.c_ubyte))
if not image_data_ptr:
    print("Image data pointer is null.")
    exit()
# 创建一个 NumPy 数组，直接从 ctypes 指针中读取数据
image_array = np.ctypeslib.as_array(image_data_ptr.contents, shape=(height, width, 3))
image_cv = cv2.cvtColor(image_array, cv2.COLOR_BGR2RGB) 

# 显示原图像
cv2.imshow('Original Image', image_cv)

# 对图像进行降噪处理，这里使用高斯模糊
image_blurred = cv2.GaussianBlur(image_array, (5, 5), 0)

# 对图像进行二值化处理
_, binary_image = cv2.threshold(image_blurred, 150, 255, cv2.THRESH_BINARY)

# 显示二值化图像
cv2.imshow('Binary Image', binary_image)

# 等待用户按键，再继续处理
cv2.waitKey(0)

# 寻找轮廓
contours, _ = cv2.findContours(binary_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# 假设最大的轮廓是光点
if contours:
    contour = max(contours, key=cv2.contourArea)
    M = cv2.moments(contour)
    # 计算几何中心坐标
    cx = int(M['m10'] / M['m00'])
    cy = int(M['m01'] / M['m00'])
    print(f"The geometric center of the light spot is: ({cx}, {cy})")
    # 返回光点的几何中心坐标
    result = (cx, cy)

# 释放窗口
cv2.destroyAllWindows()

MVStopGrabWindow(hCam)

# 关闭相机
MVCloseCam(hCam)

# 退出函数库
MVTerminateLib()

# 返回光点的几何中心坐标
print(result)

