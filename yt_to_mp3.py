import tkinter as tk
import threading
from pytube import YouTube
from moviepy.editor import VideoFileClip
import os

class RoundedEntry(tk.Frame):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.entry = tk.Entry(self, bd=2, relief="flat")
        self.entry.pack(fill='x', expand=True)
        # Create a context menu
        self.context_menu = tk.Menu(self.entry, tearoff=False)
        self.context_menu.add_command(label="Cut", command=self.cut_text)
        self.context_menu.add_command(label="Copy", command=self.copy_text)
        self.context_menu.add_command(label="Paste", command=self.paste_text)
        # Bind right-click event to show the context menu
        self.entry.bind("<Button-3>", self.show_menu)

    def bind(self, *args, **kwargs):
        self.entry.bind(*args, **kwargs)

    def cut_text(self):
        self.entry.event_generate("<<Cut>>")

    def copy_text(self):
        self.entry.event_generate("<<Copy>>")

    def paste_text(self):
        self.entry.event_generate("<<Paste>>")

    def show_menu(self, event):
        self.context_menu.tk_popup(event.x_root, event.y_root)

def search_youtube():
    def search():
        url = url_entry.entry.get()
        try:
            yt = YouTube(url)
            update_labels(yt)
            download_button.config(state="normal")
            append_output("Search Successful!\nTitle: " + yt.title)
        except Exception as e:
            # Log the error silently without updating the output_label
            print("Error:", e)
    
    threading.Thread(target=search).start()

def download_video():
    def download():
        url = url_entry.entry.get()
        try:
            yt = YouTube(url)
            video = yt.streams.get_highest_resolution()
            video.download()
            append_output("Download Successful!")
            convert_button.config(state="normal")
        except Exception as e:
            # Log the error silently without updating the output_label
            print("Error:", e)
    
    threading.Thread(target=download).start()

def convert_to_mp3():
    def convert():
        try:
            for file in os.listdir(os.getcwd()):
                if file.endswith(".mp4"):
                    video_path = os.path.join(os.getcwd(), file)
                    video_title = file[:-4]  # Extract title from the file name
                    audio_path = os.path.join(os.getcwd(), f"{video_title}.mp3")
                    
                    # Load the video and extract audio
                    video_clip = VideoFileClip(video_path)
                    audio_clip = video_clip.audio
                    
                    # Write audio to file
                    audio_clip.write_audiofile(audio_path, bitrate='320k')
                    
                    # Close the clips
                    video_clip.close()
                    audio_clip.close()
                    
                    # Delete the original MP4 file
                    os.remove(video_path)
                    
                    append_output(f"Conversion Successful: {video_title}")
                    # Add space between each conversion
                    append_output("")
                    break
            else:
                # Log the error silently without updating the output_label
                print("Error: No MP4 file found in current directory")
        except Exception as e:
            # Log the error silently without updating the output_label
            print("Error:", e)
    
    threading.Thread(target=convert).start()

def update_labels(yt):
    title_label.config(text="Title: " + yt.title) 
    author_label.config(text="Author: " + yt.author) 
    length_label.config(text="Length: " + str(yt.length) + " seconds") 
    thumbnail_label.config(text="Thumbnail URL: " + yt.thumbnail_url)

def append_output(text):
    output_label.config(text=output_label.cget("text") + "\n" + text)

# GUI
root = tk.Tk()
root.title("YouTube Video Converter")

# Set background color
root.configure(bg="#f0f0f0")

# Define custom style for rounded buttons
def round_rectangle(obj, x1, y1, x2, y2, r=25, **kwargs):    
    points = (x1+r, y1, x1+r, y1, x2-r, y1, x2-r, y1, x2, y1, x2, y1+r, x2, y1+r, x2, y2-r, x2, y2-r, x2, y2, x2-r, y2, x2-r, y2, x1+r, y2, x1+r, y2, x1, y2, x1, y2-r, x1, y2-r, x1, y1+r, x1, y1+r, x1, y1)
    return obj.create_polygon(points, **kwargs, smooth=True)

# Custom style for rounded buttons
def create_rounded_button(canvas, text, command):
    btn = round_rectangle(canvas, 5, 5, 145, 45, 10, fill="#007bff", outline="white", width=2)
    text_id = canvas.create_text(75, 25, text=text, font=("Helvetica", 12, "bold"), fill="white")
    canvas.tag_bind(btn, "<Button-1>", lambda event: command())
    canvas.tag_bind(text_id, "<Button-1>", lambda event: command())

# Labels
url_label = tk.Label(root, text="Enter YouTube URL:", bg="#f0f0f0", fg="black", font=("Helvetica", 12))
url_label.grid(row=0, column=0, pady=5, padx=10)

# Custom entry widget
url_entry = RoundedEntry(root)
url_entry.grid(row=0, column=1, pady=5, padx=10, sticky="ew")

# Buttons
btn_frame = tk.Frame(root, bg="#f0f0f0")
btn_frame.grid(row=1, column=0, columnspan=2, pady=10)

canvas_search = tk.Canvas(btn_frame, height=50, width=150, bg="#f0f0f0", highlightthickness=0)
canvas_search.pack(side=tk.LEFT, padx=10)
create_rounded_button(canvas_search, "Search", search_youtube)

download_button = tk.Canvas(btn_frame, height=50, width=150, bg="#f0f0f0", highlightthickness=0)
download_button.pack(side=tk.LEFT, padx=10)
create_rounded_button(download_button, "Download", download_video)

convert_button = tk.Canvas(btn_frame, height=50, width=150, bg="#f0f0f0", highlightthickness=0)
convert_button.pack(side=tk.LEFT, padx=10)
create_rounded_button(convert_button, "Convert to MP3", convert_to_mp3)

# Output label
output_label = tk.Label(root, text="", wraplength=500, bg="#f0f0f0", fg="black", font=("Helvetica", 12))
output_label.grid(row=2, column=0, columnspan=2, pady=10, padx=10)

# Labels for YouTube video information
title_label = tk.Label(root, text="", bg="#f0f0f0", fg="black", font=("Helvetica", 12))
title_label.grid(row=3, column=0, columnspan=2, pady=5, padx=10)
title_label.grid_remove()  # Hide the title label

author_label = tk.Label(root, text="", bg="#f0f0f0", fg="black", font=("Helvetica", 12))
author_label.grid(row=4, column=0, columnspan=2, pady=5, padx=10)
author_label.grid_remove()  # Hide the author label

length_label = tk.Label(root, text="", bg="#f0f0f0", fg="black", font=("Helvetica", 12))
length_label.grid(row=5, column=0, columnspan=2, pady=5, padx=10)
length_label.grid_remove()  # Hide the length label

thumbnail_label = tk.Label(root, text="", bg="#f0f0f0", fg="black", font=("Helvetica", 12))
thumbnail_label.grid(row=6, column=0, columnspan=2, pady=5, padx=10)
thumbnail_label.grid_remove()  # Hide the thumbnail label

# Allow the text box to resize with the window
root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)

root.mainloop()