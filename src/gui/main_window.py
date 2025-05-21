import os
import logging
import time # Added for simulated delays
import random # Added for simulated delays

from PyQt6.QtWidgets import (QMainWindow, QTableWidgetItem, QHeaderView,
                             QMessageBox, QListWidget, QDialog) # Added QDialog for SettingsDialog placeholder
from PyQt6.QtCore import Qt, QSettings, QThreadPool, pyqtSignal, pyqtSlot, QTimer # Corrected Signal and Slot imports

# Import the generated UI class
from .main_window_ui import Ui_MainWindow

# Import core components (assuming they will be implemented in core/ and data/)
# These imports are placeholders and will require the actual files to exist.
# from src.core.update_checker import CheckUpdateRunnable
# from src.core.downloader import DownloadRunnable
# from src.data.config_manager import ConfigManager # For more complex settings management

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Setup logging for this class
        self.logger = logging.getLogger(__name__)
        self.logger.info("Initializing MainWindow...")

        # Create an instance of the generated UI
        self.ui = Ui_MainWindow()
        # Set up the UI on this QMainWindow instance
        self.ui.setupUi(self)

        # --- Thread Pool for concurrency ---
        self.threadpool = QThreadPool()
        self.threadpool.setMaxThreadCount(5) # Limit concurrent threads
        self.logger.info(f"Initialized thread pool with max {self.threadpool.maxThreadCount()} threads for MainWindow.")

        # --- Configuration Management (using QSettings for simplicity) ---
        self.settings = QSettings("MyOrg", "LinuxISODownloader")

        # --- Internal State for tracked distributions ---
        # This dictionary will store the state of checkable menu items.
        # Key: "Distro_Edition" (e.g., "Ubuntu_Desktop", "Fedora_Workstation")
        # Value: True if checked, False if unchecked
        self.tracked_distros_config = {}
        self._initialize_tracked_distros_config() # Populate with all available actions

        # --- Initial setup for the table ---
        self.ui.tableWidget_availableDistros.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.Stretch # Distribution
        )
        self.ui.tableWidget_availableDistros.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.ResizeToContents # Latest Version
        )
        self.ui.tableWidget_availableDistros.horizontalHeader().setSectionResizeMode(
            2, QHeaderView.ResizeMode.ResizeToContents # Status
        )
        self.ui.tableWidget_availableDistros.horizontalHeader().setSectionResizeMode(
            3, QHeaderView.ResizeMode.Stretch # Download URL (can be hidden later)
        )
        # self.ui.tableWidget_availableDistros.setColumnHidden(3, True) # Optionally hide URL column

        # --- Connect signals to slots ---
        self.ui.pushButton_checkForUpdates.clicked.connect(self.check_for_updates)
        self.ui.pushButton_downloadSelected.clicked.connect(self.download_selected_iso)
        self.ui.actionSettings.triggered.connect(self.show_settings_dialog)
        self.ui.actionExit.triggered.connect(self.close)

        # Connect all checkable distro actions to a generic handler
        self._connect_distro_actions()

        # Load the saved state of the tracked distributions
        self._load_tracked_distros_state()

        # Initial display of tracked distributions (will be empty until check_for_updates is run)
        self.update_available_distros_table()

        self.logger.info("MainWindow initialization complete.")

    def _initialize_tracked_distros_config(self):
        """
        Initializes the tracked_distros_config dictionary with all checkable actions
        from the UI, setting their initial state to False.
        """
        # Helper to get all QAction objects from a menu
        def get_all_actions(menu):
            actions = []
            for action in menu.actions():
                if action.menu(): # If it's a submenu
                    actions.extend(get_all_actions(action.menu()))
                elif action.isCheckable():
                    actions.append(action)
            return actions

        # Get all checkable actions from the 'Distros' menu
        all_distro_actions = get_all_actions(self.ui.menuDistros)

        for action in all_distro_actions:
            # Use object name for unique identification (e.g., "actionUbuntu_Desktop")
            self.tracked_distros_config[action.objectName()] = False
        self.logger.debug(f"Initialized tracked_distros_config with {len(self.tracked_distros_config)} actions.")


    def _connect_distro_actions(self):
        """Connects the toggled signal of each checkable distro action."""
        # Helper to get all QAction objects from a menu
        def get_all_actions(menu):
            actions = []
            for action in menu.actions():
                if action.menu(): # If it's a submenu
                    actions.extend(get_all_actions(action.menu()))
                elif action.isCheckable():
                    actions.append(action)
            return actions

        all_distro_actions = get_all_actions(self.ui.menuDistros)

        for action in all_distro_actions:
            action.toggled.connect(lambda checked, a=action: self._on_distro_action_toggled(a, checked))
        self.logger.debug("Connected all checkable distro actions.")


    @pyqtSlot(object, bool) # object for QAction, bool for checked state
    def _on_distro_action_toggled(self, action, checked):
        """Handler for when a distro menu action's check state changes."""
        self.tracked_distros_config[action.objectName()] = checked
        self.logger.info(f"Distro '{action.text()}' ({action.objectName()}) toggled: {checked}")
        self._save_tracked_distros_state() # Save state immediately
        # You might want to trigger an update to the table or a check for updates here
        # self.update_available_distros_table() # Or simply mark for re-check


    def _load_tracked_distros_state(self):
        """Loads the saved state of tracked distributions from QSettings."""
        for action_name, default_state in self.tracked_distros_config.items():
            # Get the actual QAction object using its objectName
            action = self.findChild(type(self.ui.actionUbuntu_Desktop), action_name) # Use type of any action
            if action:
                saved_state = self.settings.value(f"tracked_distros/{action_name}", default_state, type=bool)
                action.setChecked(saved_state)
                self.tracked_distros_config[action_name] = saved_state
        self.logger.info("Loaded tracked distributions state from settings.")


    def _save_tracked_distros_state(self):
        """Saves the current state of tracked distributions to QSettings."""
        for action_name, state in self.tracked_distros_config.items():
            self.settings.setValue(f"tracked_distros/{action_name}", state)
        self.logger.info("Saved tracked distributions state to settings.")


    def update_available_distros_table(self, data=None):
        """
        Updates the tableWidget_availableDistros with data.
        If data is None, it clears the table.
        Data format: list of dictionaries, e.g.,
        [{'distro': 'Ubuntu Desktop', 'version': '24.04 LTS', 'status': 'Checking...', 'url': 'http://...'}, ...]
        """
        self.ui.tableWidget_availableDistros.setRowCount(0)
        if data:
            for row_data in data:
                row_position = self.ui.tableWidget_availableDistros.rowCount()
                self.ui.tableWidget_availableDistros.insertRow(row_position)
                self.ui.tableWidget_availableDistros.setItem(row_position, 0, QTableWidgetItem(row_data.get('distro', 'N/A')))
                self.ui.tableWidget_availableDistros.setItem(row_position, 1, QTableWidgetItem(row_data.get('version', 'N/A')))
                self.ui.tableWidget_availableDistros.setItem(row_position, 2, QTableWidgetItem(row_data.get('status', 'N/A')))
                self.ui.tableWidget_availableDistros.setItem(row_position, 3, QTableWidgetItem(row_data.get('url', 'N/A')))
            self.ui.tableWidget_availableDistros.resizeColumnsToContents()
        self.logger.debug("Available distributions table updated.")


    def check_for_updates(self):
        """
        Initiates checking for updates for all currently tracked distributions
        (based on the menu checkmarks).
        """
        self.ui.label_status.setText("Checking for updates...")
        self.logger.info("Initiating update check for selected distributions.")

        distros_to_check = []
        for action_name, is_checked in self.tracked_distros_config.items():
            if is_checked:
                # Convert action_name (e.g., "actionUbuntu_Desktop") to a more readable format
                # and map to actual check URLs. This mapping is crucial and needs to be robust.
                distro_info = self._map_action_to_distro_info(action_name)
                if distro_info:
                    distros_to_check.append(distro_info)
                else:
                    self.logger.warning(f"No mapping found for action: {action_name}")
                    self.ui.label_status.setText(f"Warning: No info for {action_name.replace('action', '').replace('_', ' ')}")

        if not distros_to_check:
            self.ui.label_status.setText("No distributions selected for tracking. Check 'Distros' menu.")
            QMessageBox.information(self, "No Selection", "Please select at least one distribution from the 'Distros' menu to track.")
            return

        # Clear the table and show "Checking..." status
        self.update_available_distros_table([
            {'distro': info['display_name'], 'version': 'N/A', 'status': 'Checking...', 'url': ''}
            for info in distros_to_check
        ])

        # --- Placeholder for actual update checking logic ---
        # You would loop through distros_to_check and start CheckUpdateRunnable instances
        # For demonstration, we'll simulate an update
        self.logger.info(f"Starting simulated update checks for {len(distros_to_check)} distros.")
        # Example of how you might start a worker (requires CheckUpdateRunnable class)
        # for distro_info in distros_to_check:
        #     worker = CheckUpdateRunnable(distro_info['display_name'], distro_info['check_url'])
        #     worker.signals.update_available.connect(self.handle_update_available)
        #     worker.signals.check_completed.connect(self.handle_check_completed)
        #     worker.signals.error.connect(self.handle_check_error)
        #     self.threadpool.start(worker)

        # Simulate some results for demonstration
        simulated_results = []
        for distro_info in distros_to_check:
            time.sleep(random.uniform(0.5, 1.5)) # Simulate network delay
            if "Ubuntu_Desktop" in distro_info['action_name']:
                simulated_results.append({
                    'distro': distro_info['display_name'],
                    'version': '24.04 LTS',
                    'status': 'Update Available',
                    'url': 'http://releases.ubuntu.com/24.04/ubuntu-24.04-desktop-amd64.iso'
                })
            elif "Fedora_Workstation" in distro_info['action_name']:
                simulated_results.append({
                    'distro': distro_info['display_name'],
                    'version': '40',
                    'status': 'Up-to-date',
                    'url': 'https://download.fedoraproject.org/pub/fedora/linux/releases/40/Workstation/x86_64/iso/Fedora-Workstation-Live-x86_64-40-1.10.iso'
                })
            elif "Kali_Desktop" in distro_info['action_name']:
                 simulated_results.append({
                    'distro': distro_info['display_name'],
                    'version': '2024.2',
                    'status': 'Update Available',
                    'url': 'https://cdimage.kali.org/kali-2024.2/kali-linux-2024.2-installer-amd64.iso'
                })
            else:
                simulated_results.append({
                    'distro': distro_info['display_name'],
                    'version': 'N/A',
                    'status': 'Check Failed (Simulated)',
                    'url': ''
                })
        self.update_available_distros_table(simulated_results)
        self.ui.label_status.setText("Update check complete (simulated).")
        self.logger.info("Simulated update check complete.")


    def _map_action_to_distro_info(self, action_name):
        """
        Maps a QAction object name to detailed distribution information
        including display name and (placeholder) check URL.
        This is where you'd define the specific URLs for each distro/edition.
        """
        mapping = {
            "actionUbuntu_Desktop": {"display_name": "Ubuntu Desktop", "check_url": "http://releases.ubuntu.com/", "action_name": "actionUbuntu_Desktop"},
            "actionUbuntu_Server": {"display_name": "Ubuntu Server", "check_url": "http://releases.ubuntu.com/", "action_name": "actionUbuntu_Server"},
            "actionUbuntu_Kubuntu": {"display_name": "Kubuntu", "check_url": "http://releases.ubuntu.com/kubuntu/", "action_name": "actionUbuntu_Kubuntu"},
            "actionUbuntu_Xubuntu": {"display_name": "Xubuntu", "check_url": "http://releases.ubuntu.com/xubuntu/", "action_name": "actionUbuntu_Xubuntu"},
            "actionFedora_Workstation": {"display_name": "Fedora Workstation", "check_url": "https://getfedora.org/en/workstation/download/", "action_name": "actionFedora_Workstation"},
            "actionFedora_Server": {"display_name": "Fedora Server", "check_url": "https://getfedora.org/en/server/download/", "action_name": "actionFedora_Server"},
            "actionFedora_KDE": {"display_name": "Fedora KDE Spin", "check_url": "https://spins.fedoraproject.org/kde/", "action_name": "actionFedora_KDE"},
            "actionKali_Desktop": {"display_name": "Kali Linux Desktop", "check_url": "https://www.kali.org/get-kali/#kali-installer-images", "action_name": "actionKali_Desktop"},
            "actionKali_Purple": {"display_name": "Kali Linux Purple", "check_url": "https://www.kali.org/get-kali/#kali-installer-images", "action_name": "actionKali_Purple"},
            "actionKali_Light": {"display_name": "Kali Linux Light", "check_url": "https://www.kali.org/get-kali/#kali-installer-images", "action_name": "actionKali_Light"},
        }
        return mapping.get(action_name)


    def download_selected_iso(self):
        """Initiates download for the currently selected ISO in the table."""
        selected_rows = self.ui.tableWidget_availableDistros.selectionModel().selectedRows()
        if not selected_rows:
            self.ui.label_status.setText("Please select a distribution to download.")
            QMessageBox.warning(self, "No Selection", "Please select a distribution from the table to download.")
            return

        # Assuming single selection for now
        selected_row_index = selected_rows[0].row()
        distro_name = self.ui.tableWidget_availableDistros.item(selected_row_index, 0).text()
        download_url = self.ui.tableWidget_availableDistros.item(selected_row_index, 3).text()
        status_text = self.ui.tableWidget_availableDistros.item(selected_row_index, 2).text()

        if not download_url or download_url == "N/A":
            self.ui.label_status.setText(f"No valid download URL for {distro_name}.")
            QMessageBox.warning(self, "Download Error", f"No valid download URL found for {distro_name}.")
            return

        if "Download" in status_text or "Downloading" in status_text:
            self.ui.label_status.setText(f"{distro_name} is already being downloaded or is in queue.")
            QMessageBox.information(self, "Download Status", f"Download for {distro_name} is already in progress or queued.")
            return

        self.ui.label_status.setText(f"Attempting to download {distro_name}...")
        self.logger.info(f"Attempting to download {distro_name} from {download_url}")

        # --- Placeholder for actual download logic ---
        # You would start a DownloadRunnable instance here
        # Example:
        # from src.core.downloader import DownloadRunnable # Make sure this import is uncommented
        # download_dir = self.settings.value("download_directory", os.path.expanduser("~"), type=str)
        # worker = DownloadRunnable(distro_name, download_url, download_dir)
        # worker.signals.progress.connect(self.update_download_progress)
        # worker.signals.completed.connect(self.handle_download_completed)
        # worker.signals.error.connect(self.handle_download_error)
        # worker.signals.checksum_verified.connect(self.handle_checksum_verified)
        # self.threadpool.start(worker)
        # self.ongoing_downloads[distro_name] = worker

        # Simulate download status change in table
        self.ui.tableWidget_availableDistros.setItem(selected_row_index, 2, QTableWidgetItem("Downloading... (Simulated)"))
        self.ui.progressBar_overall.setValue(0) # Reset progress bar for new download

        # Simulate progress bar update (in a real app, this comes from DownloadRunnable signals)
        self.simulated_download_progress = 0
        self.simulated_download_timer = QTimer(self)
        self.simulated_download_timer.setInterval(100) # Update every 100ms
        self.simulated_download_timer.timeout.connect(lambda: self._simulate_download_progress(distro_name, selected_row_index))
        self.simulated_download_timer.start()


    def _simulate_download_progress(self, distro_name, row_index):
        """Simulates download progress for demonstration."""
        self.simulated_download_progress += 2
        if self.simulated_download_progress > 100:
            self.simulated_download_progress = 100
            self.simulated_download_timer.stop()
            self.ui.label_status.setText(f"Simulated download of {distro_name} complete.")
            self.ui.tableWidget_availableDistros.setItem(row_index, 2, QTableWidgetItem("Download Complete (Simulated)"))
            # Simulate checksum verification
            self.ui.tableWidget_availableDistros.setItem(row_index, 3, QTableWidgetItem("Checksum Valid (Simulated)"))
            self.ui.tableWidget_availableDistros.item(row_index, 3).setForeground(Qt.GlobalColor.darkGreen)
            return

        self.ui.progressBar_overall.setValue(self.simulated_download_progress)
        # Update table status with simulated progress
        self.ui.tableWidget_availableDistros.setItem(row_index, 2, QTableWidgetItem(f"Downloading... {self.simulated_download_progress}%"))


    # Placeholder for actual update_download_progress from DownloadRunnable
    # @pyqtSlot(str, int, int)
    # def update_download_progress(self, distro_name, bytes_downloaded, total_bytes):
    #     # Find the correct row in the downloads table (or main table if showing progress there)
    #     # Update progress bar and status text
    #     pass

    # Placeholder for actual handle_download_completed from DownloadRunnable
    # @pyqtSlot(str, str)
    # def handle_download_completed(self, distro_name, file_path):
    #     self.ui.label_status.setText(f"Download complete for {distro_name}.")
    #     # Update table status
    #     # Trigger checksum verification
    #     pass

    # Placeholder for actual handle_download_error from DownloadRunnable
    # @pyqtSlot(str, str)
    # def handle_download_error(self, distro_name, error_message):
    #     self.ui.label_status.setText(f"Download failed for {distro_name}: {error_message}")
    #     # Update table status
    #     pass

    # Placeholder for actual handle_checksum_verified from DownloadRunnable
    # @pyqtSlot(str, bool, str)
    # def handle_checksum_verified(self, distro_name, is_valid, message):
    #     # Update table checksum status
    #     pass

    def show_settings_dialog(self):
        """Opens the settings dialog."""
        self.ui.label_status.setText("Opening settings...")
        # Placeholder: You will need to create src/gui/settings_dialog.py
        # from src.gui.settings_dialog import SettingsDialog
        # dialog = SettingsDialog(self)
        # if dialog.exec() == QDialog.DialogCode.Accepted:
        #     # Handle settings saved
        #     pass
        QMessageBox.information(self, "Settings", "Settings dialog not yet implemented.")


    # --- Graceful Shutdown ---
    def closeEvent(self, event):
        """Handles the window closing event, saving settings."""
        self.logger.info("Application close event triggered.")
        # Save the state of tracked distributions
        self._save_tracked_distros_state()

        # Check for ongoing downloads (if you implement self.ongoing_downloads)
        # if hasattr(self, 'ongoing_downloads') and self.ongoing_downloads:
        #     reply = QMessageBox.question(self, "Confirm Exit",
        #                                  "Downloads are in progress. Are you sure you want to exit?",
        #                                  QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        #     if reply == QMessageBox.StandardButton.Yes:
        #         # Signal ongoing downloads to cancel and wait for threads
        #         for download_worker in list(self.ongoing_downloads.values()):
        #             download_worker.cancel()
        #         self.threadpool.waitForDone(5000) # Wait up to 5 seconds
        #         self.logger.info("Application exiting gracefully after cancelling downloads.")
        #         event.accept()
        #     else:
        #         event.ignore()
        # else:
        self.logger.info("Application exiting.")
        event.accept()

