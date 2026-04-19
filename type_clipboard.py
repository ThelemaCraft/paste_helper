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
    code = ord(char)
    inp_down = INPUT(type=INPUT_KEYBOARD)
    inp_down.u.ki = KEYBDINPUT(
        wVk=0, wScan=code, dwFlags=KEYEVENTF_UNICODE,
        time=0, dwExtraInfo=None
    )
    ctypes.windll.user32.SendInput(1, ctypes.byref(inp_down), ctypes.sizeof(inp_down))
    
    inp_up = INPUT(type=INPUT_KEYBOARD)
    inp_up.u.ki = KEYBDINPUT(
        wVk=0, wScan=code, dwFlags=KEYEVENTF_UNICODE | KEYEVENTF_KEYUP,
        time=0, dwExtraInfo=None
    )
    ctypes.windll.user32.SendInput(1, ctypes.byref(inp_up), ctypes.sizeof(inp_up))

# ========== 发送 Enter 键 ==========
def send_enter():
    VK_RETURN = 0x0D
    inp_down = INPUT(type=INPUT_KEYBOARD)
    inp_down.u.ki = KEYBDINPUT(
        wVk=VK_RETURN, wScan=0, dwFlags=0,
        time=0, dwExtraInfo=None
    )
    ctypes.windll.user32.SendInput(1, ctypes.byref(inp_down), ctypes.sizeof(inp_down))
    
    inp_up = INPUT(type=INPUT_KEYBOARD)
    inp_up.u.ki = KEYBDINPUT(
        wVk=VK_RETURN, wScan=0, dwFlags=KEYEVENTF_KEYUP,
        time=0, dwExtraInfo=None
    )
    ctypes.windll.user32.SendInput(1, ctypes.byref(inp_up), ctypes.sizeof(inp_up))

# ========== 检测 ESC 键（全局，无需焦点）==========
def is_esc_pressed():
    """返回 True 表示 ESC 键正在被按下"""
    return bool(ctypes.windll.user32.GetAsyncKeyState(0x1B) & 0x8000)

# ========== 主函数 ==========
def type_clipboard(delay=0.008, wait_seconds=3):
    text = pyperclip.paste()
    if not text:
        print("剪贴板为空")
        return
    
    print(f"将在 {wait_seconds} 秒后开始输入，共 {len(text)} 个字符...")
    print("提示：按 ESC 键可随时中断输入")
    
    # 倒计时 + 检测 ESC
    for remaining in range(wait_seconds, 0, -1):
        if is_esc_pressed():
            print("\n用户按 ESC 中断！")
            return
        print(f"\r{remaining} 秒后开始...", end="")
        time.sleep(1)
    print("\r开始输入！          ")
    
    try:
        for i, ch in enumerate(text):
            if is_esc_pressed():
                print("\n用户按 ESC 中断！已停止输入。")
                return
            
            if ch == '\n':
                send_enter()
            else:
                send_unicode_char(ch)
            time.sleep(delay)
            
            if (i + 1) % 100 == 0:
                print(f"已输入 {i+1}/{len(text)} 字符")
        
        print("输入完成！")
    except Exception as e:
        print(f"错误: {e}")

if __name__ == "__main__":
    type_clipboard(delay=0.008, wait_seconds=3)