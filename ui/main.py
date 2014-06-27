from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.properties import ObjectProperty
from kivy.uix.screenmanager import ScreenManager, Screen
from subprocess import call

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


if __name__ == '__main__':
    uiApp().run()
