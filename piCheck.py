import time, commonFunc
time = time.time()
status = commonFunc.getYaml('status')
settings = commonFunc.getYaml('settings')
for pi in status['checkIn']:
    if ((time - status['checkIn'][pi])/settings['checkinTime']) >= 1:
        commonFunc.email('Pi: '+str(pi)+', hasn\'t checked in in the required amount of time')
