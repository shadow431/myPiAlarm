modprobe w1-gpio
modprobe w1-therm
python3 master.py &>> alarm.log &
sleep 20
python3 alarmFunctions.py &>> alarmFunctions.log &
