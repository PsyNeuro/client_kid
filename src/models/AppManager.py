
import psutil
import requests
import logging
import win32gui
import win32con
import sys
import os

# sys.path.append(os.path.join(os.path.dirname(__file__), "src"))
# from UI.error_window import error_window

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
from UI.ErrorWindow import show_error_win32

logging.basicConfig(level=logging.ERROR, format='%(asctime)s %(levelname)s:%(message)s')

SERVER_URL = "http://localhost:80"

class AppManager:
    def __init__(self):
        self.__current_processes:list[psutil.Process,str] = list()
        self.__system_dir = [r"c:\windows"]
    
    def is_system_app(self, path):
        if not path:
            return True
        path = path.lower()
        return any(path.startswith(dir) for dir in self.__system_dir)

    def close_window(self, name):
        def enum_handler(hwnd, lParam): # is called for each window opened, 
                                        # hwnd is the handle to the window
            if win32gui.IsWindowVisible(hwnd): # is window visible
                title = win32gui.GetWindowText(hwnd) # get its title
                
                if name.lower() in title.lower():
                    print(f"Closing window: {title}")
                    win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0) # SENDS close window message to window, same as pressing X

        win32gui.EnumWindows(enum_handler, None)
    
    def get_running_processes(self) -> None:
        self.__current_processes = []
        for proc in psutil.process_iter(['pid', 'name', 'exe']):
            try:
                path = proc.info["exe"]
                name = proc.info["name"]
                if not self.is_system_app(path):
                    self.__current_processes.append((proc, name.lower()))
            except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                logging.error(f"Error accessing process info: {e}")
                continue
            
    def send_running_processes(self, data=None) -> None:
        # Extract process names from self.__current_processes (which contains (psutil.Process, name))
        Running_processes_names = [name for _, name in self.__current_processes]
        map1 = {
         "items": Running_processes_names  
        }
        
        # You can use Running_processes_names as needed, e.g., send as data
        url = f"{SERVER_URL}/send_processes"
        try:
            response = requests.post(url, json=map1)
            if response.status_code == 200:
                print("CLIENT: Successfully sent running processes.")
                return response.json()
            else:
                logging.error(f"CLIENT: Failed to send running processes. Status code: {response.status_code}, Response: {response.text}")
                response.raise_for_status()
        except Exception as e:
            logging.error(f"CLIENT: Exception occurred while sending running processes: {e}")
    
    def close_running_processes(self, blacklist):
        """
        Terminates all running processes whose names are in the blacklist.
        :param blacklist: List of process names (strings) to terminate.
        """
        self.get_running_processes()  # Refresh the current processes list

        for proc, name in self.__current_processes:
            if name in blacklist:
                try:
                    if proc.is_running():
                        print(f"CLIENT: Terminating blacklisted process: {name}")
                        proc.terminate()
                        show_error_win32("Parental Control", f"{name} has been closed.")
                        try:
                            proc.wait(timeout=3)
                            print(f"CLIENT: Terminated {name}")
                        except psutil.TimeoutExpired:
                            print(f"CLIENT: Timeout expired for {name}, force killing.")
                            try:
                                proc.kill()
                            except psutil.NoSuchProcess:
                                print(f"CLIENT: Process {name} already exited.")
                    else:
                        print(f"CLIENT: Process {name} is not running.")
                except psutil.NoSuchProcess:
                    print(f"CLIENT: Process {name} no longer exists.")
                except psutil.AccessDenied:
                    print(f"CLIENT: Access denied when trying to terminate {name}.")
            else:
                print(f"CLIENT: {name} is not in blacklist.")
    
    def get_blacklist(self):
        url = f"{SERVER_URL}/get_blacklist"
        try:
            response = requests.get(url)
            if response.status_code == 200:
                print("CLIENT: Successfully received blacklist.")
                return response.json()  # <-- Return the parsed JSON data
            else:
                logging.error(f"CLIENT: Failed to receive blacklist. Status code: {response.status_code}, Response: {response.text}")
                response.raise_for_status()
        except Exception as e:
            logging.error(f"CLIENT: Exception occurred while getting blacklist: {e}")
    
    def clear_blacklist(self):
        url = f"{SERVER_URL}/clear_blacklist"
        try:
            response = requests.post(url)
            if response.status_code == 200:
                print("CLIENT: Successfully cleared blacklist.")
                return response.json()
            else:
                logging.error(f"CLIENT: Failed to clear blacklist. Status code: {response.status_code}, Response: {response.text}")
                response.raise_for_status()
        except Exception as e:
            logging.error(f"CLIENT: Exception occurred while clearing blacklist: {e}")

    def add_blacklist(self, entries):
        """
        Adds entries to the server blacklist.
        :param entries: List of process names (strings) to add.
        """
        url = f"{SERVER_URL}/add_blacklist"
        try:
            response = requests.post(url, json=entries)
            if response.status_code == 200:
                print(f"CLIENT: Successfully added entries to blacklist: {entries}")
                return response.json()
            else:
                logging.error(f"CLIENT: Failed to add to blacklist. Status code: {response.status_code}, Response: {response.text}")
                response.raise_for_status()
        except Exception as e:
            logging.error(f"CLIENT: Exception occurred while adding to blacklist: {e}")
    
        
        