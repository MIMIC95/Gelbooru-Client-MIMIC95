import time
import customtkinter
from PIL import Image, ImageTk
from customtkinter import CTk, CTkImage, CTkLabel

import json
import requests
import os
import concurrent.futures
import tkinter as tk
from tkinter import filedialog
from threading import Event, Thread
import shutil
import webbrowser

customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("dark-blue")

my_count = 0
data = []
image_files = []
image_urls = []
config_file = "config.json"
autoplay_event = Event()

class App(CTk):
    def __init__(self):
        super().__init__()

        self.minsize(800, 600)
        self.title("Gelbooru Image Downloader/Viewer by MIMIC95")

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        frame = customtkinter.CTkFrame(master=self)
        frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)

        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        self.canvas = tk.Canvas(master=frame, bd=2, relief="solid", background="#212121")
        self.canvas.grid(row=0, column=0, columnspan=5, pady=20, padx=20, sticky="nsew")

        self.entry1 = customtkinter.CTkEntry(master=frame, placeholder_text="Tags")
        self.entry1.grid(row=1, column=0, columnspan=5, pady=5, padx=5, sticky="ew")

        self.entry3 = customtkinter.CTkEntry(master=frame, placeholder_text="Gelbooru API Key", show="*")
        self.entry3.grid(row=2, column=0, columnspan=5, pady=5, padx=5, sticky="ew")

        self.info_label = customtkinter.CTkLabel(master=frame, text="")
        self.info_label.grid(row=4, column=0, columnspan=5, pady=5, padx=5, sticky="ew")
        self.info_label.bind("<Button-1>", self.open_image_url)

        self.slider = customtkinter.CTkSlider(master=frame, from_=0.5, to=10, number_of_steps=19, command=self.update_info_label)
        self.slider.set(2.5)
        self.slider.grid(row=3, column=0, columnspan=5, pady=5, padx=5, sticky="ew")

        self.progress_bar = customtkinter.CTkProgressBar(master=frame)
        self.progress_bar.grid(row=6, column=0, columnspan=5, pady=5, padx=5, sticky="ew")
        self.progress_bar.set(0)

        self.toggle_var = customtkinter.StringVar(value="Gelbooru")
        self.toggle_button = customtkinter.CTkButton(master=frame, text="Gelbooru", command=self.toggle_site)
        self.toggle_button.grid(row=7, column=0, columnspan=5, pady=5, padx=5, sticky="ew")

        self.load_config()

        self.canvas.bind("<Double-Button-1>", self.open_image)

        button_prev = customtkinter.CTkButton(master=frame, text="Previous", command=lambda: self.send_request("prev"))
        button_prev.grid(row=5, column=0, pady=5, padx=5, sticky="ew")

        button_search = customtkinter.CTkButton(master=frame, text="Search", command=lambda: self.send_request("search"))
        button_search.grid(row=5, column=1, pady=5, padx=5, sticky="ew")

        button_next = customtkinter.CTkButton(master=frame, text="Next", command=lambda: self.send_request("next"))
        button_next.grid(row=5, column=2, pady=5, padx=5, sticky="ew")

        self.button_autoplay = customtkinter.CTkButton(master=frame, text="Autoplay", command=self.toggle_autoplay)
        self.button_autoplay.grid(row=5, column=3, pady=5, padx=5, sticky="ew")

        button_backup = customtkinter.CTkButton(master=frame, text="BACKUP IMAGES", command=self.backup_images)
        button_backup.grid(row=5, column=4, pady=5, padx=5, sticky="ew")

        frame.grid_columnconfigure(0, weight=1)
        frame.grid_columnconfigure(1, weight=1)
        frame.grid_columnconfigure(2, weight=1)
        frame.grid_columnconfigure(3, weight=1)
        frame.grid_columnconfigure(4, weight=1)

        self.bind("<Right>", lambda event: self.send_request("next"))
        self.bind("<Left>", lambda event: self.send_request("prev"))

    def toggle_site(self):
        if self.toggle_var.get() == "Gelbooru":
            self.toggle_var.set("Safebooru")
            self.toggle_button.configure(text="Safebooru")
        else:
            self.toggle_var.set("Gelbooru")
            self.toggle_button.configure(text="Gelbooru")
        self.save_config(self.entry1.get(), 100, self.entry3.get())

    def save_config(self, tags, post_count, api_key):
        config = {
            "tags": tags,
            "post_count": post_count,
            "api_key": api_key,
            "site": self.toggle_var.get()
        }
        with open(config_file, 'w') as f:
            json.dump(config, f)

    def load_config(self):
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                config = json.load(f)
                self.entry1.insert(0, config.get("tags", ""))
                self.entry3.insert(0, config.get("api_key", ""))
                site = config.get("site", "Gelbooru")
                self.toggle_var.set(site)
                self.toggle_button.configure(text=site)

    def download_image(self, image_url, image_path):
        image_data = requests.get(image_url).content
        with open(image_path, 'wb') as f:
            f.write(image_data)
        print(f"Downloaded: {image_url} to {image_path}")

    def delayed_download(self, image_url, image_path):
        time.sleep(1)
        self.download_image(image_url, image_path)

    def background_download(self, images):
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = []
            for i, (image_url, image_path) in enumerate(images):
                futures.append(executor.submit(self.download_image, image_url, image_path))
            concurrent.futures.wait(futures)
        self.display_image()

    def send_request(self, request_type):
        global my_count, data, image_files, image_urls
        if request_type == "search":

            autoplay_event.clear()
            self.progress_bar.set(0)
            self.canvas.delete("all")

            images_dir = os.path.join(os.path.dirname(__file__), "Images")
            if os.path.exists(images_dir):
                shutil.rmtree(images_dir)
            os.makedirs(images_dir, exist_ok=True)

            tags = self.entry1.get()
            api_key = self.entry3.get()
            post_count = 100
            tags = tags
            self.save_config(tags, post_count, api_key)

            if self.toggle_var.get() == "Gelbooru":
                request_url = f"https://gelbooru.com/index.php?page=dapi&s=post&q=index&json=1&limit={post_count}&tags={tags}&api_key={api_key}"
            else:
                request_url = f"https://safebooru.org/index.php?page=dapi&s=post&q=index&json=1&limit={post_count}&tags={tags}"

            response = requests.get(request_url)

            if response.status_code == 200:
                try:
                    if self.toggle_var.get() == "Gelbooru":
                        data = response.json()["post"]
                    else:
                        data = response.json()
                    my_count = 0
                    image_files = []
                    image_urls = []
                    images = []
                    for i, post in enumerate(data):
                        image_url = post["file_url"]
                        if image_url.endswith(".mp4"):
                            print("Skipping: " + image_url)
                            continue
                        image_extension = os.path.splitext(image_url)[1]
                        image_name = f"image_{i+1:03d}{image_extension}"
                        image_path = os.path.join(images_dir, image_name)
                        image_files.append(image_path)
                        image_urls.append(image_url)
                        images.append((image_url, image_path))
                    Thread(target=self.background_download, args=(images,)).start()
                    self.display_image()  
                except json.JSONDecodeError:
                    print("Failed to decode JSON response")
            else:
                print(f"Request failed with status code: {response.status_code}")
        elif request_type == "next":
            self.next_image()
        elif request_type == "prev":
            self.prev_image()
        self.update_info_label()

    def next_image(self):
        global my_count
        while my_count < len(image_files) - 1:
            my_count += 1
            if os.path.exists(image_files[my_count]):
                self.display_image()
                break

    def prev_image(self):
        global my_count
        while my_count > 0:
            my_count -= 1
            if os.path.exists(image_files[my_count]):
                self.display_image()
                break

    def display_image(self):
        global my_count
        if my_count < len(image_files):
            image_path = image_files[my_count]
            if not os.path.exists(image_path):
                print(f"Image not found: {image_path}")
                self.progress_bar.set(0.5)  
                self.wait_for_image(image_path)
                return
            print("Displaying: " + image_path)
            image = Image.open(image_path)
            self.canvas.delete("all")
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            image_ratio = image.width / image.height
            canvas_ratio = canvas_width / canvas_height

            if image_ratio > canvas_ratio:
                new_width = canvas_width
                new_height = int(canvas_width / image_ratio)
            else:
                new_height = canvas_height
                new_width = int(canvas_height * image_ratio)

            resized_image = image.resize((new_width, new_height), Image.LANCZOS)
            self.tk_image = ImageTk.PhotoImage(resized_image)
            self.canvas.create_image(canvas_width // 2, canvas_height // 2, image=self.tk_image, anchor="center")
            self.update_idletasks()
            self.update_info_label()
            self.progress_bar.set(1)  
            print("> displayed " + str(my_count + 1) + " images out of " + str(len(image_files)))
            time.sleep(0.1)

    def wait_for_image(self, image_path):
        while not os.path.exists(image_path):
            time.sleep(0.1)
        self.display_image()

    def open_image(self, event):
        if my_count < len(image_files):
            image_path = image_files[my_count]
            if os.path.exists(image_path):
                if os.name == 'nt': 
                    os.system(f'start "" "{image_path}"')
                else: 
                    os.system(f'xdg-open "{image_path}"')

    def open_image_url(self, event):
        if my_count < len(image_urls):
            image_url = image_urls[my_count]
            webbrowser.open(image_url)

    def autoplay(self):
        global my_count
        if autoplay_event.is_set():
            self.next_image()
            delay = int(self.slider.get() * 1000) 
            self.after(delay, self.autoplay) 
            if my_count >= len(image_files) - 1:
                my_count = -1  

    def toggle_autoplay(self):
        if autoplay_event.is_set():
            autoplay_event.clear()
            self.button_autoplay.configure(text="Autoplay")
        else:
            autoplay_event.set()
            self.button_autoplay.configure(text="Stop Autoplay")
            self.autoplay()

    def backup_images(self):
        images_dir = os.path.join(os.path.dirname(__file__), "Images")
        if not os.path.exists(images_dir):
            print("No images to backup.")
            return

        backup_dir = filedialog.askdirectory(title="Select Backup Directory")
        if backup_dir:
            for image_file in os.listdir(images_dir):
                full_file_path = os.path.join(images_dir, image_file)
                if os.path.isfile(full_file_path):
                    shutil.copy(full_file_path, backup_dir)
            print(f"All images have been copied to {backup_dir}")

    def update_info_label(self, *args):
        if my_count < len(image_files):
            image_path = image_files[my_count]
            image_url = image_urls[my_count]
            if os.path.exists(image_path):
                image = Image.open(image_path)
                self.info_label.configure(text=f"URL: {image_url} | Size: {image.width}x{image.height} | Delay: {self.slider.get()}s")
            else:
                self.info_label.configure(text=f"URL: {image_url} | Image not found | Delay: {self.slider.get()}s")
        else:
            self.info_label.configure(text=f"Delay: {self.slider.get()}s")

if __name__ == "__main__":
    app = App()
    app.mainloop()
