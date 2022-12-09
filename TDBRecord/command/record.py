import TDBRecord as tdbra

def record(user, platform):
    newData = tdbra.create_data(user, platform)
    tdbra.data[f"{user}.{platform}"] = newData
    tdbra.m3u8.worker(user, platform)
