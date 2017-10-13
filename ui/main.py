from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.behaviors import *
from kivy.config import Config
from kivy.properties import ObjectProperty, StringProperty, NumericProperty
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.gridlayout import GridLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.graphics import *
from kivy.uix.image import *
from kivy.cache import Cache
from kivy.clock import Clock
from subprocess import call
from functools import partial
import urllib2, commonFunc, yaml,os,sys, zipfile
try:
    import RPi.GPIO as GPIO
    hasGPIO = True
except RuntimeError:
    print("Error import RPi.GPIO!  Are you sudo?")
except:
    hasGPIO = False

settings = commonFunc.getYaml('settings')

if hasGPIO:
    #Set the Pin Numbering Mode: BOARD=the pin number on the board, BCM=the channel numbers
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(settings['motionPin'],GPIO.IN)

def getStatus(*args):
    settings = commonFunc.getYaml('settings')
    server = "http://"+settings['master']+"/getstatus" #CONFIG
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

def getPos(config='',cols=3,rows=2):
  return (100,100)

class Background():
    photos = []
    curImage = ''
    def __init__(self):
        self.nextImage()

    def image(self):
        return self.curImage

    def nextImage(self):
        if (len(self.photos) > 0):
            img=self.photos.pop()
        else:
            self.getImages()
            img = self.nextImage()
        self.curImage = img
        return img

    def getImages(self):
        if not os.path.isdir('download'):
            os.makedirs('download')
        if not os.path.isdir('tmp'):
            os.makedirs('tmp')
        folder = './tmp/'
        for the_file in os.listdir(folder):
            file_path = os.path.join(folder, the_file)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            except Exception, e:
                print e
        try:
            f = urllib2.urlopen('http://192.168.22.14:3000/retrieve?res=800x480') #CONFIG
            with open('./download/photos.zip',"wb") as local_file:
                local_file.write(f.read())
        except:
            print "Error"
        fh = open('./download/photos.zip','rb')
        z = zipfile.ZipFile(fh)
        for name in z.namelist():
          z.extract(name,'./tmp/')
        fh.close()
        rootPath = './tmp/'
        self.photos = []
        a = True
        for image in os.listdir(rootPath):
            if 'JPG' in image:
                self.photos.append(rootPath + image)

class BlankScreen(Screen):
    settings = commonFunc.getYaml('settings')
    def __init__(self, **kwargs):
        self.bgImage = kwargs['background']
        super(BlankScreen, self).__init__(**kwargs)
    def on_enter(self):
        grid = GridLayout()
        self.grid2 = AnchorLayout()
        self.bg = ImgButton(size=(800,480)) #CONFIG
        self.bg.source = self.bgImage.image()
        self.bg.bind(on_press=partial(app.change_view,'main'))
        self.grid2.add_widget(self.bg)
        self.add_widget(self.grid2)
        self.add_widget(grid)

    def on_leave(self):
        self.remove_widget(self.grid2)

class MainScreen(Screen):
    buttons = {'main':['alarm','poweroff']}
    settings = commonFunc.getYaml('settings')
    def __init__(self, **kwargs):
        self.bgImage = kwargs['background']
        super(MainScreen, self).__init__(**kwargs)
    def on_enter(self):
        grid = GridLayout(cols=3,rows=3)
        self.grid2 = AnchorLayout()
        self.bg = ImgButton(size=(800,480)) #CONFIG
        self.bg.source = self.bgImage.image()
        self.bg.bind(on_press=partial(app.change_view,'main'))
        self.grid2.add_widget(self.bg)
        btnNum = 0
        for btn in self.buttons[self.name]:
            button = MainButton(text=btn,pos=getPos())
            button.bind(on_press=partial(app.change_view,btn,''))
            grid.add_widget(button)
            btnNum += 1
        while btnNum < 9:
            button = EmptyButton(pos=getPos())
            button.bind()
            grid.add_widget(button)
            btnNum += 1
        self.add_widget(self.grid2)
        self.add_widget(grid)
        Clock.schedule_interval(self.callback,self.settings['timeOut']) #CONFIG

    def on_leave(self):
        Clock.unschedule(self.callback)
        self.remove_widget(self.grid2)

    def callback(self,instalnce):
        self.bg.source=self.bgImage.nextImage()

class PoweroffScreen(Screen):
    def __init__(self, **kwargs):
        super(PoweroffScreen, self).__init__(**kwargs)
    def on_enter(self):
        grid = GridLayout(cols=3,rows=3)
        YesBtn = MainButton(text='Yes')
        YesBtn.bind(on_press=app.shutdown)
        grid.add_widget(YesBtn)
        NoBtn = MainButton(text='No')
        NoBtn.bind(on_press=partial(app.change_view,'main'))
        grid.add_widget(NoBtn)
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
class ImgButton(ButtonBehavior, AsyncImage):
    pass

class ImageScreen(Screen):
    settings = commonFunc.getYaml('settings')
    def __init__(self, **kwargs):
        self.bgImg = kwargs['background']
        super(ImageScreen, self).__init__(**kwargs)

    def on_enter(self):
        self.grid = AnchorLayout()
        self.img = ImgButton(size=(800,480)) #CONFIG
        self.img.source=self.bgImg.image()
        self.img.bind(on_press=partial(app.change_view,'main'))
        self.grid.add_widget(self.img)
        self.add_widget(self.grid)
        Clock.schedule_interval(self.callback,self.settings['imageDwel']) #CONFIG

    def on_leave(self):
        Clock.unschedule(self.callback)
        self.remove_widget(self.grid)

    def callback(self,instalnce):
        self.img.source=self.bgImg.nextImage()

class MainButton(Button):
    bgColor = [0,0,255,1]
    pass

class EmptyButton(Button):
    bgColor = [255,0,0,0]
    pass

class MainWidget(Widget):
    manager = ObjectProperty(None)
    pass

class uiApp(App):
    settings = commonFunc.getYaml('settings')
    pin = ''
    zone = ''
    bg = Background() 
    def build_config(self, config):
        config.setdefaults('graphics',{'fullscreen':1,'hieght':480,'width':800}) #CONFIG
    def scheduleBlank(self):
        Clock.unschedule(self.photoFrame)
        Clock.schedule_once(self.photoFrame,30)
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

    def shutdown(self,*args):
        os.system('sudo shutdown -h now')

    def zoneSet(self,zone,*args):
        self.scheduleBlank()
        settings = commonFunc.getYaml('settings')
        status = getStatus()
        if self.zone in status['armed']:
            action = 'disarm'
        else:
            action = 'arm'
        server = 'http://'+settings['master']+'/'+action+'?code='+self.pin+'&zone='+self.zone #CONFIG
        print server
        result = urllib2.urlopen(server)
        print result
        self.pin = ''
        self.sm.current = 'main'

    def build(self):
        config = self.config
        root = Screen() 
        self.sm = sm = ScreenManager()

        sm.add_widget(MainScreen(name='main',background=self.bg))
        sm.add_widget(PinScreen(name='pin',background=self.bg))
        sm.add_widget(AlarmScreen(name='alarm',background=self.bg))
        sm.add_widget(ImageScreen(name='image',background=self.bg))
        sm.add_widget(PoweroffScreen(name='poweroff',background=self.bg))
        sm.add_widget(BlankScreen(name='blank',background=self.bg))

        root.add_widget(sm)
        return root

    def start(self):
        self.backLightOn(self)
        #Clock.schedule_interval(self.callback, 1) #CONFIG ??? replacing with register and listen for issue
        Clock.schedule_once(self.photoFrame,self.settings['timeOut']) #CONFIG
        Clock.schedule_once(self.backLightOff,self.settings['blackOut']) #CONFIG
        GPIO.add_event_detect(self.settings['motionPin'], GPIO.RISING, callback=self.updateMotion, bouncetime=900) # Set up an interrupt to look for button presses

    def photoFrame(self, dt):
        self.sm.current = 'image'
        return

    def callback(self, dt):
        if self.sm.current != 'pin':
            status = getStatus()
            if len(status['triggered']) > 0:
                self.zone = status['triggered'][0]
                self.sm.current = 'pin'
                return
    def updateMotion(self,dt):
        self.backLightOn(self)
        Clock.unschedule(self.backLightOff)
        Clock.schedule_once(self.backLightOff,self.settings['blackOut'])
        return
    def backLightOff(self,dt):
        self.sm.current = 'blank'
        try: 
          backlight = open('/sys/class/backlight/rpi_backlight/bl_power','r+')
          backlight.write("1")
          backlight.close
        except:
            pass
        return
    def backLightOn(self,dt):
        try: 
          backlight = open('/sys/class/backlight/rpi_backlight/bl_power','r+')
          if backlight.read() == "1\n":
            backlight.write("0")
            self.sm.current = 'image'
          backlight.close
        except:
            pass
        return

if __name__ == '__main__':

    app = uiApp()
    app.start()
    app.run()
