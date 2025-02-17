import yt_dlp
import os
import subprocess
import shutil
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import customtkinter as ctk  # Modern UI
from tkinter import filedialog
import re

# Initialize customtkinter with a modern dark theme
ctk.set_appearance_mode("Dark")  # Can be "Light" or "Dark"
ctk.set_default_color_theme("blue")

# Append output to a text widget
def append_output(message):
    output_text.insert("end", message + "\n")
    output_text.yview("end")

def background_task(task_func):
    def run_task():
        try:
            task_func()
        except Exception as e:
            append_output(f"Background task error: {e}")
    
    executor = ThreadPoolExecutor(max_workers=2)
    future = executor.submit(run_task)
    return future

# Check if FFmpeg is installed
def check_ffmpeg_installed():
    return shutil.which("ffmpeg") is not None

# Install FFmpeg using winget
def install_ffmpeg():
    def run_command(command):
        process = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return process
    
    try:
        append_output("Installing FFmpeg...")
        process = run_command(["winget", "install", "ffmpeg"])
        if check_ffmpeg_installed():
            append_output("FFmpeg installation complete.")
        else:
            append_output("FFmpeg installation failed. Please install manually.")
    except Exception as e:
        append_output(f"Error: {e}")

# Check if NVIDIA GPU is available
def check_nvidia_gpu():
    try:
        result = subprocess.run(['nvidia-smi'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return result.returncode == 0
    except FileNotFoundError:
        return False

# YouTube Search Function
def search_youtube(url):
    def search():
        if not url:
            append_output("Error: Please enter a valid YouTube URL.")
            return
        
        if not check_ffmpeg_installed():
            append_output("FFmpeg not found. Installing FFmpeg...")
            future = background_task(install_ffmpeg)
            future.result()
            if not check_ffmpeg_installed():
                append_output("Error: FFmpeg installation failed.")
                return
        
        try:
            ydl_opts = {'quiet': True, 'format': 'best', 'outtmpl': '%(title)s.%(ext)s'}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(url, download=False)
                title = info_dict.get('title', 'Unknown Title')
                append_output(f"Search Successful!\nTitle: {title}")
        except Exception as e:
            append_output(f"Error: {e}")
    
    return background_task(lambda: search())

# YouTube Download Function
def download_video(url):
    def download():
        if not url:
            append_output("Error: Please enter a valid YouTube URL.")
            return
        
        if not check_ffmpeg_installed():
            append_output("FFmpeg is required. Installing FFmpeg...")
            future = background_task(install_ffmpeg)
            future.result()
            if not check_ffmpeg_installed():
                append_output("Error: FFmpeg installation failed.")
                return
        
        try:
            ydl_opts = {'format': 'bestvideo+bestaudio/best', 'outtmpl': '%(title)s.%(ext)s'}
            append_output("Downloading video...")
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            append_output("Download Successful!")
        except Exception as e:
            append_output(f"Error: {e}")
    
    return background_task(lambda: download())

# Convert to MP3 Function
def convert_to_mp3():
    def convert():
        if not check_ffmpeg_installed():
            append_output("FFmpeg is required. Installing FFmpeg...")
            future = background_task(install_ffmpeg)
            future.result()
            if not check_ffmpeg_installed():
                append_output("Error: FFmpeg installation failed.")
                return
        
        append_output("Converting to MP3...")
        video_files = [file for file in os.listdir(os.getcwd()) if file.lower().endswith(('.mp4', '.mkv', '.avi', '.mov', '.webm'))]
        if not video_files:
            append_output("Error: No video file found in current directory")
            return
        
        def process_file(file):
            video_path = os.path.join(os.getcwd(), file)
            video_title = os.path.splitext(file)[0]
            audio_path = os.path.join(save_dir.get(), f"{video_title}.mp3")
            append_output(f"Converting {video_path} to MP3...")

            if check_nvidia_gpu():
                ffmpeg_command = ['ffmpeg', '-i', video_path, '-vn', '-c:a', 'libmp3lame', '-b:a', '320k', '-y', audio_path]
                append_output("Using GPU for conversion...")
            else:
                num_threads = max(1, os.cpu_count() // 2)
                ffmpeg_command = ['ffmpeg', '-i', video_path, '-vn', '-c:a', 'libmp3lame', '-b:a', '320k', '-threads', str(num_threads), '-y', audio_path]
                append_output("Using CPU for conversion with optimized thread usage...")

            process = subprocess.run(ffmpeg_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if os.path.exists(audio_path):
                os.remove(video_path)
                append_output(f"Conversion Successful and file deleted: {video_title}")
            else:
                append_output(f"Error: Conversion failed for {video_title}")

        with ThreadPoolExecutor() as executor:
            future_to_file = {executor.submit(process_file, file): file for file in video_files}
            for future in as_completed(future_to_file):
                try:
                    future.result()
                except Exception as e:
                    append_output(f"Error: {e}")
    
    return background_task(lambda: convert())

# File Dialog for selecting a directory
def browse_directory():
    directory = filedialog.askdirectory()
    if directory:
        save_dir.set(directory)

# Modern GUI Setup
root = ctk.CTk()
root.title("YouTube Video Conveter")
root.geometry("800x650")
root.resizable(False, False)  # Disable resizing the window
# Set the window icon (ensure 'icon.ico' is in the correct path)
root.iconbitmap("icon.ico")  # Use this for a .ico file

frame = ctk.CTkFrame(root, corner_radius=15)
frame.pack(pady=20, padx=20, fill="both", expand=True)

# URL Input
ctk.CTkLabel(frame, text="YouTube URL:", font=("Arial", 14)).pack(pady=5)
url_entry = ctk.CTkEntry(frame, width=400, height=40, corner_radius=10, placeholder_text="Enter YouTube URL...")
url_entry.pack(pady=5)

# Button Frame for Search, Download, and Convert
button_frame = ctk.CTkFrame(frame, fg_color="transparent")
button_frame.pack(pady=10)

search_button = ctk.CTkButton(button_frame, text="Search", command=lambda: search_youtube(url_entry.get()), corner_radius=10)
search_button.grid(row=0, column=0, padx=5)

download_button = ctk.CTkButton(button_frame, text="Download", command=lambda: download_video(url_entry.get()), corner_radius=10)
download_button.grid(row=0, column=1, padx=5)

convert_button = ctk.CTkButton(button_frame, text="Convert to MP3", command=convert_to_mp3, corner_radius=10)
convert_button.grid(row=0, column=2, padx=5)

# Directory Input and Browse Button
save_dir = ctk.StringVar(value=os.getcwd())
ctk.CTkLabel(frame, text="Save Directory:", font=("Arial", 14)).pack(pady=5)
save_dir_entry = ctk.CTkEntry(frame, textvariable=save_dir, width=400, height=40, corner_radius=10)
save_dir_entry.pack(pady=5)
browse_button = ctk.CTkButton(frame, text="Browse", command=browse_directory, corner_radius=10)
browse_button.pack(pady=5)

# Output Display Textbox
output_text = ctk.CTkTextbox(frame, width=500, height=150, corner_radius=10)
output_text.pack(pady=10)

# Instructions Text Box
instructions_text = ctk.CTkTextbox(frame, width=500, height=133, corner_radius=10)
instructions_text.pack(pady=10)
instructions_text.insert("end", (
    "Instructions:\n"
    "1. Enter the YouTube URL in the 'YouTube URL' field.\n"
    "2. Click 'Search' to retrieve video information.\n"
    "3. Click 'Download' to download the video.\n"
    "4. Click 'Convert to MP3' to convert the downloaded video to MP3 format.\n"
    "5. Use 'Browse' to select the directory where MP3 files will be saved.\n"
    "6. Check the output box for progress and error messages."
))
instructions_text.configure(state="disabled")  # Make the textbox read-only and non-selectable

root.mainloop()
