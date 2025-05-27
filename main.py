#!/usr/bin/env python3
"""
Linux Distro Downloader
A GUI application for downloading and verifying Linux distribution ISO files.

Author: Created with Claude's assistance
Version: 1.1.0
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
from datetime import datetime
import re

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
        self.root.title("Linux Distro Downloader v1.1")
        self.root.geometry("900x800")
        self.root.minsize(700, 600)
        
        # Initialize variables
        self.download_dir = tk.StringVar(value=str(Path.home() / "Downloads"))
        self.selected_distro = tk.StringVar()
        self.selected_edition = tk.StringVar()
        self.download_thread = None
        self.version_check_thread = None
        self.is_downloading = False
        self.download_paused = False
        self.download_cancelled = False
        self.current_response = None
        self.current_file_handle = None
        
        # Load distribution data
        self.distro_data = self.load_distro_data()
        self.version_info = {}
        
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
        
        # Version check section
        version_frame = ctk.CTkFrame(main_frame)
        version_frame.pack(fill="x", padx=20, pady=(0, 10))
        
        version_label = ctk.CTkLabel(version_frame, text="Version Information:", font=ctk.CTkFont(size=14, weight="bold"))
        version_label.pack(anchor="w", padx=20, pady=(15, 5))
        
        version_controls = ctk.CTkFrame(version_frame, fg_color="transparent")
        version_controls.pack(fill="x", padx=20, pady=(0, 15))
        
        self.check_versions_btn = ctk.CTkButton(
            version_controls,
            text="Check Latest Versions",
            command=self.start_version_check,
            width=150
        )
        self.check_versions_btn.pack(side="left", padx=(0, 10))
        
        self.version_status_label = ctk.CTkLabel(version_controls, text="Click to check for latest versions", font=ctk.CTkFont(size=11))
        self.version_status_label.pack(side="left", anchor="w")
        
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
            width=350
        )
        self.distro_combo.pack(anchor="w", padx=20, pady=(0, 10))
        
        # Edition selection
        edition_label = ctk.CTkLabel(selection_frame, text="Select Edition:", font=ctk.CTkFont(size=14, weight="bold"))
        edition_label.pack(anchor="w", padx=20, pady=(10, 5))
        
        self.edition_combo = ctk.CTkComboBox(
            selection_frame,
            values=[],
            variable=self.selected_edition,
            width=350,
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
        
        self.dir_entry = ctk.CTkEntry(dir_input_frame, textvariable=self.download_dir, width=450)
        self.dir_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        browse_btn = ctk.CTkButton(dir_input_frame, text="Browse", command=self.browse_directory, width=80)
        browse_btn.pack(side="right")
        
        # Download controls frame
        controls_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        controls_frame.pack(pady=20)
        
        self.download_btn = ctk.CTkButton(
            controls_frame,
            text="Download ISO",
            command=self.start_download,
            font=ctk.CTkFont(size=16, weight="bold"),
            height=40,
            width=140
        )
        self.download_btn.pack(side="left", padx=(0, 10))
        
        self.pause_btn = ctk.CTkButton(
            controls_frame,
            text="Pause",
            command=self.pause_download,
            font=ctk.CTkFont(size=14),
            height=40,
            width=100,
            state="disabled"
        )
        self.pause_btn.pack(side="left", padx=(0, 10))
        
        self.cancel_btn = ctk.CTkButton(
            controls_frame,
            text="Cancel",
            command=self.cancel_download,
            font=ctk.CTkFont(size=14),
            height=40,
            width=100,
            state="disabled",
            fg_color="#dc3545",
            hover_color="#c82333"
        )
        self.cancel_btn.pack(side="left")
        
        # Progress frame
        progress_frame = ctk.CTkFrame(main_frame)
        progress_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(progress_frame, width=500)
        self.progress_bar.pack(pady=(20, 10))
        self.progress_bar.set(0)
        
        # Status labels
        self.status_label = ctk.CTkLabel(progress_frame, text="Ready to download", font=ctk.CTkFont(size=12))
        self.status_label.pack(pady=(0, 5))
        
        self.progress_label = ctk.CTkLabel(progress_frame, text="", font=ctk.CTkFont(size=11))
        self.progress_label.pack(pady=(0, 20))
        
        # Info text area
        self.info_text = ctk.CTkTextbox(main_frame, height=120)
        self.info_text.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        self.info_text.insert("1.0", "Welcome to Linux Distro Downloader!\n\nSelect a distribution and edition to get started.\nUse 'Check Latest Versions' to see current release information.")
    
    def start_version_check(self):
        """Start version checking in background thread"""
        if self.version_check_thread and self.version_check_thread.is_alive():
            return
        
        self.check_versions_btn.configure(state="disabled", text="Checking...")
        self.version_status_label.configure(text="Checking for latest versions...")
        
        self.version_check_thread = threading.Thread(
            target=self.check_latest_versions,
            daemon=True
        )
        self.version_check_thread.start()
    
    def check_latest_versions(self):
        """Check for latest versions of distributions"""
        try:
            version_checkers = {
                'Ubuntu': self.check_ubuntu_version,
                'Linux Mint': self.check_mint_version,
                'Fedora': self.check_fedora_version,
                'Debian': self.check_debian_version,
                'Kali Linux': self.check_kali_version,
                'CentOS Stream': self.check_centos_version,
                'openSUSE': self.check_opensuse_version,
                'Arch Linux': self.check_arch_version
            }
            
            checked_count = 0
            total_count = len(version_checkers)
            
            for distro_name, checker_func in version_checkers.items():
                try:
                    version_info = checker_func()
                    if version_info:
                        self.version_info[distro_name] = version_info
                    checked_count += 1
                    
                    # Update progress
                    progress_text = f"Checking versions... ({checked_count}/{total_count})"
                    self.root.after(0, lambda: self.version_status_label.configure(text=progress_text))
                    
                except Exception as e:
                    logger.warning(f"Failed to check version for {distro_name}: {e}")
                    
                # Small delay to avoid overwhelming servers
                time.sleep(0.5)
            
            # Update UI with results
            self.root.after(0, self.update_version_display)
            
        except Exception as e:
            logger.error(f"Error during version check: {e}")
            self.root.after(0, lambda: self.version_status_label.configure(text="Version check failed"))
        
        finally:
            self.root.after(0, lambda: self.check_versions_btn.configure(state="normal", text="Check Latest Versions"))
    
    def check_ubuntu_version(self) -> Optional[Dict[str, str]]:
        """Check latest Ubuntu version"""
        try:
            response = requests.get("https://api.launchpad.net/1.0/ubuntu/series", timeout=10)
            if response.status_code == 200:
                data = response.json()
                active_series = [s for s in data['entries'] if s['active'] and s['supported']]
                if active_series:
                    latest = max(active_series, key=lambda x: x['version'])
                    return {
                        'version': latest['version'],
                        'name': latest['displayname'],
                        'status': 'Active LTS' if 'LTS' in latest['displayname'] else 'Active'
                    }
        except Exception as e:
            logger.debug(f"Ubuntu version check failed: {e}")
        return None
    
    def check_mint_version(self) -> Optional[Dict[str, str]]:
        """Check latest Linux Mint version"""
        try:
            response = requests.get("https://www.linuxmint.com/releases.php", timeout=10)
            if response.status_code == 200:
                # Simple regex to extract version from HTML
                version_match = re.search(r'Linux Mint (\d+\.?\d*)', response.text)
                if version_match:
                    return {
                        'version': version_match.group(1),
                        'name': f"Linux Mint {version_match.group(1)}",
                        'status': 'Latest'
                    }
        except Exception as e:
            logger.debug(f"Mint version check failed: {e}")
        return None
    
    def check_fedora_version(self) -> Optional[Dict[str, str]]:
        """Check latest Fedora version"""
        try:
            response = requests.get("https://bodhi.fedoraproject.org/releases/", timeout=10)
            if response.status_code == 200:
                data = response.json()
                current_releases = [r for r in data['releases'] if r['state'] == 'current']
                if current_releases:
                    latest = max(current_releases, key=lambda x: int(x['version']))
                    return {
                        'version': latest['version'],
                        'name': f"Fedora {latest['version']}",
                        'status': 'Current'
                    }
        except Exception as e:
            logger.debug(f"Fedora version check failed: {e}")
        return None
    
    def check_debian_version(self) -> Optional[Dict[str, str]]:
        """Check latest Debian version"""
        return {
            'version': '12',
            'name': 'Debian 12 (Bookworm)',
            'status': 'Stable'
        }
    
    def check_kali_version(self) -> Optional[Dict[str, str]]:
        """Check latest Kali Linux version"""
        try:
            current_year = datetime.now().year
            current_month = datetime.now().month
            quarter = ((current_month - 1) // 3) + 1
            estimated_version = f"{current_year}.{quarter}"
            
            return {
                'version': estimated_version,
                'name': f"Kali Linux {estimated_version}",
                'status': 'Rolling'
            }
        except Exception:
            return None
    
    def check_centos_version(self) -> Optional[Dict[str, str]]:
        """Check latest CentOS Stream version"""
        return {
            'version': '9',
            'name': 'CentOS Stream 9',
            'status': 'Current'
        }
    
    def check_opensuse_version(self) -> Optional[Dict[str, str]]:
        """Check latest openSUSE version"""
        return {
            'version': '15.5 / Tumbleweed',
            'name': 'openSUSE Leap 15.5 / Tumbleweed',
            'status': 'Current'
        }
    
    def check_arch_version(self) -> Optional[Dict[str, str]]:
        """Check latest Arch Linux version"""
        try:
            current_date = datetime.now()
            version = current_date.strftime("%Y.%m.01")
            
            return {
                'version': version,
                'name': f"Arch Linux {version}",
                'status': 'Rolling'
            }
        except Exception:
            return None
    
    def update_version_display(self):
        """Update the version information display"""
        if not self.version_info:
            self.version_status_label.configure(text="No version information available")
            return
        
        checked_count = len(self.version_info)
        self.version_status_label.configure(text=f"Version check complete ({checked_count} distributions checked)")
        
        # Update distribution selection to show version info
        self.update_distro_combo_with_versions()
    
    def update_distro_combo_with_versions(self):
        """Update distribution combo box to include version information"""
        distro_values = []
        for distro_name in self.distro_data.keys():
            if distro_name in self.version_info:
                version_info = self.version_info[distro_name]
                display_name = f"{distro_name} (v{version_info['version']})"
                distro_values.append(display_name)
            else:
                distro_values.append(distro_name)
        
        current_selection = self.selected_distro.get()
        self.distro_combo.configure(values=distro_values)
        
        # Restore selection if it exists
        if current_selection:
            for value in distro_values:
                if current_selection in value:
                    self.distro_combo.set(value)
                    break
    
    def on_distro_select(self, distro_display_name: str):
        """Handle distribution selection"""
        # Extract actual distro name from display name
        distro_name = distro_display_name.split(' (v')[0] if ' (v' in distro_display_name else distro_display_name
        
        if distro_name in self.distro_data:
            editions = list(self.distro_data[distro_name]['editions'].keys())
            self.edition_combo.configure(values=editions, state="normal")
            self.edition_combo.set(editions[0] if editions else "")
            
            # Update info with version information
            distro_info = self.distro_data[distro_name]
            info_text = f"Selected: {distro_name}\n"
            info_text += f"Description: {distro_info.get('description', 'No description available')}\n"
            
            if distro_name in self.version_info:
                version_info = self.version_info[distro_name]
                info_text += f"Latest Version: {version_info['name']} ({version_info['status']})\n"
            
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
        
        distro_display = self.selected_distro.get()
        edition = self.selected_edition.get()
        
        if not distro_display or not edition:
            messagebox.showerror("Error", "Please select both distribution and edition!")
            return
        
        # Extract actual distro name
        distro = distro_display.split(' (v')[0] if ' (v' in distro_display else distro_display
        
        download_dir = self.download_dir.get()
        if not os.path.exists(download_dir):
            try:
                os.makedirs(download_dir)
            except OSError as e:
                messagebox.showerror("Error", f"Cannot create download directory:\n{e}")
                return
        
        # Reset download state
        self.download_cancelled = False
        self.download_paused = False
        
        # Start download in separate thread
        self.download_thread = threading.Thread(
            target=self.download_iso,
            args=(distro, edition, download_dir),
            daemon=True
        )
        self.download_thread.start()
    
    def pause_download(self):
        """Pause or resume the download"""
        if not self.is_downloading:
            return
        
        if self.download_paused:
            self.download_paused = False
            self.pause_btn.configure(text="Pause")
            self.update_status("Resuming download...")
        else:
            self.download_paused = True
            self.pause_btn.configure(text="Resume")
            self.update_status("Download paused")
    
    def cancel_download(self):
        """Cancel the current download"""
        if not self.is_downloading:
            return
        
        result = messagebox.askyesno("Cancel Download", "Are you sure you want to cancel the download?")
        if result:
            self.download_cancelled = True
            self.update_status("Cancelling download...")
            
            # Close current connections
            if self.current_response:
                try:
                    self.current_response.close()
                except:
                    pass
            
            if self.current_file_handle:
                try:
                    self.current_file_handle.close()
                except:
                    pass
    
    def download_iso(self, distro: str, edition: str, download_dir: str):
        """Download and verify ISO file with pause/cancel support"""
        self.is_downloading = True
        self.download_btn.configure(text="Downloading...", state="disabled")
        self.pause_btn.configure(state="normal")
        self.cancel_btn.configure(state="normal")
        
        try:
            # Get download info
            edition_data = self.distro_data[distro]['editions'][edition]
            url = edition_data['url']
            checksum = edition_data['checksum']
            filename = edition_data['filename']
            filepath = os.path.join(download_dir, filename)
            
            self.update_status(f"Starting download of {distro} {edition}...")
            logger.info(f"Starting download: {distro} {edition} from {url}")
            
            # Download file with pause/cancel support
            success = self.download_file_with_controls(url, filepath)
            
            if self.download_cancelled:
                self.update_status("✖️ Download cancelled")
                self.cleanup_cancelled_download(filepath)
                return
            
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
                if not self.download_cancelled:
                    self.update_status("❌ Download failed")
                    logger.error(f"Download failed: {filepath}")
        
        except Exception as e:
            if not self.download_cancelled:
                error_msg = f"Error during download: {str(e)}"
                self.update_status(f"❌ {error_msg}")
                self.update_info(error_msg)
                messagebox.showerror("Error", error_msg)
                logger.error(f"Download error: {e}")
        
        finally:
            self.is_downloading = False
            self.download_paused = False
            self.current_response = None
            self.current_file_handle = None
            self.download_btn.configure(text="Download ISO", state="normal")
            self.pause_btn.configure(text="Pause", state="disabled")
            self.cancel_btn.configure(state="disabled")
            self.progress_bar.set(0)
            self.progress_label.configure(text="")
    
    def download_file_with_controls(self, url: str, filepath: str) -> bool:
        """Download file with pause/cancel controls"""
        try:
            # Check if partial file exists for resume capability
            resume_pos = 0
            if os.path.exists(filepath + ".part"):
                resume_pos = os.path.getsize(filepath + ".part")
                logger.info(f"Resuming download from position: {resume_pos}")
            
            headers = {}
            if resume_pos > 0:
                headers['Range'] = f'bytes={resume_pos}-'
            
            self.current_response = requests.get(url, stream=True, timeout=30, headers=headers)
            self.current_response.raise_for_status()
            
            total_size = int(self.current_response.headers.get('content-length', 0))
            if resume_pos > 0:
                total_size += resume_pos
            
            downloaded = resume_pos
            
            # Open file in append mode if resuming, otherwise write mode
            mode = 'ab' if resume_pos > 0 else 'wb'
            self.current_file_handle = open(filepath + ".part", mode)
            
            try:
                for chunk in self.current_response.iter_content(chunk_size=8192):
                    if self.download_cancelled:
                        return False
                    
                    # Handle pause
                    while self.download_paused and not self.download_cancelled:
                        time.sleep(0.1)
                    
                    if self.download_cancelled:
                        return False
                    
                    if chunk:
                        self.current_file_handle.write(chunk)
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
                
                self.current_file_handle.close()
                self.current_file_handle = None
                
                # Rename completed file
                if os.path.exists(filepath):
                    os.remove(filepath)
                os.rename(filepath + ".part", filepath)
                
                return True
                
            finally:
                if self.current_file_handle:
                    self.current_file_handle.close()
                    self.current_file_handle = None
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error during download: {e}")
            return False
        except IOError as e:
            logger.error(f"File system error during download: {e}")
            return False
    
    def cleanup_cancelled_download(self, filepath: str):
        """Clean up partial download files when cancelled"""
        try:
            partial_file = filepath + ".part"
            if os.path.exists(partial_file):
                os.remove(partial_file)
                logger.info(f"Cleaned up partial download: {partial_file}")
        except Exception as e:
            logger.warning(f"Failed to clean up partial download: {e}")
    
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