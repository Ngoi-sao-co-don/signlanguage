from kivymd.app import MDApp
from kivymd.uix.label import MDLabel
from kivy.core.text import LabelBase
from kivymd.uix.screen import Screen



switch_camera ='''
MDIconButton:
    icon: "rotate-right"
    style: "standard"
    pos_hint:{'center_x':0.5,'center_y':0.5}
    theme_icon_color: "Custom"
    icon_color: "white"
    on_release: self.switch_camera_handler
'''


from kivy.uix.image import Image
from kivy.uix.camera import Camera
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivymd.uix.button import MDIconButton,MDFloatingActionButton, MDFlatButton
from kivy.uix.label import Label
from kivy.graphics import Color, Rectangle
from kivy.uix.togglebutton import ToggleButton
import cv2
import threading
import imutils
import socket, pickle, struct, time



class DemoApp(MDApp):

    def build(self):
        LabelBase.register("Poppins",
                           fn_regular="fonts/poppins_regular.ttf",
                           fn_bold="fonts/poppins_bold.ttf")
        
        screen = Screen()
        self.capture = cv2.VideoCapture(0)
        self.image = Image(fit_mode='cover')
        Clock.schedule_interval(self.update, 1.0 / 30.0)



        self.message = MDLabel(text='', halign='center', theme_text_color='Custom', text_color=(255 / 255.0,200/255.0,0,0.8),
                         font_style='Subtitle2', font_name='Poppins', pos_hint={'center_x': 0.5, 'center_y': 0.25})

        self.servermessage = "ok"

        self.micro_btn = MDIconButton(icon='microphone', pos_hint={'center_x': 0.2, 'center_y': 0.1},
                                      theme_icon_color="Custom",
                                      icon_color="white")

        self.setting_btn = MDIconButton(icon='adjust', pos_hint={'center_x': 0.9, 'center_y': 0.95},
                                      theme_icon_color="Custom",
                                      icon_color="white")

        self.start_btn = MDIconButton(icon='power', pos_hint={'center_x':0.5,'center_y':0.1},theme_icon_color= "Custom",
                             icon_color= "white",md_bg_color='red', on_release= self.start_stream)

        self.stop_btn = MDIconButton(icon='power-off', pos_hint={'center_x': 0.5, 'center_y': 0.1},
                                      theme_icon_color="Custom",
                                      icon_color="white", md_bg_color='red', on_release=self.stop_stream)




        self.switch_camera = MDIconButton(icon= "rotate-right",pos_hint={'center_x':0.8,'center_y':0.1},theme_icon_color= "Custom",
                             icon_color= "white",
                             on_release= self.switch_camera_handler)


        screen.add_widget(self.image)
        screen.add_widget(self.setting_btn)
        screen.add_widget(self.message)
        screen.add_widget(self.micro_btn)
        screen.add_widget(self.stop_btn)
        screen.add_widget(self.start_btn)

        screen.add_widget(self.switch_camera)


        return screen
    def update(self, dt):
        ret, frame = self.capture.read()
        if ret:
            buf1 = cv2.flip(frame, -1)
            buf = buf1.tobytes()
            texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
            texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
            self.image.texture = texture

    def on_stop(self):
        self.capture.release()

    def switch_camera_handler(self, obj):
        print("Handle switch camera later")

    def start_stream(self, instance):
        threading.Thread(target=lambda: self.send_frames(self.capture)).start()
        # Khi nút start được nhấn
        self.start_btn.opacity = 0  # Ẩn nút start
        self.start_btn.disabled = True  # Vô hiệu hóa nút start
        self.stop_btn.opacity = 1  # Hiện nút stop
        self.stop_btn.disabled = False  # Kích hoạt nút stop

    def stop_stream(self, instance):
        self.client_socket.close()
        # Khi nút stop được nhấn
        self.start_btn.opacity = 1  # Hiện nút start
        self.start_btn.disabled = False  # Kích hoạt nút start
        self.stop_btn.opacity = 0  # Ẩn nút stop
        self.stop_btn.disabled = True  # Vô hiệu hóa nút stop

    def send_frames(self, frame):
        camera = frame
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        host_ip = '192.168.200.1'
        port = 9999
        try:
            self.client_socket.connect((host_ip, port))
            while True:
                ret, frame = camera.read()
                frame = imutils.resize(frame, width=450)
                a = pickle.dumps(frame)
                message = struct.pack("Q", len(a)) + a
                self.client_socket.sendall(message)
                # Nhận và hiển thị thông điệp từ server
                try:
                    message = self.client_socket.recv(1024).decode()
                    print(message)
                    self.message.text = message
                    self.servermessage = message
                except:
                    pass
                #key = cv2.waitKey(1) & 0xFF
                # if key == ord("q"):
                #     break
        except Exception as e:
            self.message.text = "Kết nối đã bị gián đoạn"
            print(f'Error: {e}')

DemoApp().run()