apt install python-dev
pip install flask
pip install pyyaml
pip install rpi.gpio
#if ! [ -f settings.yaml]
#then
#    python install.py
#fi
git clone https://github.com/SequentMicrosystems/16inputs-rpi.git
cd 16inputs-rpi/python/16inputs
python3 setup.py install
