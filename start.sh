modprobe w1-gpio
modprobe w1-therm
python master.py &>> alarm.log &
sleep 20
python alarmFunctions.py &>> alarmFunctions.log &
