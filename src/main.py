from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.core.window import Window

Window.clearcolor = (0.03, 0.05, 0.1, 1)


class JarvisRoot(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", padding=40, spacing=20, **kwargs)

        title = Label(
            text="[b]J A R V I S[/b]",
            markup=True,
            font_size="42sp",
            color=(0.3, 0.8, 1, 1),
            size_hint=(1, 0.3),
        )
        self.add_widget(title)

        self.status = Label(
            text="Готов к запуску",
            font_size="20sp",
            color=(0.8, 0.9, 1, 1),
            size_hint=(1, 0.4),
        )
        self.add_widget(self.status)

        btn = Button(
            text="СЛУШАТЬ",
            font_size="24sp",
            background_color=(0.1, 0.5, 0.9, 1),
            size_hint=(1, 0.2),
        )
        btn.bind(on_press=self.on_listen)
        self.add_widget(btn)

    def on_listen(self, instance):
        self.status.text = "Слушаю..."


class JarvisApp(App):
    def build(self):
        self.title = "Jarvis"
        return JarvisRoot()


if __name__ == "__main__":
    JarvisApp().run()
