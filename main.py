from src.models.AppManager import AppManager
cond = True

if __name__ == "__main__":
    Manager: AppManager = AppManager()
    
    # with open("blacklist.json", "r") as f:
    #     blacklist = json.load(f)

    while cond is True:
        Manager.get_running_processes()
        res = Manager.send_running_processes()
        Manager.close_running_processes(res["matches"])
    # print(res["matches"])
    