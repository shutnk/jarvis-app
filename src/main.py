from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.core.window import Window
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.utils import platform

Window.clearcolor = (0.03, 0.05, 0.1, 1)


class JarvisRoot(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", padding=40, spacing=20, **kwargs)
        self.listening = False

        title = Label(
            text="[b]J A R V I S[/b]",
            markup=True,
            font_size="42sp",
            color=(0.3, 0.8, 1, 1),
            size_hint=(1, 0.25),
        )
        self.add_widget(title)

        self.status = Label(
            text="Готов к запуску",
            font_size="20sp",
            color=(0.8, 0.9, 1, 1),
            size_hint=(1, 0.45),
        )
        self.add_widget(self.status)

        self.btn = Button(
            text="СЛУШАТЬ",
            font_size="24sp",
            background_color=(0.1, 0.5, 0.9, 1),
            size_hint=(1, 0.2),
        )
        self.btn.bind(on_press=self.on_listen)
        self.add_widget(self.btn)

        Clock.schedule_once(self.request_permissions, 0.5)

    def request_permissions(self, dt):
        if platform == "android":
            try:
                from android.permissions import request_permissions, Permission
                request_permissions([Permission.RECORD_AUDIO])
                self.status.text = "Разрешение на микрофон запрошено"
            except Exception as e:
                self.status.text = f"Ошибка разрешений: {e}"

    def animate_listening(self):
        self.btn.background_color = (0.9, 0.3, 0.3, 1)
        anim = Animation(font_size=28, duration=0.4) + Animation(font_size=24, duration=0.4)
        anim.repeat = True
        anim.start(self.btn)

    def stop_animation(self):
        Animation.cancel_all(self.btn)
        self.btn.font_size = 24
        self.btn.background_color = (0.1, 0.5, 0.9, 1)

    def speak(self, text):
        if platform == "android":
            try:
                from jnius import autoclass
                PythonActivity = autoclass("org.kivy.android.PythonActivity")
                TextToSpeech = autoclass("android.speech.tts.TextToSpeech")
                Locale = autoclass("java.util.Locale")
                tts = TextToSpeech(PythonActivity.mActivity, None)
                tts.setLanguage(Locale("ru", "RU"))
                tts.speak(text, TextToSpeech.QUEUE_FLUSH, None, "jarvis_tts")
                self.status.text = f"Джарвис: {text}"
            except Exception as e:
                self.status.text = f"Ошибка TTS: {e}"
        else:
            self.status.text = f"Джарвис: {text}"

    def on_listen(self, instance):
        if self.listening:
            return
        self.listening = True
        self.status.text = "Слушаю..."
        self.animate_listening()

        if platform == "android":
            try:
                from jnius import autoclass
                PythonActivity = autoclass("org.kivy.android.PythonActivity")
                Intent = autoclass("android.content.Intent")
                RecognizerIntent = autoclass("android.speech.RecognizerIntent")
                activity = PythonActivity.mActivity

                intent = Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH)
                intent.putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL,
                                RecognizerIntent.LANGUAGE_MODEL_FREE_FORM)
                intent.putExtra(RecognizerIntent.EXTRA_LANGUAGE, "ru-RU")
                intent.putExtra(RecognizerIntent.EXTRA_PROMPT, "Говорите...")

                # Запускаем распознавание через startActivityForResult
                from android import activity
                activity.bind(on_activity_result=self.on_activity_result)
                activity.startActivityForResult(intent, 1000)
            except Exception as e:
                self.status.text = f"Ошибка распознавания: {e}"
                self.listening = False
                self.stop_animation()
        else:
            Clock.schedule_once(lambda dt: self.process_result("Привет, я Джарвис"), 2)

    def on_activity_result(self, request_code, result_code, data):
        if request_code != 1000:
            return
        from android import activity
        activity.unbind(on_activity_result=self.on_activity_result)
        self.listening = False
        self.stop_animation()

        if result_code == -1 and data is not None:  # RESULT_OK
            try:
                results = data.getStringArrayListExtra("android.speech.extra.RESULTS")
                if results and results.size() > 0:
                    text = results.get(0)
                    self.status.text = f"Вы: {text}"
                    Clock.schedule_once(lambda dt: self.respond(text), 0.5)
                    return
            except Exception as e:
                self.status.text = f"Ошибка: {e}"
        self.status.text = "Не расслышал. Попробуйте ещё раз."

    def respond(self, text):
        text_lower = text.lower()
        if "привет" in text_lower or "здравствуй" in text_lower:
            answer = "Привет! Я Джарвис. Чем могу помочь?"
        elif "время" in text_lower:
            from datetime import datetime
            answer = f"Сейчас {datetime.now().strftime('%H:%M')}"
        elif "как дела" in text_lower:
            answer = "Всё отлично! Готов служить."
        else:
            answer = f"Вы сказали: {text}"
        self.speak(answer)


class JarvisApp(App):
    def build(self):
        self.title = "Jarvis"
        return JarvisRoot()


if __name__ == "__main__":
    JarvisApp().run()
