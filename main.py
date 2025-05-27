#!/usr/bin/env python3
"""
Linux Distro Downloader
A GUI application for downloading and verifying Linux distribution ISO files.

Author: Created with Claude's assistance
Version: 1.0.0
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
import threading
import requests
import hashlib
import json
import os
import sys
from pathlib import Path
import time
from typing import Dict, Any, Optional
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('downloader.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class LinuxDistroDownloader:
    def __init__(self):
        # Set appearance mode and color theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Initialize main window
        self.root = ctk.CTk()
        self.root.title("Linux Distro Downloader v1.0")
        self.root.geometry("800x700")
        self.root.minsize(600, 500)
        
        # Initialize variables
        self.download_dir = tk.StringVar(value=str(Path.home() / "Downloads"))
        self.selected_distro = tk.StringVar()
        self.selected_edition = tk.StringVar()
        self.download_thread = None
        self.is_downloading = False
        
        # Load distribution data
        self.distro_data = self.load_distro_data()
        
        # Setup GUI
        self.setup_gui()
        
        logger.info("Linux Distro Downloader initialized")
    
    def load_distro_data(self) -> Dict[str, Any]:
        """Load distribution data from JSON file"""
        try:
            with open('distro_data.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error("distro_data.json not found")
            messagebox.showerror("Error", "Distribution data file not found!")
            sys.exit(1)
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing distro_data.json: {e}")
            messagebox.showerror("Error", "Invalid distribution data file!")
            sys.exit(1)
    
    def setup_gui(self):
        """Setup the main GUI layout"""
        # Main container
        main_frame = ctk.CTkFrame(self.root)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title_label = ctk.CTkLabel(
            main_frame, 
            text="Linux Distribution Downloader",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=(20, 30))
        
        # Selection frame
        selection_frame = ctk.CTkFrame(main_frame)
        selection_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        # Distribution selection
        distro_label = ctk.CTkLabel(selection_frame, text="Select Distribution:", font=ctk.CTkFont(size=14, weight="bold"))
        distro_label.pack(anchor="w", padx=20, pady=(20, 5))
        
        self.distro_combo = ctk.CTkComboBox(
            selection_frame,
            values=list(self.distro_data.keys()),
            command=self.on_distro_select,
            variable=self.selected_distro,
            width=300
        )
        self.distro_combo.pack(anchor="w", padx=20, pady=(0, 10))
        
        # Edition selection
        edition_label = ctk.CTkLabel(selection_frame, text="Select Edition:", font=ctk.CTkFont(size=14, weight="bold"))
        edition_label.pack(anchor="w", padx=20, pady=(10, 5))
        
        self.edition_combo = ctk.CTkComboBox(
            selection_frame,
            values=[],
            variable=self.selected_edition,
            width=300,
            state="disabled"
        )
        self.edition_combo.pack(anchor="w", padx=20, pady=(0, 20))
        
        # Download directory frame
        dir_frame = ctk.CTkFrame(main_frame)
        dir_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        dir_label = ctk.CTkLabel(dir_frame, text="Download Directory:", font=ctk.CTkFont(size=14, weight="bold"))
        dir_label.pack(anchor="w", padx=20, pady=(20, 5))
        
        dir_input_frame = ctk.CTkFrame(dir_frame, fg_color="transparent")
        dir_input_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        self.dir_entry = ctk.CTkEntry(dir_input_frame, textvariable=self.download_dir, width=400)
        self.dir_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        browse_btn = ctk.CTkButton(dir_input_frame, text="Browse", command=self.browse_directory, width=80)
        browse_btn.pack(side="right")
        
        # Download button
        self.download_btn = ctk.CTkButton(
            main_frame,
            text="Download ISO",
            command=self.start_download,
            font=ctk.CTkFont(size=16, weight="bold"),
            height=40
        )
        self.download_btn.pack(pady=20)
        
        # Progress frame
        progress_frame = ctk.CTkFrame(main_frame)
        progress_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(progress_frame, width=400)
        self.progress_bar.pack(pady=(20, 10))
        self.progress_bar.set(0)
        
        # Status labels
        self.status_label = ctk.CTkLabel(progress_frame, text="Ready to download", font=ctk.CTkFont(size=12))
        self.status_label.pack(pady=(0, 5))
        
        self.progress_label = ctk.CTkLabel(progress_frame, text="", font=ctk.CTkFont(size=11))
        self.progress_label.pack(pady=(0, 20))
        
        # Info text area
        self.info_text = ctk.CTkTextbox(main_frame, height=100)
        self.info_text.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        self.info_text.insert("1.0", "Welcome to Linux Distro Downloader!\n\nSelect a distribution and edition to get started.")
    
    def on_distro_select(self, distro_name: str):
        """Handle distribution selection"""
        if distro_name in self.distro_data:
            editions = list(self.distro_data[distro_name]['editions'].keys())
            self.edition_combo.configure(values=editions, state="normal")
            self.edition_combo.set(editions[0] if editions else "")
            
            # Update info
            distro_info = self.distro_data[distro_name]
            info_text = f"Selected: {distro_name}\n"
            info_text += f"Description: {distro_info.get('description', 'No description available')}\n"
            info_text += f"Available editions: {', '.join(editions)}"
            
            self.info_text.delete("1.0", "end")
            self.info_text.insert("1.0", info_text)
    
    def browse_directory(self):
        """Browse for download directory"""
        directory = filedialog.askdirectory(initialdir=self.download_dir.get())
        if directory:
            self.download_dir.set(directory)
    
    def start_download(self):
        """Start the download process"""
        if self.is_downloading:
            messagebox.showwarning("Warning", "Download already in progress!")
            return
        
        distro = self.selected_distro.get()
        edition = self.selected_edition.get()
        
        if not distro or not edition:
            messagebox.showerror("Error", "Please select both distribution and edition!")
            return
        
        download_dir = self.download_dir.get()
        if not os.path.exists(download_dir):
            try:
                os.makedirs(download_dir)
            except OSError as e:
                messagebox.showerror("Error", f"Cannot create download directory:\n{e}")
                return
        
        # Start download in separate thread
        self.download_thread = threading.Thread(
            target=self.download_iso,
            args=(distro, edition, download_dir),
            daemon=True
        )
        self.download_thread.start()
    
    def download_iso(self, distro: str, edition: str, download_dir: str):
        """Download and verify ISO file"""
        self.is_downloading = True
        self.download_btn.configure(text="Downloading...", state="disabled")
        
        try:
            # Get download info
            edition_data = self.distro_data[distro]['editions'][edition]
            url = edition_data['url']
            checksum = edition_data['checksum']
            filename = edition_data['filename']
            filepath = os.path.join(download_dir, filename)
            
            self.update_status(f"Starting download of {distro} {edition}...")
            logger.info(f"Starting download: {distro} {edition} from {url}")
            
            # Download file
            success = self.download_file(url, filepath)
            
            if success:
                self.update_status("Download completed. Verifying checksum...")
                logger.info(f"Download completed: {filepath}")
                
                # Verify checksum
                if self.verify_checksum(filepath, checksum):
                    self.update_status("✅ Download and verification successful!")
                    self.update_info(f"Successfully downloaded and verified:\n{filename}\n\nLocation: {filepath}")
                    messagebox.showinfo("Success", f"Successfully downloaded and verified {filename}!")
                    logger.info(f"Verification successful: {filepath}")
                else:
                    self.update_status("❌ Checksum verification failed!")
                    self.update_info(f"Download completed but checksum verification failed!\nFile: {filepath}\n\nPlease re-download or verify manually.")
                    messagebox.showerror("Verification Failed", "Checksum verification failed! The file may be corrupted.")
                    logger.error(f"Checksum verification failed: {filepath}")
            else:
                self.update_status("❌ Download failed")
                logger.error(f"Download failed: {filepath}")
        
        except Exception as e:
            error_msg = f"Error during download: {str(e)}"
            self.update_status(f"❌ {error_msg}")
            self.update_info(error_msg)
            messagebox.showerror("Error", error_msg)
            logger.error(f"Download error: {e}")
        
        finally:
            self.is_downloading = False
            self.download_btn.configure(text="Download ISO", state="normal")
            self.progress_bar.set(0)
            self.progress_label.configure(text="")
    
    def download_file(self, url: str, filepath: str) -> bool:
        """Download file with progress tracking"""
        try:
            response = requests.get(url, stream=True, timeout=30)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        if total_size > 0:
                            progress = downloaded / total_size
                            self.progress_bar.set(progress)
                            
                            # Update progress info
                            downloaded_mb = downloaded / (1024 * 1024)
                            total_mb = total_size / (1024 * 1024)
                            self.root.after(0, lambda: self.progress_label.configure(
                                text=f"{downloaded_mb:.1f} MB / {total_mb:.1f} MB ({progress*100:.1f}%)"
                            ))
            
            return True
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error during download: {e}")
            return False
        except IOError as e:
            logger.error(f"File system error during download: {e}")
            return False
    
    def verify_checksum(self, filepath: str, expected_checksum: str) -> bool:
        """Verify file checksum"""
        try:
            sha256_hash = hashlib.sha256()
            with open(filepath, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(chunk)
            
            calculated_checksum = sha256_hash.hexdigest().lower()
            expected_checksum = expected_checksum.lower()
            
            logger.info(f"Expected checksum: {expected_checksum}")
            logger.info(f"Calculated checksum: {calculated_checksum}")
            
            return calculated_checksum == expected_checksum
            
        except Exception as e:
            logger.error(f"Error calculating checksum: {e}")
            return False
    
    def update_status(self, message: str):
        """Update status label from any thread"""
        self.root.after(0, lambda: self.status_label.configure(text=message))
    
    def update_info(self, message: str):
        """Update info text from any thread"""
        def update():
            self.info_text.delete("1.0", "end")
            self.info_text.insert("1.0", message)
        self.root.after(0, update)
    
    def run(self):
        """Start the application"""
        logger.info("Starting Linux Distro Downloader GUI")
        self.root.mainloop()

def main():
    """Main entry point"""
    try:
        app = LinuxDistroDownloader()
        app.run()
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        messagebox.showerror("Fatal Error", f"Application failed to start:\n{e}")

if __name__ == "__main__":
    main()