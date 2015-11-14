aptitude install python-dev
pip install flask
pip install pyyaml
pip install rpi.gpio
if ! [ -f settings.yaml]
then
    python install.py
fi
