import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
import requests

class MainScreen(BoxLayout):
    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)
        self.orientation = 'vertical'
        
        # At startup, we want to fetch houses from the API
        self.populate_houses()

    def populate_houses(self):
        # Replace with your backend URL
        api_url = "http://127.0.0.1:8000/api/houses/"
        try:
            response = requests.get(api_url)
            if response.status_code == 200:
                houses_data = response.json()
                # We will just list house names for now
                scroll = ScrollView()
                content = BoxLayout(orientation='vertical', size_hint_y=None)
                content.bind(minimum_height=content.setter('height'))
                
                for house in houses_data:
                    # house['house_name'] should be a field from your serializer
                    house_name = house.get('house_name', 'No Name')
                    lbl = Label(text=house_name, size_hint_y=None, height=40)
                    content.add_widget(lbl)
                
                scroll.add_widget(content)
                self.add_widget(scroll)
            else:
                self.add_widget(Label(text="Error fetching houses"))
        except Exception as e:
            self.add_widget(Label(text=f"Exception: {e}"))

class MakazihubApp(App):
    def build(self):
        return MainScreen()

if __name__ == '__main__':
    MakazihubApp().run()
