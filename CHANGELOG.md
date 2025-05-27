# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Nothing yet

### Changed
- Nothing yet

### Fixed
- Nothing yet

## [1.1.0] - 2025-05-27

### Added
- **Download Control Features**:
  - Pause/Resume functionality for downloads with visual feedback
  - Cancel download capability with confirmation dialog
  - Resume interrupted downloads from last position using partial file support
  - Improved download state management and error handling

- **Version Checking System**:
  - "Check Latest Versions" button to fetch current distribution versions
  - Integration with official APIs and websites for version information
  - Real-time version display in distribution selection dropdown
  - Support for checking versions of all 8 distributions:
    - Ubuntu (via Launchpad API)
    - Linux Mint (via website scraping)
    - Fedora (via Bodhi API)
    - Debian (stable release info)
    - Kali Linux (rolling release estimation)
    - CentOS Stream (current version)
    - openSUSE (Leap and Tumbleweed)
    - Arch Linux (rolling release dating)

- **Enhanced User Interface**:
  - New control buttons for Pause/Resume and Cancel operations
  - Version information section with status updates
  - Improved layout with better organization of controls
  - Enhanced status messages with emoji indicators
  - Progress tracking during version checking process

### Changed
- **Interface Improvements**:
  - Increased main window size (900x800) to accommodate new features
  - Reorganized layout with dedicated version checking section
  - Enhanced distribution selection with version information display
  - Improved button layout and visual hierarchy
  - Better spacing and organization of UI elements

- **Download Management**:
  - Completely rewritten download engine with pause/cancel support
  - Improved error handling and recovery mechanisms
  - Enhanced progress tracking and status reporting
  - Better thread management for download operations

- **Version Information**:
  - Distribution dropdown now shows current versions when available
  - Context information includes version details
  - Smart version estimation for rolling releases

### Technical Improvements
- **Threading**: Separate threads for version checking and downloads
- **State Management**: Improved download state tracking and control
- **Error Handling**: Better exception handling for network operations
- **Resource Management**: Proper cleanup of file handles and network connections
- **API Integration**: Integration with multiple distribution APIs and websites
- **File Handling**: Support for partial file resume and cleanup

### Fixed
- Download thread safety improvements
- Better handling of network interruptions
- Improved error messages and user feedback
- Enhanced logging for troubleshooting

### Security
- Improved handling of network requests with proper timeouts
- Better validation of download sources and version information
- Safe handling of partial downloads and file operations

## [1.0.0] - 2025-05-27

### Added
- Initial release of Linux Distro Downloader
- Modern GUI built with CustomTkinter
- Support for 8 popular Linux distributions:
  - Ubuntu (Desktop & Server LTS)
  - Linux Mint (Cinnamon, MATE, XFCE)
  - Fedora (Workstation & Server)
  - Debian (Standard DVD & Netinst)
  - Kali Linux (Live & Installer)
  - CentOS Stream (DVD & Boot ISO)
  - openSUSE (Leap & Tumbleweed)
  - Arch Linux
- Real-time download progress tracking with speed and ETA
- Automatic SHA256 checksum verification
- Configurable download directory
- Comprehensive error handling and retry mechanisms
- Detailed logging system
- Distribution data validation
- Cross-platform support (Windows, macOS, Linux)

### Features
- **User Interface**:
  - Clean, modern dark theme interface
  - Intuitive distribution and edition selection
  - Real-time progress bar with detailed statistics
  - Status updates and error messaging
  - Directory browser for download location

- **Download Management**:
  - Robust HTTP download with streaming
  - Progress tracking (percentage, speed, ETA)
  - Automatic retry on network errors
  - Checksum verification with visual feedback

- **Data Management**:
  - JSON-based distribution data storage
  - Data validation and integrity checking
  - Easy addition of new distributions
  - Statistics and reporting

### Technical Details
- **Language**: Python 3.8+
- **GUI Framework**: CustomTkinter
- **HTTP Library**: Requests
- **Checksum**: SHA256
- **Threading**: Background downloads with thread-safe GUI updates
- **Logging**: Configurable logging with file and console output

### Supported Platforms
- Windows 10/11
- macOS 10.15+
- Linux (Ubuntu, Debian, Fedora, etc.)

### Security
- All downloads use HTTPS when available
- SHA256 checksum verification for file integrity
- No data collection or external communication beyond downloads
- Source code available for security auditing

[Unreleased]: https://github.com/AshenSage/LinuxDownloaderWithClaude/compare/v1.1.0...HEAD
[1.1.0]: https://github.com/AshenSage/LinuxDownloaderWithClaude/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/AshenSage/LinuxDownloaderWithClaude/releases/tag/v1.0.0