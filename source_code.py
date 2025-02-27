import time
import customtkinter
from PIL import Image, ImageTk
from customtkinter import CTk, CTkImage, CTkLabel

import json
import requests
import os
import tkinter as tk
from tkinter import filedialog, Menu, messagebox, Toplevel, Label
from threading import Event, Thread, Lock
import shutil
import webbrowser
import pyperclip
import random

customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("dark-blue")

my_count = 0
data = []
image_files = []
image_urls = []
image_tags = []
config_file = "config.json"
autoplay_event = Event()
download_event = Event()
download_lock = Lock()

fruits = ["apple", "banana", "cherry", "date", "elderberry", "fig", "grape", "honeydew", "kiwi", "lemon", "mango", "nectarine", "orange", "papaya", "quince", "raspberry", "strawberry", "tangerine", "ugli", "vanilla", "watermelon", "xigua", "yellowpassionfruit", "zucchini"]

class App(CTk):
    def __init__(self):
        super().__init__()

        self.minsize(1200, 800)
        self.title("Gelbooru Image Downloader/Viewer by MIMIC95")

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        frame = customtkinter.CTkFrame(master=self)
        frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        self.canvas = tk.Canvas(master=frame, bd=2, relief="solid", background="#212121")
        self.canvas.grid(row=0, column=0, columnspan=5, pady=2, padx=2, sticky="nsew")

        self.slider = customtkinter.CTkSlider(master=frame, from_=0.5, to=10, number_of_steps=19, command=self.update_info_label)
        self.slider.set(2.5)
        self.slider.grid(row=2, column=0, columnspan=5, pady=2, padx=2, sticky="ew")

        self.entry1 = customtkinter.CTkEntry(master=frame, placeholder_text="Tags")
        self.entry1.grid(row=3, column=0, columnspan=5, pady=2, padx=2, sticky="ew")

        self.entry3 = customtkinter.CTkEntry(master=frame, placeholder_text="Gelbooru API Key", show="*")
        self.entry3.grid(row=4, column=0, columnspan=5, pady=2, padx=2, sticky="ew")

        self.progress_bar = customtkinter.CTkProgressBar(master=frame)
        self.progress_bar.grid(row=5, column=0, columnspan=5, pady=2, padx=2, sticky="ew")
        self.progress_bar.set(0)

        button_prev = customtkinter.CTkButton(master=frame, text="Previous", command=lambda: self.send_request("prev"))
        button_prev.grid(row=6, column=0, pady=2, padx=2, sticky="ew")

        self.button_search = customtkinter.CTkButton(master=frame, text="Search", command=lambda: self.send_request("search"))
        self.button_search.grid(row=6, column=1, pady=2, padx=2, sticky="ew")

        button_next = customtkinter.CTkButton(master=frame, text="Next", command=lambda: self.send_request("next"))
        button_next.grid(row=6, column=2, pady=2, padx=2, sticky="ew")

        self.button_autoplay = customtkinter.CTkButton(master=frame, text="Autoplay", command=self.toggle_autoplay)
        self.button_autoplay.grid(row=6, column=3, pady=2, padx=2, sticky="ew")

        button_backup = customtkinter.CTkButton(master=frame, text="BACKUP IMAGES", command=self.backup_images)
        button_backup.grid(row=6, column=4, pady=2, padx=2, sticky="ew")

        self.toggle_var = customtkinter.StringVar(value="Gelbooru")
        self.toggle_button = customtkinter.CTkButton(master=frame, text="Gelbooru", command=self.toggle_site)
        self.toggle_button.grid(row=7, column=0, columnspan=5, pady=2, padx=2, sticky="ew")

        self.load_config()

        self.canvas.bind("<Double-Button-1>", self.open_image)
        self.canvas.bind("<Button-3>", self.show_context_menu)

        frame.grid_columnconfigure(0, weight=1)
        frame.grid_columnconfigure(1, weight=1)
        frame.grid_columnconfigure(2, weight=1)
        frame.grid_columnconfigure(3, weight=1)
        frame.grid_columnconfigure(4, weight=1)

        self.bind("<Right>", lambda event: self.send_request("next"))
        self.bind("<Left>", lambda event: self.send_request("prev"))

        self.context_menu = Menu(self, tearoff=0)
        self.context_menu.add_command(label="Open Image URL", command=self.open_image_url)
        self.context_menu.add_command(label="Copy Tags", command=self.copy_tags)
        self.context_menu.add_command(label="Delete Image", command=self.delete_image)
        self.context_menu.add_command(label="Save Image", command=self.save_image)
        self.context_menu.add_command(label="Open Saved Images Folder", command=self.open_saved_images_folder)

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

    def get_next_image_name(self, images_dir):
        existing_files = os.listdir(images_dir)
        image_numbers = [int(f.split('_')[1].split('.')[0]) for f in existing_files if f.startswith('image_')]
        next_number = max(image_numbers, default=0) + 1
        return f"image_{next_number:03d}"

    def download_image(self, image_url, images_dir, retries=3):
        for attempt in range(retries):
            if not download_event.is_set():
                return None
            try:
                response = requests.head(image_url)
                if 'Content-Length' in response.headers:
                    size = int(response.headers['Content-Length'])
                    if size > 10 * 1024 * 1024:  # 10 MB
                        print(f"Skipping: {image_url} (size: {size / (1024 * 1024):.2f} MB)")
                        return None

                image_extension = os.path.splitext(image_url)[1]
                image_name = self.get_next_image_name(images_dir) + image_extension
                image_path = os.path.join(images_dir, image_name)
                image_data = requests.get(image_url).content
                with open(image_path, 'wb') as f:
                    f.write(image_data)
                print(f"Downloaded: {image_url} to {image_path}")
                return image_path
            except (requests.exceptions.RequestException, requests.exceptions.ChunkedEncodingError) as e:
                print(f"Error downloading {image_url}: {e}")
                if attempt < retries - 1:
                    print(f"Retrying... ({attempt + 1}/{retries})")
                    time.sleep(1)
                else:
                    print(f"Failed to download {image_url} after {retries} attempts")
                    return None

    def background_download(self, images):
        images_dir = os.path.join(os.path.dirname(__file__), "Images")
        total_images = len(images)
        for i, image_url in enumerate(images):
            if not download_event.is_set():
                break
            image_path = self.download_image(image_url, images_dir)
            if image_path:
                with download_lock:
                    image_files.append(image_path)
                self.update_progress_bar((i + 1) / total_images)
                if i == 0:
                    self.display_image()
        self.update_progress_bar(0) 

    def update_progress_bar(self, value):
        self.progress_bar.set(value)

    def send_request(self, request_type):
        if request_type not in ["prev", "next"] and self.progress_bar.get() > 0:
            self.show_popup("PLEASE WAIT TILL THE DOWNLOADS ARE FINISHED!")
            return

        global my_count, data, image_files, image_urls, image_tags
        if request_type == "search":
            download_event.clear()
            with download_lock:
                image_files.clear()
                image_urls.clear()
                image_tags.clear()
            download_event.set()

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
                    images = []
                    for post in data:
                        image_url = post["file_url"]
                        if image_url.endswith(".mp4"):
                            print("Skipping: " + image_url)
                            continue
                        image_urls.append(image_url)
                        image_tags.append(post["tags"])
                    download_thread = Thread(target=self.background_download, args=(image_urls,))
                    download_thread.start()
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

    def open_image_url(self, event=None):
        if my_count < len(image_urls):
            image_url = image_urls[my_count]
            webbrowser.open(image_url)

    def copy_tags(self):
        if my_count < len(image_tags):
            tags = image_tags[my_count].replace(" ", "+")
            pyperclip.copy(tags)
            print("Tags copied to clipboard")

    def delete_image(self):
        if my_count < len(image_files):
            image_path = image_files[my_count]
            if os.path.exists(image_path):
                os.remove(image_path)
                print(f"Deleted: {image_path}")
                self.next_image()

    def save_image(self):
        if my_count < len(image_files):
            image_path = image_files[my_count]
            if os.path.exists(image_path):
                saved_images_dir = os.path.join(os.path.dirname(__file__), "saved images")
                os.makedirs(saved_images_dir, exist_ok=True)
                fruit_name = random.choice(fruits)
                random_number = random.randint(0, 99999)
                image_extension = os.path.splitext(image_path)[1]
                new_image_name = f"{fruit_name}_{random_number:05d}{image_extension}"
                new_image_path = os.path.join(saved_images_dir, new_image_name)
                shutil.copy(image_path, new_image_path)
                print(f"Saved: {image_path} to {new_image_path}")

    def open_saved_images_folder(self):
        saved_images_dir = os.path.join(os.path.dirname(__file__), "saved images")
        if os.path.exists(saved_images_dir):
            if os.name == 'nt':
                os.startfile(saved_images_dir)
            else:
                os.system(f'xdg-open "{saved_images_dir}"')
        else:
            print("Saved images folder does not exist.")

    def show_context_menu(self, event):
        self.context_menu.post(event.x_root, event.y_root)

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
            image_tags_text = ", ".join(image_tags[my_count].split())
            if os.path.exists(image_path):
                image = Image.open(image_path)
                print(f"URL: {image_url} | Size: {image.width}x{image.height} | Delay: {self.slider.get()}s\nTags: {image_tags_text}")
            else:
                print(f"URL: {image_url} | Image not found | Delay: {self.slider.get()}s\nTags: {image_tags_text}")
        else:
            print(f"Delay: {self.slider.get()}s\nTags: ")

    def show_popup(self, message):
        popup = Toplevel(self)
        popup.title("Download In Progress")
        popup.geometry("400x120")

        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (400 // 2)
        y = (self.winfo_screenheight() // 2) - (120 // 2)
        popup.geometry(f"+{x}+{y}")

        Label(popup, text=message, padx=30, pady=30).pack()

        ok_button = customtkinter.CTkButton(popup, text="OK", command=popup.destroy)
        ok_button.pack(pady=10)

        self.after(5000, popup.destroy)

if __name__ == "__main__":
    app = App()
    app.mainloop()
