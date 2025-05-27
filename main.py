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
            
            # Update server info if first edition is selected
            if editions:
                self.update_server_info(distro_name, editions[0])
    
    def on_edition_select(self, edition_name: str):
        """Handle edition selection"""
        distro_display = self.selected_distro.get()
        if distro_display:
            distro_name = distro_display.split(' (v')[0] if ' (v' in distro_display else distro_display
            self.update_server_info(distro_name, edition_name)
    
    def update_server_info(self, distro_name: str, edition_name: str):
        """Update server information display"""
        try:
            edition_info = self.distro_data[distro_name]['editions'][edition_name]
            url = edition_info['url']
            
            # Get server information
            server_info = self.get_server_info(url)
            
            # Format server information text
            info_text = f"🌐 Domain: {server_info['domain']}\n"
            info_text += f"🖥️  IP Address: {server_info['ip']}\n"
            info_text += f"{server_info['flag']} Country: {server_info['country_name']}"
            
            self.server_info_text.configure(text=info_text)
            
        except Exception as e:
            logger.warning(f"Failed to update server info: {e}")
            self.server_info_text.configure(text="Server information unavailable")
    
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