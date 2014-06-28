from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.properties import ObjectProperty
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.clock import Clock
from subprocess import call
import urllib2, commonFunc, yaml


def getStatus():
    settings = commonFunc.getYaml('settings')
    server = "http://"+settings['master']+"/getstatus" 
    while True: 
        try: 
            status = yaml.load(urllib2.urlopen(server)) 
        except urllib2.URLError,e: 
            commonFunc.email("There was an error connecting to: "+server+"\nError:"+str(e))
            status={}
            status['triggered']=[]
            continue  
        break 
    return status 

class MainScreen(Screen):
    pass

class PinScreen(Screen):
    pass

class AlarmScreen(Screen):
    pass

class MainButton(Button):
    bgColor = [0,0,255,1]
    pass

class MainWidget(Widget):
    manager = ObjectProperty(None)
    pass

class uiApp(App):
    pin = ''
    def change_view(self, l):
        #d = ('left', 'up', 'down', 'right')
        #di = d.index(self.sm.transition.direction)
        #self.sm.transition.direction = d[(di + 1) % len(d)]
        self.sm.current = l

    def getPin(self, digit):
        self.pin = self.pin + digit
    def disarm(self,zone):
        print(self.pin)
        self.pin = ''
        self.sm.current = 'alarm'

    def remove_screen(self, *l):
        self.sm.remove_widget(self.sm.get_screen('test1'))
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

    def callback(self, dt):
        if self.sm.current != 'pin':
            status = getStatus()
            if len(status['triggered']) > 0:
                self.sm.current = 'pin'

if __name__ == '__main__':

    app = uiApp()
    app.start()
    app.run()
