#############################################
# WiFi Scanner
#############################################
from kivy.app import App
from kivy.clock import mainthread
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button

from android import mActivity
from android.broadcast import BroadcastReceiver
from jnius import autoclass, cast

from android_permissions import AndroidPermissions

Context = autoclass('android.content.Context')
WifiManager = autoclass('android.net.wifi.WifiManager')

class MyApp(App):
    
    def build(self):
        self.label = Label(text='Press the button...')
        b = Button(text='Start WiFi Scan', on_press=self.check_permission)
        box = BoxLayout(orientation='vertical')
        box.add_widget(self.label)
        box.add_widget(b)
        return box

    def on_start(self):
        self.scan_num = 0
        self.br = None
        self.wm = cast('android.net.wifi.WifiManager',
                       mActivity.getSystemService(Context.WIFI_SERVICE))

    def check_permission(self, b):
        self.dont_gc = AndroidPermissions(self.start_scan)
        
    def start_scan(self):
        self.dont_gc = None
        if not self.br:
            action = WifiManager.SCAN_RESULTS_AVAILABLE_ACTION
            self.br = BroadcastReceiver(self.on_broadcast, actions=[action])
            self.br.start()
            if self.wm.startScan():
                self.label.text = 'Scanning.........'
            else:
                self.label.text = 'Start Scan Failed.\n' +\
                    'Android limits the WiFi scan count or rate.'

    def on_broadcast(self, context, intent):
        extras = intent.getExtras()
        if extras.get(WifiManager.EXTRA_RESULTS_UPDATED):
            text = 'Look what I found (Scan #'+str(self.scan_num)+'):\n\n'
            self.scan_num += 1
            for result in self.wm.getScanResults().toArray():
                if result.SSID:
                    text += result.SSID + '\n'
                else:
                    text += 'A WiFi with no SSID\n'
            self.update_label(text)
        self.br.stop()
        self.br = None
            
    @mainthread
    def update_label(self,text):
        self.label.text = text

MyApp().run()
