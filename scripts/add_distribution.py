#!/usr/bin/env python3
"""
Add Distribution Script for Linux Distro Downloader

Interactive script to add new Linux distributions to the data file.

Usage:
    python scripts/add_distribution.py
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any

# Add parent directory to path to import utils
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.data_manager import DistroDataManager

def get_user_input(prompt: str, required: bool = True) -> str:
    """Get user input with validation"""
    while True:
        value = input(prompt).strip()
        if value or not required:
            return value
        print("This field is required. Please try again.")

def get_yes_no(prompt: str, default: bool = True) -> bool:
    """Get yes/no input from user"""
    default_str = "Y/n" if default else "y/N"
    while True:
        response = input(f"{prompt} ({default_str}): ").strip().lower()
        if not response:
            return default
        if response in ['y', 'yes']:
            return True
        elif response in ['n', 'no']:
            return False
        print("Please enter 'y' or 'n'")

def validate_url(url: str) -> bool:
    """Validate URL format"""
    return url.startswith(('http://', 'https://'))

def validate_checksum(checksum: str) -> bool:
    """Validate checksum format (SHA256)"""
    return len(checksum) == 64 and all(c in '0123456789abcdefABCDEF' for c in checksum)

def add_edition() -> Dict[str, str]:
    """Add a single edition interactively"""
    print("\n--- Adding Edition ---")
    
    filename = get_user_input("Enter ISO filename (e.g., ubuntu-22.04-desktop-amd64.iso): ")
    
    url = ""
    while not validate_url(url):
        url = get_user_input("Enter download URL (must start with http:// or https://): ")
        if not validate_url(url):
            print("Invalid URL format. Please try again.")
    
    checksum = ""
    while not validate_checksum(checksum):
        checksum = get_user_input("Enter SHA256 checksum (64 hex characters): ")
        if not validate_checksum(checksum):
            print("Invalid checksum format. Must be 64 hexadecimal characters.")
    
    return {
        'filename': filename,
        'url': url,
        'checksum': checksum.lower()
    }

def main():
    """Main interactive function"""
    print("=" * 60)
    print("    Linux Distro Downloader - Add Distribution")
    print("=" * 60)
    
    # Load existing data
    data_manager = DistroDataManager()
    
    print(f"\nCurrent distributions: {', '.join(data_manager.get_distributions())}")
    print(f"Total: {len(data_manager.get_distributions())} distributions")
    
    # Get distribution details
    print("\n--- Distribution Information ---")
    
    distro_name = get_user_input("Enter distribution name (e.g., 'Elementary OS'): ")
    description = get_user_input("Enter distribution description: ")
    
    # Add editions
    editions = {}
    
    while True:
        edition_name = get_user_input("\nEnter edition name (e.g., 'Desktop', 'Server'): ")
        
        if edition_name in editions:
            print(f"Edition '{edition_name}' already added!")
            continue
        
        editions[edition_name] = add_edition()
        
        print(f"\n✓ Added edition: {edition_name}")
        
        if not get_yes_no("\nAdd another edition?", False):
            break
    
    # Confirm before saving
    print("\n" + "=" * 40)
    print("Summary:")
    print(f"Distribution: {distro_name}")
    print(f"Description: {description}")
    print(f"Editions: {', '.join(editions.keys())}")
    print("=" * 40)
    
    if get_yes_no("\nSave this distribution?", True):
        # Add to data manager
        data_manager.data[distro_name] = {
            'description': description,
            'editions': editions
        }
        
        if data_manager.save_data():
            print(f"\n✓ Successfully added distribution '{distro_name}'")
            print(f"Total distributions: {len(data_manager.get_distributions())}")
        else:
            print(f"\n✗ Failed to save distribution '{distro_name}'")
    else:
        print("\nOperation cancelled.")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)