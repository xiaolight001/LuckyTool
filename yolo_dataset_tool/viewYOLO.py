import os
import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import xml.etree.ElementTree as ET

class ImageLabelViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("YOLO 和 XML 标注查看器")

        self.image_folder = ""
        self.label_folder = ""
        self.image_list = []
        self.current_index = 0
        self.class_colors = {}
        
        self.label = tk.Label(root, text="请选择图像文件夹和标签文件夹", font=("Arial", 16))
        self.label.pack(pady=10)
        
        self.load_button = tk.Button(root, text="选择图像文件夹", command=self.select_image_folder)
        self.load_button.pack(pady=5)
        
        self.load_label_button = tk.Button(root, text="选择标签文件夹", command=self.select_label_folder)
        self.load_label_button.pack(pady=5)
        
        self.prev_button = tk.Button(root, text="上一张", command=self.show_prev_image, state=tk.DISABLED)
        self.prev_button.pack(side=tk.LEFT, padx=20, pady=20)
        
        self.next_button = tk.Button(root, text="下一张", command=self.show_next_image, state=tk.DISABLED)
        self.next_button.pack(side=tk.RIGHT, padx=20, pady=20)
        
        self.canvas = tk.Canvas(root, width=800, height=600)
        self.canvas.pack(padx=10, pady=10)
    
    def select_image_folder(self):
        self.image_folder = filedialog.askdirectory(title="选择图像文件夹")
        if self.image_folder:
            self.image_list = sorted([f for f in os.listdir(self.image_folder) if f.endswith(('.jpg', '.png'))])
            self.current_index = 0
            self.show_image()
    
    def select_label_folder(self):
        self.label_folder = filedialog.askdirectory(title="选择标签文件夹")
        if self.label_folder:
            self.show_image()
    
    def show_image(self):
        if not self.image_list:
            return
        
        image_path = os.path.join(self.image_folder, self.image_list[self.current_index])
        label_path_txt = os.path.join(self.label_folder, os.path.splitext(self.image_list[self.current_index])[0] + ".txt")
        
        boxes = self.read_yolo_labels(label_path_txt) if os.path.exists(label_path_txt) else []
        
        image = cv2.imdecode(np.fromfile(image_path, dtype=np.uint8), cv2.IMREAD_COLOR)
        if image is None:
            messagebox.showerror("错误", "无法读取图像")
            return
        
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        for class_id, x1, y1, x2, y2 in boxes:
            if class_id not in self.class_colors:
                self.class_colors[class_id] = tuple(np.random.randint(0, 255, 3).tolist())
            
            color = self.class_colors[class_id]
            cv2.rectangle(image, (x1, y1), (x2, y2), color, 2)
            cv2.putText(image, str(class_id), (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        
        self.display_image(image)
        self.update_buttons()
    
    def display_image(self, image):
        canvas_width, canvas_height = self.canvas.winfo_width(), self.canvas.winfo_height()
        img_width, img_height = image.shape[1], image.shape[0]
        scale = min(canvas_width / img_width, canvas_height / img_height)
        new_width, new_height = int(img_width * scale), int(img_height * scale)
        resized_image = cv2.resize(image, (new_width, new_height))
        pil_image = Image.fromarray(resized_image)
        imgtk = ImageTk.PhotoImage(image=pil_image)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=imgtk)
        self.canvas.image = imgtk
    
    def read_yolo_labels(self, label_path):
        boxes = []
        image_path = os.path.join(self.image_folder, self.image_list[self.current_index])
        image = cv2.imdecode(np.fromfile(image_path, dtype=np.uint8), cv2.IMREAD_COLOR)
        h, w, _ = image.shape
        
        with open(label_path, "r") as file:
            for line in file.readlines():
                values = line.strip().split()
                class_id = int(values[0])
                x_center, y_center, width, height = map(float, values[1:])
                x1 = int((x_center - width / 2) * w)
                y1 = int((y_center - height / 2) * h)
                x2 = int((x_center + width / 2) * w)
                y2 = int((y_center + height / 2) * h)
                boxes.append((class_id, x1, y1, x2, y2))
        return boxes
    
    def show_prev_image(self):
        if self.current_index > 0:
            self.current_index -= 1
            self.show_image()
    
    def show_next_image(self):
        if self.current_index < len(self.image_list) - 1:
            self.current_index += 1
            self.show_image()
    
    def update_buttons(self):
        self.prev_button.config(state=tk.NORMAL if self.current_index > 0 else tk.DISABLED)
        self.next_button.config(state=tk.NORMAL if self.current_index < len(self.image_list) - 1 else tk.DISABLED)

root = tk.Tk()
app = ImageLabelViewer(root)
root.mainloop()
