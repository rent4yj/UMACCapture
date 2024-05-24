import tkinter as tk
from tkinter import simpledialog
from PIL import ImageGrab
import pyautogui
import time
import threading
import os
import json
from datetime import datetime

class ScreenCaptureApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Screen Capture App")
        self.root.geometry("300x350")
        self.interval = 1
        self.capturing = False
        self.config_file = "config.json"

        self.interval_label = tk.Label(root, text="Capture Interval (seconds):")
        self.interval_label.pack(pady=5)
        
        self.interval_entry = tk.Entry(root)
        self.interval_entry.pack(pady=5)
        
        self.set_interval_button = tk.Button(root, text="Set Interval", command=self.set_interval)
        self.set_interval_button.pack(pady=5)
        
        self.start_button = tk.Button(root, text="Start Capture", command=self.start_capture)
        self.start_button.pack(pady=5)
        
        self.stop_button = tk.Button(root, text="Stop Capture", command=self.stop_capture)
        self.stop_button.pack(pady=5)

        self.rect = None
        self.start_x = None
        self.start_y = None
        self.cur_x = None
        self.cur_y = None

        self.capture_area_button = tk.Button(root, text="Set Capture Area", command=self.set_capture_area)
        self.capture_area_button.pack(pady=5)
        
        self.load_config()

    def set_interval(self):
        try:
            self.interval = int(self.interval_entry.get())
            print(f"Capture interval set to {self.interval} seconds.")
        except ValueError:
            print("Please enter a valid number for the interval.")

    def start_capture(self):
        if self.capture_area:
            self.capturing = True
            self.capture_thread = threading.Thread(target=self.capture_loop)
            self.capture_thread.start()
            print("Screen capture started.")

    def stop_capture(self):
        self.capturing = False
        if hasattr(self, 'capture_thread') and self.capture_thread.is_alive():
            self.capture_thread.join()
        print("Screen capture stopped.")

    def set_capture_area(self):
        self.capture_area_window = tk.Toplevel(self.root)
        self.capture_area_window.attributes("-fullscreen", True)
        self.capture_area_window.attributes("-alpha", 0.3)
        
        self.canvas = tk.Canvas(self.capture_area_window, cursor="cross", bg="grey11")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        self.canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_mouse_move)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)

    def on_button_press(self, event):
        self.start_x = event.x
        self.start_y = event.y
        if self.rect:
            self.canvas.delete(self.rect)
        self.rect = self.canvas.create_rectangle(self.start_x, self.start_y, self.start_x, self.start_y, outline='red')

    def on_mouse_move(self, event):
        self.cur_x, self.cur_y = (event.x, event.y)
        self.canvas.coords(self.rect, self.start_x, self.start_y, self.cur_x, self.cur_y)

    def on_button_release(self, event):
        self.cur_x, self.cur_y = (event.x, event.y)
        self.capture_area_window.destroy()
        self.capture_area = (self.start_x, self.start_y, self.cur_x, self.cur_y)
        self.save_config()
        print(f"Capture area set to: {self.capture_area}")

    def capture_loop(self):
        while self.capturing:
            self.capture_screen()
            time.sleep(self.interval)

    def capture_screen(self):
        if self.capture_area:
            x1, y1, x2, y2 = self.capture_area
            img = ImageGrab.grab(bbox=(x1, y1, x2, y2))
            filename = datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".png"
            img.save(filename)
            print(f"Captured {filename}")

    def save_config(self):
        config = {
            "capture_area": self.capture_area,
            "interval": self.interval
        }
        with open(self.config_file, 'w') as f:
            json.dump(config, f)

    def load_config(self):
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                config = json.load(f)
                self.capture_area = tuple(config.get("capture_area", ()))
                self.interval = config.get("interval", 1)
                self.interval_entry.insert(0, str(self.interval))
                print(f"Loaded config: {config}")
        else:
            self.capture_area = None

if __name__ == "__main__":
    root = tk.Tk()
    app = ScreenCaptureApp(root)
    root.mainloop()
