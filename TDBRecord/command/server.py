import TDBRecord as tdbra

from threading import Thread
import time

def start():
    tdbra.logger.debug("TDBRecord Main function started!")

    statusCheckThread = Thread(target=statusChecker)
    statusCheckThread.daemon = True
    statusCheckThread.start()

    tdbra.logger.debug("TDBRecord Status Checker Thread started!")
    while True:
        try:
            command = tdbra.input("> ")
        except KeyboardInterrupt:
            for user in list(tdbra.data.keys()):
                tdbra.data[user]["exit"] = True
            while len(tdbra.data) > 0:
                time.sleep(0.4)
            break

        if command == "exit":
            for user in list(tdbra.data.keys()):
                tdbra.data[user]["exit"] = True
            while len(tdbra.data) > 0:
                time.sleep(0.4)
            break
        elif command == "status":
            users = []
            for user in list(tdbra.data.keys()):
                users.append(user)
            if len(users) == 0:
                tdbra.logger.info("No user is recording")
                continue
            tdbra.logger.info("Users recording:", users)
        elif command == "users":
            tdbra.logger.info("Users:", tdbra.conf["users"])
        elif command == "help":
            tdbra.logger.info("Available commands: exit, status, users, help")
        else:
            print(exec(command))
    pass

def statusChecker():
    while True:
        for user in tdbra.conf["users"]:
            if f"{user['name']}.{user['platform']}" in tdbra.data: continue

            if tdbra.m3u8.checkStatus(user["name"], user["platform"]):
                if f"{user['name']}.{user['platform']}" not in tdbra.data:
                    recordThread = Thread(target=tdbra.m3u8.worker, args=(user["name"], user["platform"]))
                    recordThread.daemon = True
                    newData = tdbra.create_data(user["name"], user["platform"], recordThread)
                    tdbra.data[f"{user['name']}.{user['platform']}"] = newData
                    recordThread.start()
                    tdbra.logger.debug(f"TDBRecord Record Thread for {user['name']}.{user['platform']} started!")
        
        time.sleep(60)
        pass