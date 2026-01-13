import requests
from datetime import datetime, timedelta
from kivy.lang import Builder
from kivymd.app import MDApp
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.list import TwoLineAvatarListItem, OneLineListItem, IconLeftWidget, MDList
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.properties import StringProperty
from kivy.uix.screenmanager import ScreenManager, Screen

# --- KV Layout Language ---
KV = '''
<WeatherListItem>:
    theme_text_color: "Custom"
    text_color: 1, 1, 1, 1
    secondary_theme_text_color: "Custom"
    secondary_text_color: 0.7, 0.7, 0.7, 1
    # FIXED: Using IconLeftWidget instead of ImageLeftWidget
    IconLeftWidget:
        icon: root.icon_name
        theme_text_color: "Custom"
        text_color: 1, 0.6, 0, 1

<ManualListItem>:
    theme_text_color: "Custom"
    text_color: 1, 1, 1, 1
    IconLeftWidget:
        icon: root.icon_name
        theme_text_color: "Custom"
        text_color: 1, 0.6, 0, 1

ScreenManager:
    HomeScreen:
    AdminScreen:

<HomeScreen>:
    name: 'home'
    md_bg_color: 0.1, 0.1, 0.1, 1

    MDBoxLayout:
        orientation: 'vertical'
        padding: "10dp"
        spacing: "10dp"

        # --- Top Bar ---
        MDBoxLayout:
            size_hint_y: None
            height: "50dp"
            MDLabel:
                text: "Weather App"
                font_style: "H6"
                theme_text_color: "Custom"
                text_color: 1, 1, 1, 1
            MDIconButton:
                icon: "cog"
                theme_text_color: "Custom"
                text_color: 1, 1, 1, 1
                on_release: app.show_password_dialog()

        # --- Search Bar ---
        MDBoxLayout:
            size_hint_y: None
            height: "50dp"
            spacing: "10dp"
            MDTextField:
                id: search_input
                hint_text: "City or Pincode"
                mode: "rectangle"
                text_color_focus: 1, 1, 1, 1
                line_color_focus: 1, 0.6, 0, 1
                icon_right: "magnify"
            MDIconButton:
                icon: "magnify"
                theme_text_color: "Custom"
                text_color: 1, 0.6, 0, 1
                on_release: app.search_location()

        # --- Main Card ---
        MDCard:
            orientation: 'vertical'
            padding: "15dp"
            size_hint_y: None
            height: "180dp"
            radius: [20]
            md_bg_color: 0.2, 0.2, 0.2, 1
            MDLabel:
                id: location_label
                text: "Location"
                halign: "center"
                font_style: "H5"
                theme_text_color: "Custom"
                text_color: 1, 1, 1, 1
            MDBoxLayout:
                orientation: 'horizontal'
                MDIcon:
                    id: current_icon
                    icon: "weather-cloudy"
                    halign: "center"
                    font_size: "60sp"
                    theme_text_color: "Custom"
                    text_color: 1, 0.6, 0, 1
                MDLabel:
                    id: temp_label
                    text: "--"
                    halign: "center"
                    font_style: "H3"
                    theme_text_color: "Custom"
                    text_color: 1, 1, 1, 1
            MDLabel:
                id: desc_label
                text: "---"
                halign: "center"
                theme_text_color: "Secondary"

        # --- Forecast ---
        MDLabel:
            id: forecast_title
            text: "Forecast"
            size_hint_y: None
            height: "30dp"
            theme_text_color: "Custom"
            text_color: 1, 0.6, 0, 1
        ScrollView:
            MDList:
                id: forecast_list

<AdminScreen>:
    name: 'admin'
    md_bg_color: 0.1, 0.1, 0.1, 1
    MDBoxLayout:
        orientation: 'vertical'
        padding: "20dp"
        spacing: "10dp"
        MDLabel:
            text: "Admin: 30-Day Planner"
            font_style: "H6"
            theme_text_color: "Custom"
            text_color: 1, 1, 1, 1
            size_hint_y: None
            height: "40dp"
        MDBoxLayout:
            size_hint_y: None
            height: "50dp"
            MDLabel:
                text: "Enable Manual Mode"
                theme_text_color: "Custom"
                text_color: 1, 1, 1, 1
            MDSwitch:
                id: manual_switch
                active: False
                on_active: app.toggle_manual_mode(self, self.active)
        MDLabel:
            text: "Tap a day to edit:"
            theme_text_color: "Secondary"
            size_hint_y: None
            height: "30dp"
        ScrollView:
            MDList:
                id: admin_list
        MDFillRoundFlatButton:
            text: "Save & Go Back"
            pos_hint: {"center_x": 0.5}
            on_release: app.go_home()
'''

class HomeScreen(Screen): pass
class AdminScreen(Screen): pass

# FIXED: We now use icon_name instead of source url
class WeatherListItem(TwoLineAvatarListItem):
    icon_name = StringProperty("weather-cloudy") 

class ManualListItem(TwoLineAvatarListItem):
    icon_name = StringProperty("help")

class WeatherApp(MDApp):
    # ===============================================
    # PASTE YOUR API KEY HERE
    api_key = "627be999cb5eeb973cfed3159869f8bf"
    # ===============================================

    manual_mode = False
    manual_data = {} 
    
    weather_types = {
        "Sunny": {"icon": "weather-sunny", "desc": "Bright sun. High UV."},
        "Partly Cloudy": {"icon": "weather-partly-cloudy", "desc": "Sun & clouds."},
        "Cloudy": {"icon": "weather-cloudy", "desc": "Overcast, no sun."},
        "Rainy": {"icon": "weather-rainy", "desc": "Rainfall. Take umbrella."},
        "Storm": {"icon": "weather-lightning", "desc": "Thunder & Lightning."},
        "Snow": {"icon": "weather-snowy", "desc": "Freezing snow."},
        "Foggy": {"icon": "weather-fog", "desc": "Low visibility fog."},
        "Windy": {"icon": "weather-windy", "desc": "High winds."}
    }

    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Orange"
        for i in range(1, 31):
            self.manual_data[i] = "Sunny"
        return Builder.load_string(KV)

    # --- PASSWORD SYSTEM ---
    def show_password_dialog(self):
        content = MDBoxLayout(orientation="vertical", size_hint_y=None, height="50dp")
        self.pw_input = MDTextField(hint_text="Password", password=True)
        content.add_widget(self.pw_input)

        self.pass_dialog = MDDialog(
            title="Admin Login",
            type="custom",
            content_cls=content,
            buttons=[
                MDFlatButton(text="CANCEL", on_release=lambda x: self.pass_dialog.dismiss()),
                MDFlatButton(text="LOGIN", on_release=self.check_password)
            ]
        )
        self.pass_dialog.open()

    def check_password(self, obj):
        if self.pw_input.text == "190088":
            self.pass_dialog.dismiss()
            self.open_admin_panel()
        else:
            self.pass_dialog.title = "Wrong Password!"

    # --- ADMIN LOGIC ---
    def open_admin_panel(self):
        self.root.current = 'admin'
        self.refresh_admin_list()

    def refresh_admin_list(self):
        admin_list = self.root.get_screen('admin').ids.admin_list
        admin_list.clear_widgets()
        for day in range(1, 31):
            w_type = self.manual_data[day]
            icon = self.weather_types[w_type]["icon"]
            item = ManualListItem(
                text=f"Day {day}",
                secondary_text=f"{w_type}",
                icon_name=icon,
                on_release=lambda x, d=day: self.open_weather_selector(d)
            )
            admin_list.add_widget(item)

    def open_weather_selector(self, day_num):
        content = MDBoxLayout(orientation="vertical", size_hint_y=None, height="300dp")
        scroll = ScrollView()
        list_container = MDList()
        for w_name in self.weather_types:
            item = OneLineListItem(text=w_name, on_release=lambda x, w=w_name, d=day_num: self.set_manual_weather(d, w))
            list_container.add_widget(item)
        scroll.add_widget(list_container)
        content.add_widget(scroll)
        self.select_dialog = MDDialog(
            title=f"Set Weather: Day {day_num}",
            type="custom",
            content_cls=content,
            buttons=[MDFlatButton(text="CANCEL", on_release=lambda x: self.select_dialog.dismiss())]
        )
        self.select_dialog.open()

    def set_manual_weather(self, day, weather_name):
        self.manual_data[day] = weather_name
        self.select_dialog.dismiss()
        self.refresh_admin_list()

    def toggle_manual_mode(self, switch, active):
        self.manual_mode = active

    def go_home(self):
        self.root.current = 'home'
        if self.manual_mode: self.show_manual_forecast()

    # --- HELPER: CONVERT WEATHER ID TO ICON ---
    def get_icon_from_id(self, weather_id):
        if 200 <= weather_id <= 232: return "weather-lightning"
        elif 300 <= weather_id <= 531: return "weather-rainy"
        elif 600 <= weather_id <= 622: return "weather-snowy"
        elif 701 <= weather_id <= 781: return "weather-fog"
        elif weather_id == 800: return "weather-sunny"
        elif weather_id >= 801: return "weather-cloudy"
        else: return "weather-partly-cloudy"

    # --- SEARCH LOGIC ---
    def search_location(self):
        if self.manual_mode:
            self.show_alert("Manual Mode On", "Turn off Manual Mode to use Search.")
            return

        query = self.root.get_screen('home').ids.search_input.text.strip()
        if not query: return
        
        base = "http://api.openweathermap.org/data/2.5"
        key = self.api_key

        if query.isdigit() and len(query) == 6:
            url = f"{base}/weather?zip={query},IN&appid={key}&units=metric"
            url_f = f"{base}/forecast?zip={query},IN&appid={key}&units=metric"
        else:
            url = f"{base}/weather?q={query}&appid={key}&units=metric"
            url_f = f"{base}/forecast?q={query}&appid={key}&units=metric"

        self.get_api_weather(url, url_f)

    def get_api_weather(self, url_now, url_forecast):
        try:
            res = requests.get(url_now).json()
            if res.get('cod') == 401:
                self.show_alert("Error", "Invalid API Key")
                return
            if res.get('cod') != 200:
                self.show_alert("Error", "City not found")
                return
            
            # Update Current
            screen = self.root.get_screen('home')
            screen.ids.location_label.text = f"{res['name']}, {res['sys']['country']}"
            screen.ids.temp_label.text = f"{int(res['main']['temp'])}°C"
            screen.ids.desc_label.text = res['weather'][0]['description'].title()
            
            # Update Main Icon (OFFLINE METHOD)
            main_id = res['weather'][0]['id']
            screen.ids.current_icon.icon = self.get_icon_from_id(main_id)
            
            # Update Forecast
            res_f = requests.get(url_forecast).json()
            f_list = screen.ids.forecast_list
            f_list.clear_widgets()
            screen.ids.forecast_title.text = "5-Day Live Forecast"

            for item in res_f['list'][::8]:
                date = datetime.fromtimestamp(item['dt']).strftime('%a %d')
                temp = f"{int(item['main']['temp'])}°C"
                desc = item['weather'][0]['description'].title()
                
                # Get Icon ID and convert to Name (OFFLINE METHOD)
                w_id = item['weather'][0]['id']
                icon_name = self.get_icon_from_id(w_id)
                
                f_list.add_widget(WeatherListItem(
                    text=f"{date} | {temp}",
                    secondary_text=desc,
                    icon_name=icon_name
                ))
        except:
            self.show_alert("Error", "Connection Failed")

    def show_manual_forecast(self):
        screen = self.root.get_screen('home')
        screen.ids.location_label.text = "Manual Mode"
        screen.ids.temp_label.text = "Plan"
        screen.ids.desc_label.text = "30-Day Custom"
        screen.ids.forecast_title.text = "30-Day Custom Plan"
        
        f_list = screen.ids.forecast_list
        f_list.clear_widgets()
        today = datetime.now()
        
        for d in range(1, 31):
            w_type = self.manual_data[d]
            w_info = self.weather_types[w_type]
            date_str = (today + timedelta(days=d-1)).strftime('%a %d')
            
            f_list.add_widget(ManualListItem(
                text=f"{date_str} | {w_type}",
                secondary_text=w_info["desc"],
                icon_name=w_info["icon"]
            ))

    def show_alert(self, title, text):
        MDDialog(title=title, text=text, buttons=[MDFlatButton(text="OK", on_release=lambda x: x.dismiss())]).open()

if __name__ == '__main__':
    WeatherApp().run()
