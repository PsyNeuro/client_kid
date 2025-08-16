
import psutil
import requests
import logging

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
    
    
    
        
        