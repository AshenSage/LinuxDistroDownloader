# Linux Distro Downloader

A modern, user-friendly GUI application for downloading and verifying official Linux distribution ISO files. Built with Python and CustomTkinter for a sleek, native-looking interface.

![Linux Distro Downloader](https://img.shields.io/badge/Python-3.8%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey)

## ✨ Features

- **Modern GUI**: Clean, intuitive interface built with CustomTkinter
- **Multiple Distributions**: Support for 8 popular Linux distributions:
  - Ubuntu (Desktop & Server LTS)
  - Linux Mint (Cinnamon, MATE, XFCE)
  - Fedora (Workstation & Server)
  - Debian (Standard DVD & Netinst)
  - Kali Linux (Live & Installer)
  - CentOS Stream (DVD & Boot ISO)
  - openSUSE (Leap & Tumbleweed)
  - Arch Linux
- **Real-time Progress**: Live download progress with speed and completion percentage
- **Automatic Verification**: SHA256 checksum verification for file integrity
- **Robust Downloads**: Built-in error handling and retry mechanisms
- **Flexible Storage**: Choose your preferred download directory
- **Comprehensive Logging**: Detailed logs for troubleshooting

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Internet connection for downloads

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/AshenSage/LinuxDownloaderWithClaude.git
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

1. **Select Distribution**: Choose your desired Linux distribution from the dropdown menu
2. **Choose Edition**: Pick the specific edition/variant you want to download
3. **Set Download Directory**: Specify where you want to save the ISO file (defaults to Downloads folder)
4. **Download**: Click "Download ISO" to start the process
5. **Monitor Progress**: Watch real-time download progress and status updates
6. **Verification**: The application automatically verifies file integrity using checksums

## 📝 Supported Distributions

| Distribution | Editions | Latest Version |
|--------------|----------|----------------|
| **Ubuntu** | Desktop LTS, Server LTS | 22.04.3 LTS |
| **Linux Mint** | Cinnamon, MATE, XFCE | 21.2 |
| **Fedora** | Workstation, Server | 39 |
| **Debian** | Standard DVD, Netinst | 12.2.0 |
| **Kali Linux** | Live, Installer | 2023.3 |
| **CentOS Stream** | DVD ISO, Boot ISO | 9 |
| **openSUSE** | Leap, Tumbleweed | 15.5 / Current |
| **Arch Linux** | ISO | 2023.11.01 |

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

## 📊 Logging

The application creates detailed logs in `downloader.log` for:
- Download progress and completion
- Checksum verification results
- Error messages and troubleshooting information
- Application startup and shutdown events

## ⚠️ Important Notes

- **File Sizes**: Linux ISOs are typically 1-4GB in size
- **Download Time**: Varies based on your internet connection speed
- **Disk Space**: Ensure sufficient free space in your download directory
- **Checksums**: Always verify checksums match official sources
- **Updates**: Distribution data may need periodic updates for new releases

## 🔍 Troubleshooting

### Common Issues

1. **Download Fails**:
   - Check internet connection
   - Verify download directory permissions
   - Check available disk space
   - Review logs in `downloader.log`

2. **Checksum Verification Fails**:
   - Re-download the file
   - Verify the expected checksum is correct
   - Check for file corruption during download

3. **GUI Not Starting**:
   - Ensure Python 3.8+ is installed
   - Install/update dependencies: `pip install -r requirements.txt`
   - Check for missing `distro_data.json` file

### Error Codes

- **Network Errors**: Connection timeout, DNS resolution issues
- **File System Errors**: Permission denied, disk full, invalid path
- **Verification Errors**: Checksum mismatch, corrupted download

## 🔒 Security

- All downloads use HTTPS when available
- SHA256 checksums verify file integrity
- No data is collected or transmitted beyond download requests
- Source code is open for security auditing

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to:

1. **Report Issues**: Use GitHub Issues for bug reports
2. **Suggest Features**: Request new distributions or features
3. **Update Data**: Help keep distribution data current
4. **Code Improvements**: Submit pull requests for enhancements

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
- [ ] Resume interrupted downloads
- [ ] Batch download multiple ISOs
- [ ] Automatic distribution data updates
- [ ] USB creation wizard
- [ ] Dark/Light theme toggle
- [ ] Download scheduling
- [ ] Mirror selection for faster downloads

## 📞 Support

If you encounter issues or need help:

1. Check the [Troubleshooting](#-troubleshooting) section
2. Review `downloader.log` for detailed error information
3. Search existing [GitHub Issues](https://github.com/AshenSage/LinuxDownloaderWithClaude/issues)
4. Create a new issue with detailed information

## 🙏 Acknowledgments

- Built with [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) for modern GUI
- Inspired by the need for a simple, reliable Linux ISO downloader
- Created with assistance from Claude AI
- Thanks to all Linux distribution maintainers for their excellent work

---

**Happy Linux exploring! 🐧**

*Note: This application downloads ISOs from official distribution sources. Always verify checksums and download from trusted mirrors.*