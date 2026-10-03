from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.core.window import Window
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.utils import platform
import threading
import os

Window.clearcolor = (0.03, 0.05, 0.1, 1)


class JarvisRoot(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", padding=40, spacing=20, **kwargs)
        self.listening = False
        self.recognizer = None
        self.listener = None

        title = Label(
            text="[b]J A R V I S[/b]",
            markup=True, font_size="42sp",
            color=(0.3, 0.8, 1, 1), size_hint=(1, 0.25),
        )
        self.add_widget(title)

        self.status = Label(
            text="Готов к запуску",
            font_size="20sp", color=(0.8, 0.9, 1, 1), size_hint=(1, 0.45),
        )
        self.add_widget(self.status)

        self.btn = Button(
            text="СЛУШАТЬ", font_size="24sp",
            background_color=(0.1, 0.5, 0.9, 1), size_hint=(1, 0.2),
        )
        self.btn.bind(on_press=self.on_listen)
        self.add_widget(self.btn)

        Clock.schedule_once(self.request_permissions, 0.5)

    def request_permissions(self, dt):
        if platform == "android":
            try:
                from android.permissions import request_permissions, Permission
                request_permissions([Permission.RECORD_AUDIO, Permission.INTERNET])
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
        """Озвучка через gTTS + MediaPlayer (надёжно, но нужен интернет)."""
        if platform == "android":
            def _do_speak():
                try:
                    from gtts import gTTS
                    from jnius import autoclass, cast
                    from android.runnable import run_on_ui_thread

                    # Генерируем mp3 через gTTS
                    tts = gTTS(text=text, lang='ru')
                    mp3_path = os.path.join(os.path.expanduser("~"), "jarvis_tts.mp3")
                    tts.save(mp3_path)
                    print(f"MP3 saved: {mp3_path}")

                    @run_on_ui_thread
                    def play():
                        try:
                            MediaPlayer = autoclass("android.media.MediaPlayer")
                            File = autoclass("java.io.File")
                            FileInputStream = autoclass("java.io.FileInputStream")

                            player = MediaPlayer()
                            fis = FileInputStream(File(mp3_path))
                            fd = fis.getFD()
                            player.setDataSource(fd)
                            fis.close()
                            player.prepare()
                            player.start()
                            print("MediaPlayer started")
                        except Exception as e:
                            print(f"MediaPlayer error: {e}")

                    play()
                except Exception as e:
                    print(f"gTTS/MediaPlayer error: {e}")
                    # fallback на Android TTS
                    self._speak_native(text)

            threading.Thread(target=_do_speak, daemon=True).start()
            self.status.text = f"Джарвис: {text}"
        else:
            self.status.text = f"Джарвис: {text}"

    def _speak_native(self, text):
        """Fallback: встроенный Android TTS."""
        try:
            from jnius import autoclass
            from android.runnable import run_on_ui_thread
            PythonActivity = autoclass("org.kivy.android.PythonActivity")
            TextToSpeech = autoclass("android.speech.tts.TextToSpeech")
            Locale = autoclass("java.util.Locale")

            @run_on_ui_thread
            def do_speak():
                try:
                    tts = TextToSpeech(PythonActivity.mActivity, None)
                    tts.setLanguage(Locale("ru", "RU"))
                    tts.speak(text, 0, None, "jarvis_tts")
                    print("Native TTS speak called")
                except Exception as e:
                    print(f"Native TTS error: {e}")

            do_speak()
        except Exception as e:
            print(f"Native TTS init error: {e}")

    def on_listen(self, instance):
        if self.listening:
            return
        self.listening = True
        self.status.text = "Слушаю..."
        self.animate_listening()

        if platform == "android":
            try:
                from jnius import autoclass, PythonJavaClass, java_method
                from android.runnable import run_on_ui_thread
                SpeechRecognizer = autoclass("android.speech.SpeechRecognizer")
                RecognizerIntent = autoclass("android.speech.RecognizerIntent")
                Intent = autoclass("android.content.Intent")
                PythonActivity = autoclass("org.kivy.android.PythonActivity")

                app = self

                class RecognitionListener(PythonJavaClass):
                    __javainterfaces__ = ["android/speech/RecognitionListener"]
                    __javacontext__ = "app"

                    @java_method("(Landroid/os/Bundle;)V")
                    def onReadyForSpeech(self, params):
                        pass

                    @java_method("()V")
                    def onBeginningOfSpeech(self):
                        pass

                    @java_method("(F)V")
                    def onRmsChanged(self, rmsdB):
                        pass

                    @java_method("([B)V")
                    def onBufferReceived(self, buffer):
                        pass

                    @java_method("()V")
                    def onEndOfSpeech(self):
                        pass

                    @java_method("(I)V")
                    def onError(self, error):
                        app.status.text = f"Ошибка распознавания: {error}"
                        app.listening = False
                        app.stop_animation()

                    @java_method("(Landroid/os/Bundle;)V")
                    def onResults(self, results):
                        try:
                            matches = results.getStringArrayList(
                                SpeechRecognizer.RESULTS_RECOGNITION)
                            if matches and matches.size() > 0:
                                text = matches.get(0)
                                app.status.text = f"Вы: {text}"
                                Clock.schedule_once(lambda dt: app.respond(text), 0.5)
                            else:
                                app.status.text = "Не расслышал"
                        except Exception as e:
                            app.status.text = f"Ошибка: {e}"
                        app.listening = False
                        app.stop_animation()

                    @java_method("(Landroid/os/Bundle;)V")
                    def onPartialResults(self, partialResults):
                        pass

                    @java_method("(Landroid/os/Bundle;)V")
                    def onEvent(self, eventType, params):
                        pass

                @run_on_ui_thread
                def start_recognition():
                    activity = PythonActivity.mActivity
                    app.recognizer = SpeechRecognizer.createSpeechRecognizer(activity)
                    app.listener = RecognitionListener()
                    app.recognizer.setRecognitionListener(app.listener)

                    intent = Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH)
                    intent.putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL,
                                    RecognizerIntent.LANGUAGE_MODEL_FREE_FORM)
                    intent.putExtra(RecognizerIntent.EXTRA_LANGUAGE, "ru-RU")
                    app.recognizer.startListening(intent)

                start_recognition()

            except Exception as e:
                self.status.text = f"Ошибка: {e}"
                self.listening = False
                self.stop_animation()
        else:
            Clock.schedule_once(lambda dt: self.respond("Привет"), 2)

    def respond(self, text):
        text_lower = text.lower()
        if "привет" in text_lower or "здравствуй" in text_lower:
            answer = "Привет! Я Джарвис."
        elif "время" in text_lower:
            from datetime import datetime
            answer = f"Сейчас {datetime.now().strftime('%H:%M')}"
        elif "как дела" in text_lower:
            answer = "Всё отлично!"
        else:
            answer = f"Вы сказали: {text}"
        self.speak(answer)


class JarvisApp(App):
    def build(self):
        self.title = "Jarvis"
        return JarvisRoot()


if __name__ == "__main__":
    JarvisApp().run()
