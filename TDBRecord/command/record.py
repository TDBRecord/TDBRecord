import TDBRecord as tdbra

def record(user, platform):
    if tdbra.m3u8.checkStatus(user, platform):
        tdbra.logger.info(f"Recording {user} on {platform}")
        newData = tdbra.create_data(user, platform)
        tdbra.data[f"{user}.{platform}"] = newData
        tdbra.m3u8.worker(user, platform)
    else:
        tdbra.logger.error(f"Failed to record {user} on {platform}. Is stream online?")
