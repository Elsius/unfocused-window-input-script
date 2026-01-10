import win32gui
import win32ui
import ctypes
from ctypes import wintypes
import numpy as np

ctypes.windll.shcore.SetProcessDpiAwareness(1)
user32 = ctypes.windll.user32
PrintWindow = user32.PrintWindow
PrintWindow.argtypes = [wintypes.HWND, wintypes.HDC, wintypes.UINT]
PrintWindow.restype = wintypes.BOOL

class WindowCapture:
    def __init__(self, window_name):
        self.hwnd = win32gui.FindWindow(None, window_name)
        if not self.hwnd:
            raise Exception(f'Window not found: {window_name}')


    def get_screenshot(self):
        def cleanup(dcObj, cDC, wDC, dataBitMap, hwnd):
            dcObj.DeleteDC()
            cDC.DeleteDC()
            win32gui.ReleaseDC(hwnd, wDC)
            win32gui.DeleteObject(dataBitMap.GetHandle())
        # Get the size of the internal game area
        rect = win32gui.GetWindowRect(self.hwnd)
        self.w = rect[2] - rect[0]
        self.h = rect[3] - rect[1]
        if self.w <= 0 or self.h <= 0:
            print(f'height: {self.h}, width: {self.w}')
            return None
        
        wDC = win32gui.GetWindowDC(self.hwnd)
        dcObj = win32ui.CreateDCFromHandle(wDC)
        cDC = dcObj.CreateCompatibleDC()
        
        dataBitMap = win32ui.CreateBitmap()
        dataBitMap.CreateCompatibleBitmap(dcObj, self.w, self.h)
        cDC.SelectObject(dataBitMap)
        
        PrintWindow(self.hwnd, cDC.GetSafeHdc(), 2)
        
        # # 4. Convert to NumPy
        try:
            signedIntsArray = dataBitMap.GetBitmapBits(True)
            stride = ((self.w * 32 + 31) & ~31) // 8
            img = np.frombuffer(signedIntsArray, dtype='uint8')
            img.shape = (self.h, stride // 4, 4)
            img = img[:,:self.w,:]
        except (ValueError, Exception) as e:
            # Cleanup and skip this frame if the window resized mid-capture
            cleanup(dcObj, cDC, wDC, dataBitMap, self.hwnd)
            return None
        # 5. Cleanup (The most important part!)
        cleanup(dcObj, cDC, wDC, dataBitMap, self.hwnd)

        client_left, client_top = win32gui.ClientToScreen(self.hwnd, (0, 0))
        offset_x = client_left - rect[0]
        offset_y = client_top - rect[1]

        _, _, cw, ch = win32gui.GetClientRect(self.hwnd)

        # Slice: [y_start : y_end, x_start : x_end]
        # This removes the title bar and side borders
        img = img[offset_y : offset_y + ch, offset_x : offset_x + cw]

        # Drop Alpha channel
        # Make image C_CONTIGUOUS to avoid errors in OpenCV/YOLO
        img = np.ascontiguousarray(img[...,:3]).copy()

        return img

