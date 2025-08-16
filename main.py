from src.models.AppManager import AppManager

if __name__ == "__main__":
    Manager:AppManager = AppManager()
    Manager.get_running_processes()
    Manager.send_running_processes()
    # print(type(Manager.__current_processes[1][0]))
    
    