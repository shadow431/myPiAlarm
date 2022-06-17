import time, commonFunc
time = time.time()
status = commonFunc.getYaml('status')
settings = commonFunc.getYaml('settings')
print("Checking")
for pi in status['checkIn']:
    print(str(pi)+" checked")
    if ((time - status['checkIn'][pi])/settings['checkinTime']) >= 1:
        print(str(pi)+" is stale")
        commonFunc.email('Pi: '+str(pi)+', hasn\'t checked in in the required amount of time')
