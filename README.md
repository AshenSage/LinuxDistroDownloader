# Linux Distro Downloader

A modern, user-friendly GUI application for downloading and verifying official Linux distribution ISO files. Built with Python and CustomTkinter for a sleek, native-looking interface.

![Linux Distro Downloader](https://img.shields.io/badge/Python-3.8%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey)
![Version](https://img.shields.io/badge/Version-1.1.0-brightgreen)

## ✨ Features

- **Modern GUI**: Clean, intuitive interface built with CustomTkinter
- **Download Control**: Pause, resume, and cancel downloads with smart retry mechanisms
- **Version Checking**: Real-time checking of latest distribution versions from official sources
- **Multiple Distributions**: Support for 8 popular Linux distributions:
  - Ubuntu (Desktop & Server LTS)
  - Linux Mint (Cinnamon, MATE, XFCE)
  - Fedora (Workstation & Server)
  - Debian (Standard DVD & Netinst)
  - Kali Linux (Live & Installer)
  - CentOS Stream (DVD & Boot ISO)
  - openSUSE (Leap & Tumbleweed)
  - Arch Linux
- **Smart Progress Tracking**: Live download progress with speed, ETA, and resume capability
- **Automatic Verification**: SHA256 checksum verification for file integrity
- **Robust Downloads**: Built-in error handling, pause/resume, and retry mechanisms
- **Flexible Storage**: Choose your preferred download directory
- **Comprehensive Logging**: Detailed logs for troubleshooting

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Internet connection for downloads

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/AshenSage/LinuxDistroDownloader.git
   cd LinuxDownloaderWithClaude
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application:**
   ```bash
   python main.py
   ```

## 📱 Usage

### Basic Download Process

1. **Check Versions** (Optional): Click "Check Latest Versions" to see current release information
2. **Select Distribution**: Choose your desired Linux distribution from the dropdown menu
3. **Choose Edition**: Pick the specific edition/variant you want to download
4. **Set Download Directory**: Specify where you want to save the ISO file (defaults to Downloads folder)
5. **Download**: Click "Download ISO" to start the process
6. **Monitor Progress**: Watch real-time download progress and status updates
7. **Control Download**: Use Pause/Resume or Cancel buttons as needed
8. **Verification**: The application automatically verifies file integrity using checksums

### Download Controls

- **Pause/Resume**: Click "Pause" during download to pause, click "Resume" to continue
- **Cancel**: Click "Cancel" to abort download (with confirmation dialog)
- **Resume Interrupted**: Restart a cancelled download to resume from where it left off

### Version Checking

- Click "Check Latest Versions" to fetch current version information
- Distribution dropdown will show latest versions when available
- Information panel displays version details and release status

## 📝 Supported Distributions

| Distribution | Editions | Version Checking | Auto-Update |
|--------------|----------|------------------|-------------|
| **Ubuntu** | Desktop LTS, Server LTS | ✅ Launchpad API | 22.04.3 LTS |
| **Linux Mint** | Cinnamon, MATE, XFCE | ✅ Website Parsing | 21.2 |
| **Fedora** | Workstation, Server | ✅ Bodhi API | 39 |
| **Debian** | Standard DVD, Netinst | ✅ Release Info | 12.2.0 |
| **Kali Linux** | Live, Installer | ✅ Rolling Estimation | 2023.3 |
| **CentOS Stream** | DVD ISO, Boot ISO | ✅ Current Version | 9 |
| **openSUSE** | Leap, Tumbleweed | ✅ Release Info | 15.5 / Current |
| **Arch Linux** | ISO | ✅ Rolling Dating | 2023.11.01 |

## 🆕 What's New in v1.1.0

### Download Control Features
- **Pause/Resume**: Full control over download process
- **Smart Cancellation**: Safe download abortion with cleanup
- **Resume Support**: Continue interrupted downloads automatically
- **Enhanced Error Handling**: Better recovery from network issues

### Version Checking System
- **Real-time Version Info**: Check latest distribution versions
- **API Integration**: Official sources for accurate version data
- **Visual Indicators**: Version info displayed in distribution selection
- **Multi-source Support**: Different checking methods per distribution

### User Interface Improvements
- **Enhanced Layout**: Better organization and visual hierarchy
- **Control Buttons**: Dedicated pause/resume and cancel functionality
- **Status Indicators**: Emoji-enhanced status messages
- **Progress Tracking**: Improved download progress visualization

## 🔧 Configuration

### Adding New Distributions

To add new Linux distributions or update existing ones, modify the `distro_data.json` file:

```json
{
  "Distribution Name": {
    "description": "Brief description of the distribution",
    "editions": {
      "Edition Name": {
        "filename": "actual-iso-filename.iso",
        "url": "https://direct-download-url.com/file.iso",
        "checksum": "sha256-checksum-hash"
      }
    }
  }
}
```

### Checksum Sources

Ensure you obtain checksums from official sources:
- **Ubuntu**: `https://releases.ubuntu.com/`
- **Linux Mint**: `https://linuxmint.com/verify.php`
- **Fedora**: `https://getfedora.org/security/`
- **Debian**: `https://cdimage.debian.org/debian-cd/`
- **Kali**: `https://www.kali.org/get-kali/`

## 📊 Advanced Features

### Download Resume
- Partial downloads are automatically saved as `.part` files
- Resume interrupted downloads by restarting the same download
- Smart byte-range requests for efficient resumption

### Version API Integration
- **Ubuntu**: Launchpad API for official release information
- **Fedora**: Bodhi API for current releases
- **Linux Mint**: Website parsing for latest versions
- **Others**: Custom checkers for each distribution type

### Error Recovery
- Automatic retry on network failures
- Graceful handling of server timeouts
- Smart recovery from partial download corruption

## 📊 Logging

The application creates detailed logs in `downloader.log` for:
- Download progress and completion
- Version checking results
- Checksum verification results
- Error messages and troubleshooting information
- Application startup and shutdown events
- Download pause/resume/cancel operations

## ⚠️ Important Notes

- **File Sizes**: Linux ISOs are typically 1-4GB in size
- **Download Time**: Varies based on your internet connection speed
- **Disk Space**: Ensure sufficient free space in your download directory
- **Checksums**: Always verify checksums match official sources
- **Resume Capability**: Interrupted downloads can be resumed
- **Version Updates**: Use version checking to ensure you have current releases

## 🔍 Troubleshooting

### Common Issues

1. **Download Fails**:
   - Check internet connection
   - Verify download directory permissions
   - Check available disk space
   - Review logs in `downloader.log`
   - Try resuming the download

2. **Checksum Verification Fails**:
   - Re-download the file
   - Verify the expected checksum is correct
   - Check for file corruption during download
   - Ensure complete download (not partial)

3. **GUI Not Starting**:
   - Ensure Python 3.8+ is installed
   - Install/update dependencies: `pip install -r requirements.txt`
   - Check for missing `distro_data.json` file

4. **Version Checking Fails**:
   - Check internet connection
   - Some distributions may have API limitations
   - Version info is cached and updated periodically

### Advanced Troubleshooting

- **Partial Downloads**: Look for `.part` files in download directory
- **Network Issues**: Check firewall and proxy settings
- **API Timeouts**: Version checking may fail on slow connections
- **Thread Issues**: Restart application if downloads become unresponsive

## 🔒 Security

- All downloads use HTTPS when available
- SHA256 checksums verify file integrity
- No data is collected or transmitted beyond download requests
- Source code is open for security auditing
- Version checking uses official APIs and sources
- Safe handling of partial downloads and cleanup

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to:

1. **Report Issues**: Use GitHub Issues for bug reports
2. **Suggest Features**: Request new distributions or features
3. **Update Data**: Help keep distribution data current
4. **Code Improvements**: Submit pull requests for enhancements
5. **Version Checkers**: Add support for new distribution APIs

### Development Setup

```bash
# Clone the repository
git clone https://github.com/AshenSage/LinuxDownloaderWithClaude.git
cd LinuxDownloaderWithClaude

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

## 🚀 Future Enhancements

- [ ] Torrent download support
- [ ] Batch download multiple ISOs
- [ ] Automatic distribution data updates
- [ ] USB creation wizard
- [ ] Download scheduling
- [ ] Mirror selection for faster downloads
- [ ] Download history and management
- [ ] Notification system for completed downloads
- [ ] Dark/Light theme toggle
- [ ] Enhanced version checking with release notes

## 📞 Support

If you encounter issues or need help:

1. Check the [Troubleshooting](#-troubleshooting) section
2. Review `downloader.log` for detailed error information
3. Search existing [GitHub Issues](https://github.com/AshenSage/LinuxDownloaderWithClaude/issues)
4. Create a new issue with detailed information
5. Check the [Changelog](CHANGELOG.md) for recent updates

## 🙏 Acknowledgments

- Built with [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) for modern GUI
- Inspired by the need for a simple, reliable Linux ISO downloader
- Created with assistance from Claude AI
- Thanks to all Linux distribution maintainers for their excellent work
- Community contributors for testing and feedback

---

**Happy Linux exploring! 🐧**

*Note: This application downloads ISOs from official distribution sources. Always verify checksums and download from trusted mirrors. Version information is fetched from official APIs and websites.*
