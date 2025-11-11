import yt_dlp
import os
import subprocess
from pathlib import Path
import sys 
import shutil 
import platform 

# --- Default Settings ---
DEFAULT_DOWNLOAD_PATH = Path.home() / "Downloads" / "YT_Downloads" 

def find_ffmpeg_path():
    """
    Searches for the ffmpeg.exe path in the system PATH, common directories, 
    and the exact path shown in your image (C:\YT\ffmpeg\bin).
    """
    ffmpeg_exe = shutil.which("ffmpeg")
    if ffmpeg_exe:
        return ffmpeg_exe
    
    # 🌟 Exact FFmpeg path from your latest image, and other common ones
    common_paths = [
        Path("C:/YT/ffmpeg/bin/ffmpeg.exe"), # Exact path from your image
        Path("C:/YT/ffmpeg/ffmpeg.exe"),     # Fallback if 'bin' wasn't there
        Path("C:/ffmpeg/bin/ffmpeg.exe"),    # Another common path
        Path("C:/ffmpeg/ffmpeg.exe"),        # Another common path fallback
    ]
    
    for p in common_paths:
        if p.exists():
            return str(p.resolve())
            
    return None

def update_ytdlp_library():
    """Updates the yt-dlp library using pip."""
    print("-" * 40)
    print("🔄 Checking for yt-dlp library updates...")
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--upgrade', 'yt-dlp'], 
                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("✅ Library updated successfully (or is already the latest version).")
    except Exception as e:
        print("❌ Failed to update library. Please update manually.")
    print("-" * 40)

def open_download_folder(folder_path):
    """Opens the download folder automatically based on the operating system."""
    try:
        if platform.system() == "Windows":
            os.startfile(folder_path)
        elif platform.system() == "Darwin": # macOS
            subprocess.Popen(["open", folder_path])
        else: # Linux
            subprocess.Popen(["xdg-open", folder_path])
        
        # 🚨 تم تعديل هذا السطر لتجنب استخدام f-string وحل مشاكل IDLE
        print("📂 Opening download folder now: " + str(folder_path))

    except Exception as e:
        print("❌ Failed to open download folder automatically: " + str(e))

def create_download_options(is_audio_only, ffmpeg_path):
    """Creates the yt-dlp options dictionary."""
    
    output_template = str(DEFAULT_DOWNLOAD_PATH.resolve() / '%(title)s.%(ext)s')

    ydl_opts = {
        'outtmpl': output_template, 
        'ignoreerrors': True,
        'ffmpeg_location': ffmpeg_path,
        'restrictfilenames': True, 
        'format': 'bestvideo*+bestaudio/best' if not is_audio_only else 'bestaudio/best',
    }

    if is_audio_only:
        ydl_opts.update({
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'extract_audio': True,
        })
        
    return ydl_opts

def get_user_input():
    """Receives user input: URL, path, and download type."""
    print("=" * 40)
    print("          YT-DLP Interactive Downloader")
    print("=" * 40)
    
    url = input("1. Please enter the video or playlist URL: ")
    
    global DEFAULT_DOWNLOAD_PATH
    current_path = str(DEFAULT_DOWNLOAD_PATH.resolve())
    
    new_path_input = input("2. Current save path: [" + current_path + "]\n   Do you want to change it? (Press Enter for current path, or enter a new path): ")

    if new_path_input:
        DEFAULT_DOWNLOAD_PATH = Path(new_path_input)

    while True:
        mode = input("3. What type of download is required? (Type v for Video+Audio / a for Audio only): ").lower()
        if mode in ['v', 'a']:
            is_audio_only = (mode == 'a')
            break
        else:
            print("❌ Invalid input. Please enter 'v' or 'a'.")
            
    return url, is_audio_only

def main():
    """Main program function, wrapped in a continuous loop."""
    
    update_ytdlp_library()
    
    # 🔍 Check for FFmpeg once at startup
    ffmpeg_path = find_ffmpeg_path()
    if not ffmpeg_path or ffmpeg_path == 'ffmpeg':
        print("\n" + "=" * 40)
        print("🚨 IMPORTANT NOTE: FFmpeg was not found!")
        print("  Video/audio will not be merged, and you may get temporary files (e.g., `_.webm`).")
        print("  To fix this, ensure ffmpeg.exe is in: C:\YT\ffmpeg\bin")
        print("=" * 40)
        ffmpeg_path = 'ffmpeg' 
    else:
        print("\n✅ FFmpeg found. Video and audio will be merged!")

    # 🔁 Continuous loop for multiple downloads
    while True:
        
        url, is_audio_only = get_user_input()

        if not url:
            print("❌ No URL entered. Returning to the start.")
            continue

        # 1. Create the save folder
        try:
            DEFAULT_DOWNLOAD_PATH.mkdir(parents=True, exist_ok=True)
            print("\nFile(s) will be saved in folder: " + str(DEFAULT_DOWNLOAD_PATH.resolve()))
                
        except Exception as e:
            print("❌ Failed to create save folder: " + str(e))
            continue

        # 2. Start the download process
        ydl_options = create_download_options(is_audio_only, ffmpeg_path)
        
        print("-" * 40)
        print("Selected download type: " + ('Audio Only (MP3)' if is_audio_only else 'Best Quality Video and Audio'))
        print("-" * 40)

        try:
            with yt_dlp.YoutubeDL(ydl_options) as ydl:
                ydl.download([url])
                print("\n" + "=" * 40)
                print("         🥳 Download operations complete!")
                print("=" * 40)
                
                open_download_folder(str(DEFAULT_DOWNLOAD_PATH.resolve()))

        except yt_dlp.utils.DownloadError as e:
            print("\n" + "=" * 40)
            print("❌ Download failed. Ensure the URL is correct and the library is updated.")
            print("Error details: " + str(e))
            print("=" * 40)
        
        except Exception as e:
            print("\n" + "=" * 40)
            print("❌ An unexpected error occurred. Error details: " + str(e))
            print("=" * 40)
            
        # ❓ Ask if the user wants to download another file
        cont = input("\nDo you want to download another video? (Type yes or press Enter to continue, or no to exit): ").lower()
        if cont in ['no', 'n', 'لا']:
            print("Thank you for using the tool. Goodbye.")
            break
        
        # Visual separator for starting over
        print("\n" + "#" * 50 + "\n")


if __name__ == "__main__":
    main()
    # إضافة هذا السطر لمنع الإغلاق المفاجئ لنافذة CMD
    input("Press Enter to close the window...")
