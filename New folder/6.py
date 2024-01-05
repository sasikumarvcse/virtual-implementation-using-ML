import cv2
import numpy as np
from kivy.uix.image import Image
from kivy.core.window import Window
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton


class HeartRateApp(App):
    def build(self):
        self.layout = BoxLayout(orientation='vertical')
        self.label = Label(text="Calculating heart rate, respiratory rate, and blood pressure...", font_size='20sp')
        self.layout.add_widget(self.label)

        self.start_stop_button = ToggleButton(text='Start', on_press=self.start_stop_recognition)
        self.layout.add_widget(self.start_stop_button)

        Clock.schedule_interval(self.update, 1.0 / 30.0)  # Update frame every 33ms (approximately 30fps)
        # Add background image
        background_image = Image(source='scopes.png', allow_stretch=True, keep_ratio=False)
        self.layout.add_widget(background_image)

        return self.layout

    def update(self, dt):
        if self.start_stop_button.state == 'down':
            # Capture frame from the camera
            cap = cv2.VideoCapture(0)
            ret, frame = cap.read()
            cap.release()

            # Preprocess the frame
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            blur = cv2.GaussianBlur(gray, (15, 15), 0)

            # Perform face detection
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            faces = face_cascade.detectMultiScale(blur, 1.1, 4)

            if len(faces) > 0:
                (x, y, w, h) = faces[0]
                roi = gray[y:y + h, x:x + w]
                mean_intensity = np.mean(roi)

                # Calculate heart rate from average intensity (example formula)
                heart_rate = 60 + (mean_intensity - 100) / 5

                # Calculate respiratory rate from chest movement
                chest_roi = gray[y + h:y + 2 * h, x:x + w]
                chest_intensity = np.mean(chest_roi)
                respiratory_rate = 15 + (chest_intensity - 100) / 5

                # Calculate blood pressure (example formula)
                blood_pressure = (heart_rate / respiratory_rate) * 25

                # Update label text with heart rate, respiratory rate, and blood pressure
                self.label.text = f"Heart Rate: {round(heart_rate)} BPM\nRespiratory Rate: {round(respiratory_rate)} BPM\nBlood Pressure: {round(blood_pressure)} mmHg\n "
            else:
                self.label.text = 'No face detected'

            if 'heart_rate' in locals():  # Check if the 'heart_rate' variable is defined
                if heart_rate < 60 or heart_rate > 100:
                    self.label.text += " \n(Your body is unfit)"
                else:
                    self.label.text += " \n(Your body is fit)"

                if heart_rate < 60 or heart_rate > 100:
                    self.label.text += " \n(Your heart rate is abnormal)"
                else:
                    self.label.text += " \n(Your heart rate is normal)"

                if respiratory_rate < 12 or respiratory_rate > 25:
                    self.label.text += " \n(Your respiratory rate is abnormal)"
                else:
                    self.label.text += " \n(Your respiratory rate is normal)"

                if blood_pressure < 80 or blood_pressure > 120:
                    self.label.text += " \n(Your blood pressure is abnormal)"
                else:
                    self.label.text += " \n(Your blood pressure is normal)"

    def start_stop_recognition(self, instance):
        if self.start_stop_button.state == 'down':
            self.start_stop_button.text = 'Stop'
        else:
            self.start_stop_button.text = 'Start'


if __name__ == '__main__':
    HeartRateApp().run()