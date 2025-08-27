import win32gui
import win32con
import threading

def show_error_win32(title, message):
    def _show():
        win32gui.MessageBox(0, message, title, win32con.MB_ICONERROR)
    threading.Thread(target=_show, daemon=True).start()