from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.properties import ObjectProperty, StringProperty, NumericProperty
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.gridlayout import GridLayout
from kivy.clock import Clock
from subprocess import call
from functools import partial
import urllib2, commonFunc, yaml
try:
    import RPi.GPIO as GPIO
except RuntimeError:
    print("Error import RPi.GPIO!  Are you sudo?")


#Set the Pin Numbering Mode: BOARD=the pin number on the board, BCM=the channel numbers
GPIO.setmode(GPIO.BOARD)
GPIO.setup(22,GPIO.OUT)
GPIO.output(22,1)

def getStatus(*args):
    settings = commonFunc.getYaml('settings')
    server = "http://"+settings['master']+"/getstatus"
    if len(args) > 0:
        server += "?get="+args[0]
    
    try: 
        status = yaml.load(urllib2.urlopen(server)) 
    except urllib2.URLError,e: 
        commonFunc.email("There was an error connecting to: "+server+"\nError:"+str(e))
        status={}
        if len(args) == 0:
            status['triggered']=[]

    return status 

class MainScreen(Screen):
    buttons = {'main':['alarm']}
    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)
    def on_enter(self):
        grid = GridLayout(cols=3)
        for btn in self.buttons[self.name]:
            button = MainButton(text=btn)
            button.bind(on_press=partial(app.change_view,btn,''))
            grid.add_widget(button)
        self.add_widget(grid)
    pass

class PinScreen(Screen):
    def __init__(self, **kwargs):
        super(PinScreen, self).__init__(**kwargs)
    def on_enter(self):
        grid = GridLayout(cols=3)
        for btn in ['1','2','3','4','5','6','7','8','9','*','0','#']:
            button = MainButton(text=btn)
            button.bind(on_press=partial(app.getPin,btn))
            grid.add_widget(button)
        clrBtn = MainButton(text='Clear')
        clrBtn.bind(on_press=app.clearPin)
        grid.add_widget(clrBtn)
        znBtn = MainButton(text=app.zone)
        znBtn.bind(on_press=partial(app.zoneSet,app.zone))
        grid.add_widget(znBtn)
        allBtn = MainButton(text='All Zones')
        allBtn.bind(on_press=partial(app.zoneSet,'*'))
        grid.add_widget(allBtn)
        self.add_widget(grid)
    pass

class AlarmScreen(Screen):
    def __init__(self, **kwargs):
        super(AlarmScreen, self).__init__(**kwargs)
    #    self.draw_grid()

    def on_enter(self):
        action = 'arm'
        grid = GridLayout(cols=3)
        zones = getStatus('zones')
        status = getStatus()
        for zone in zones:
            if zone in status['armed']:
                bgColor = [255,0,0,1]
            else:
                bgColor = [0,255,0,1]
            button = Button(text=zone,background_color=bgColor)
            button.bind(on_press=partial(app.change_view,'pin',zone))
            grid.add_widget(button)
        self.add_widget(grid)

class MainButton(Button):
    bgColor = [0,0,255,1]
    pass

class MainWidget(Widget):
    manager = ObjectProperty(None)
    pass

class uiApp(App):
    pin = ''
    zone = ''
    def scheduleBlank(self):
        Clock.unschedule(self.blackOut)
        Clock.schedule_once(self.blackOut,30)
    def clearPin(self,*args):
        self.pin=''
    def change_view(self, l, zone,*args):
        #d = ('left', 'up', 'down', 'right')
        #di = d.index(self.sm.transition.direction)
        #self.sm.transition.direction = d[(di + 1) % len(d)]i
        self.scheduleBlank()
        self.zone = zone
        self.sm.current = l

    def getPin(self, digit, *args):
        self.pin = self.pin + digit

    def zoneSet(self,zone,*args):
        self.scheduleBlank()
        settings = commonFunc.getYaml('settings')
        status = getStatus()
        if self.zone in status['armed']:
            action = 'disarm'
        else:
            action = 'arm'
        server = 'http://'+settings['master']+'/'+action+'?code='+self.pin+'&zone='+self.zone
        print server
        result = urllib2.urlopen(server)
        print result
        self.pin = ''
        self.sm.current = 'main'

    def build(self):
        root = Screen() 
        self.sm = sm = ScreenManager()

        sm.add_widget(MainScreen(name='main'))
        sm.add_widget(PinScreen(name='pin'))
        sm.add_widget(AlarmScreen(name='alarm'))

        root.add_widget(sm)
        return root

    def start(self):
        Clock.schedule_interval(self.callback, 1)
        Clock.schedule_once(self.blackOut,30)

    def callback(self, dt):
        if self.sm.current != 'pin':
            status = getStatus()
            if len(status['triggered']) > 0:
                self.zone = status['triggered'][0]
                self.sm.current = 'pin'
                return
    def blackOut(self,dt):
        print "Turn off screen"
        GPIO.output(22,1)
        return

if __name__ == '__main__':

    app = uiApp()
    app.start()
    app.run()
