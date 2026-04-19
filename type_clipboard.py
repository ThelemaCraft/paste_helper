import time
import ctypes
from ctypes import wintypes
import pyperclip 
import sys

# ========== Windows API 结构定义 ==========
INPUT_KEYBOARD = 1
KEYEVENTF_KEYUP = 0x0002
KEYEVENTF_UNICODE = 0x0004

class KEYBDINPUT(ctypes.Structure):
    _fields_ = [
        ("wVk", wintypes.WORD),
        ("wScan", wintypes.WORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong))
    ]

class MOUSEINPUT(ctypes.Structure):
    _fields_ = [
        ("dx", wintypes.LONG),
        ("dy", wintypes.LONG),
        ("mouseData", wintypes.DWORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong))
    ]

class HARDWAREINPUT(ctypes.Structure):
    _fields_ = [
        ("uMsg", wintypes.DWORD),
        ("wParamL", wintypes.WORD),
        ("wParamH", wintypes.WORD)
    ]

class _INPUTunion(ctypes.Union):
    _fields_ = [
        ("ki", KEYBDINPUT),
        ("mi", MOUSEINPUT),
        ("hi", HARDWAREINPUT)
    ]

class INPUT(ctypes.Structure):
    _fields_ = [
        ("type", wintypes.DWORD),
        ("u", _INPUTunion)
    ]

# ========== 发送单个 Unicode 字符 ==========
def send_unicode_char(char):
    """通过 Windows API 发送一个 Unicode 字符（按下+弹起）"""
    code = ord(char)
    
    # 按下
    inp_down = INPUT(type=INPUT_KEYBOARD)
    inp_down.u.ki = KEYBDINPUT(
        wVk=0,
        wScan=code,
        dwFlags=KEYEVENTF_UNICODE,
        time=0,
        dwExtraInfo=None
    )
    ctypes.windll.user32.SendInput(1, ctypes.byref(inp_down), ctypes.sizeof(inp_down))
    
    # 弹起
    inp_up = INPUT(type=INPUT_KEYBOARD)
    inp_up.u.ki = KEYBDINPUT(
        wVk=0,
        wScan=code,
        dwFlags=KEYEVENTF_UNICODE | KEYEVENTF_KEYUP,
        time=0,
        dwExtraInfo=None
    )
    ctypes.windll.user32.SendInput(1, ctypes.byref(inp_up), ctypes.sizeof(inp_up))

# ========== 发送 Enter 键 ==========
def send_enter():
    """发送 Enter 键"""
    VK_RETURN = 0x0D
    
    # 按下
    inp_down = INPUT(type=INPUT_KEYBOARD)
    inp_down.u.ki = KEYBDINPUT(
        wVk=VK_RETURN,
        wScan=0,
        dwFlags=0,
        time=0,
        dwExtraInfo=None
    )
    ctypes.windll.user32.SendInput(1, ctypes.byref(inp_down), ctypes.sizeof(inp_down))
    
    # 弹起
    inp_up = INPUT(type=INPUT_KEYBOARD)
    inp_up.u.ki = KEYBDINPUT(
        wVk=VK_RETURN,
        wScan=0,
        dwFlags=KEYEVENTF_KEYUP,
        time=0,
        dwExtraInfo=None
    )
    ctypes.windll.user32.SendInput(1, ctypes.byref(inp_up), ctypes.sizeof(inp_up))

# ========== 发送完整字符串（支持换行 + 可中断） ==========
def type_clipboard(delay=0.008, wait_seconds=3):
    """
    将剪贴板内容逐字符模拟键盘输入
    delay: 每字符间隔（秒），默认 0.008
    wait_seconds: 运行前等待时间，默认 3 秒
    按 Ctrl+C 可随时中断输入
    """
    # 获取剪贴板内容
    text = pyperclip.paste()
    if not text:
        print("剪贴板为空")
        return
    
    print(f"将在 {wait_seconds} 秒后开始输入，共 {len(text)} 个字符...")
    print("提示：按 Ctrl+C 可随时中断输入")
    
    try:
        time.sleep(wait_seconds)
        
        print("开始输入...")
        for i, ch in enumerate(text):
            # 检查是否被中断
            if ch == '\n':
                send_enter()      # 换行符发送 Enter 键
            else:
                send_unicode_char(ch)
            time.sleep(delay)
            # 每 100 个字符打印一次进度
            if (i + 1) % 100 == 0:
                print(f"已输入 {i+1}/{len(text)} 字符")
        
        print("输入完成！")
        
    except KeyboardInterrupt:
        print("\n\n用户中断！已停止输入。")
        sys.exit(0)

# ========== 主程序 ==========
if __name__ == "__main__":
    # 使用方法：
    # 1. 先复制你想要输入的内容（Ctrl+C）
    # 2. 运行此脚本
    # 3. 在倒计时结束前切换到目标窗口并点击输入框
    # 4. 按 Ctrl+C 可随时中断
    
    # 可以在这里修改参数
    type_clipboard(delay=0.008, wait_seconds=3)