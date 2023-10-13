import os
import cv2
import numpy as np
from moviepy.editor import VideoFileClip
from tkinter import Tk, Label, Button, filedialog, StringVar, Radiobutton, Frame

# Ensure input and output directories exist
if not os.path.exists("input"):
    os.makedirs("input")
    
if not os.path.exists("output"):
    os.makedirs("output")

def cartoonize_image(img_path, bilateral_filter_iterations=5, d=9, sigma_color=75, sigma_space=75):
    # reading image 
    img = cv2.imread(img_path)
    
    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Apply median blur
    gray = cv2.medianBlur(gray, 5)
    
    # Detect edges using adaptive thresholding
    edges = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 9, 9)
    
    # Dilate edges to make them thicker
    kernel = np.ones((2,2), np.uint8)
    edges = cv2.dilate(edges, kernel)
    
    # Apply bilateral filter multiple times to stylize the image
    color = img
    for _ in range(bilateral_filter_iterations):
        color = cv2.bilateralFilter(color, d, sigma_color, sigma_space)
    
    # Reduce noise using Gaussian Blur
    color = cv2.GaussianBlur(color, (3, 3), 0)
    
    # Cartoonization: Bitwise AND operation between the stylized color image and edges
    cartoon = cv2.bitwise_and(color, color, mask=edges)

    return img, edges, cartoon

def convert_video_to_gif(video_path, output_path):
    clip = VideoFileClip(video_path)
    clip.write_gif(output_path, fps=10)
    clip.close()

class GUI:
    def __init__(self, master):
        self.master = master
        master.title("Processing Tool")
        
        self.label = Label(master, text="Choose a task:")
        self.label.pack(pady=10)

        self.mode = StringVar(value="cartoonize")

        self.cartoonize_rb = Radiobutton(master, text="Cartoonize", variable=self.mode, value="cartoonize")
        self.cartoonize_rb.pack(anchor="w")

        self.gifmaker_rb = Radiobutton(master, text="Gif Maker", variable=self.mode, value="gifmaker")
        self.gifmaker_rb.pack(anchor="w")

        self.upload_button = Button(master, text="Upload File", command=self.upload_file)
        self.upload_button.pack(pady=20)

        self.process_button = Button(master, text="Process", command=self.process)
        self.process_button.pack(pady=20)
        
        self.filepath = ""

    def upload_file(self):
        filetypes = [("All files", "*.*")]

        if self.mode.get() == "cartoonize":
            filetypes = [("Image Files", "*.png;*.jpg;*.jpeg")]
        elif self.mode.get() == "gifmaker":
            filetypes = [("Video Files", "*.mp4;*.avi;*.mkv")]

        self.filepath = filedialog.askopenfilename(title="Select a file", filetypes=filetypes)
        if self.filepath:
            dest_path = os.path.join("input", os.path.basename(self.filepath))
            with open(self.filepath, "rb") as fsrc:
                with open(dest_path, "wb") as fdst:
                    fdst.write(fsrc.read())
            self.filepath = dest_path

    def process(self):
        if not self.filepath:
            return
        
        output_path = os.path.join("output", os.path.basename(self.filepath))

        if self.mode.get() == "cartoonize":
            _, _, cartoon = cartoonize_image(self.filepath)
            cv2.imwrite(output_path, cartoon)
            print(f"Cartoonized image saved at {output_path}")

        elif self.mode.get() == "gifmaker":
            if self.filepath.endswith(('.mp4', '.avi', '.mkv')):
                output_path = os.path.splitext(output_path)[0] + '.gif'
                convert_video_to_gif(self.filepath, output_path)
                print(f"GIF saved at {output_path}")
            else:
                print(f"Unsupported file format for GIF creation: {self.filepath}")

        self.show_result(output_path)

    def show_result(self, output_path):
        if os.path.exists(output_path):
            result_win = Tk()
            result_win.title("Result")
            label = Label(result_win, text=f"Output saved at: {output_path}", wraplength=400)
            label.pack(pady=20)
            result_win.mainloop()

if __name__ == "__main__":
    root = Tk()
    gui = GUI(root)
    root.mainloop()