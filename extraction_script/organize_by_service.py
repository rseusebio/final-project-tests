#!/usr/bin/env python3
"""
Script to organize test result files by service
Creates service-specific folders and moves files accordingly
"""

import os
import shutil
import glob
from pathlib import Path

def create_service_folders(base_path):
    """Create service folders in the given directory"""
    services = ['order', 'product', 'user', 'payment']
    
    for service in services:
        service_path = os.path.join(base_path, service)
        if not os.path.exists(service_path):
            os.makedirs(service_path)
            print(f"Created folder: {service_path}")

def get_service_from_filename(filename):
    """Extract service name from filename"""
    # Handle different file patterns:
    # - run_{number}_{service}_*.json
    # - results_{protocol}:{test_type}_run_{number}.json (these stay in root)
    
    if filename.startswith('run_') and '_cloudwatch_logs.json' in filename:
        # run_{number}_{service}_cloudwatch_logs.json
        parts = filename.split('_')
        if len(parts) >= 3:
            return parts[2]  # service is the third part
    
    elif filename.startswith('run_') and '_cpu_metrics.json' in filename:
        # run_{number}_{service}_cpu_metrics.json
        parts = filename.split('_')
        if len(parts) >= 3:
            return parts[2]
    
    elif filename.startswith('run_') and '_memory_metrics.json' in filename:
        # run_{number}_{service}_memory_metrics.json
        parts = filename.split('_')
        if len(parts) >= 3:
            return parts[2]
    
    elif filename.startswith('run_') and '_network_rx_bytes_metrics.json' in filename:
        # run_{number}_{service}_network_rx_bytes_metrics.json
        parts = filename.split('_')
        if len(parts) >= 3:
            return parts[2]
    
    elif filename.startswith('run_') and '_network_tx_bytes_metrics.json' in filename:
        # run_{number}_{service}_network_tx_bytes_metrics.json
        parts = filename.split('_')
        if len(parts) >= 3:
            return parts[2]
    
    # Files that should stay in root (k6 results, timing, averages)
    return None

def organize_files_by_service(test_dir):
    """Organize files in a test directory by service"""
    print(f"\nProcessing directory: {test_dir}")
    
    # Create service folders
    create_service_folders(test_dir)
    
    # Get all JSON files
    json_files = glob.glob(os.path.join(test_dir, "*.json"))
    
    moved_count = 0
    for file_path in json_files:
        filename = os.path.basename(file_path)
        
        # Determine service
        service = get_service_from_filename(filename)
        
        if service:
            # Move file to appropriate service folder
            service_folder = os.path.join(test_dir, service)
            destination = os.path.join(service_folder, filename)
            
            try:
                shutil.move(file_path, destination)
                print(f"  Moved {filename} -> {service}/")
                moved_count += 1
            except Exception as e:
                print(f"  Error moving {filename}: {e}")
        else:
            # File stays in root (k6 results, timing, averages)
            print(f"  Kept {filename} in root")
    
    print(f"  Total files moved: {moved_count}")

def main():
    """Main function to organize all test result directories"""
    base_path = "test-results"
    
    if not os.path.exists(base_path):
        print(f"Error: {base_path} directory not found")
        return
    
    # Get all test directories
    test_dirs = [d for d in os.listdir(base_path) 
                 if os.path.isdir(os.path.join(base_path, d))]
    
    print(f"Found {len(test_dirs)} test directories to organize:")
    for test_dir in test_dirs:
        print(f"  - {test_dir}")
    
    # Process each test directory
    for test_dir in test_dirs:
        test_path = os.path.join(base_path, test_dir)
        organize_files_by_service(test_path)
    
    print("\nOrganization complete!")

if __name__ == "__main__":
    main()
