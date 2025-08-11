#!/usr/bin/env python3
"""
Master Extraction Script
Runs all three extraction scripts on each test directory and saves results to output folder
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path
from typing import List, Dict, Any


def get_test_directories(base_path: str) -> List[str]:
    """Get all test directories from the base path"""
    test_dirs = []
    for item in os.listdir(base_path):
        item_path = os.path.join(base_path, item)
        if os.path.isdir(item_path) and ':' in item:  # Test directories contain ':'
            test_dirs.append(item)
    return sorted(test_dirs)


def create_output_structure(base_path: str, output_base: str):
    """Create output directory structure"""
    test_dirs = get_test_directories(base_path)
    
    for test_dir in test_dirs:
        # Create main test directory
        test_output_dir = os.path.join(output_base, test_dir)
        os.makedirs(test_output_dir, exist_ok=True)
        
        # Create service subdirectories
        services = ['order', 'product', 'user', 'payment']
        for service in services:
            service_dir = os.path.join(test_output_dir, service)
            os.makedirs(service_dir, exist_ok=True)
        
        print(f"Created output structure for: {test_dir}")


def run_k6_extraction(test_dir: str, base_path: str, output_base: str):
    """Run k6 metrics extraction"""
    print(f"\n🔍 Running k6 metrics extraction for: {test_dir}")
    
    input_path = os.path.join(base_path, test_dir)
    output_path = os.path.join(output_base, test_dir)
    
    try:
        # Run the k6 extraction script
        cmd = [
            sys.executable, 
            "extraction_script/extract_k6_metrics.py", 
            input_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=os.getcwd())
        
        if result.returncode == 0:
            print(f"  ✅ k6 extraction completed successfully")
            
            # Copy the output file to our output directory
            k6_output = os.path.join(input_path, "average_k6_metrics.json")
            if os.path.exists(k6_output):
                dest_path = os.path.join(output_path, "k6_metrics.json")
                shutil.copy2(k6_output, dest_path)
                print(f"  📁 k6 metrics saved to: {dest_path}")
            else:
                print(f"  ⚠️  k6 output file not found")
        else:
            print(f"  ❌ k6 extraction failed:")
            print(f"     {result.stderr}")
            
    except Exception as e:
        print(f"  ❌ Error running k6 extraction: {e}")


def run_cloudwatch_logs_extraction(test_dir: str, base_path: str, output_base: str):
    """Run CloudWatch logs extraction"""
    print(f"\n📊 Running CloudWatch logs extraction for: {test_dir}")
    
    input_path = os.path.join(base_path, test_dir)
    output_path = os.path.join(output_base, test_dir)
    
    try:
        # Run the CloudWatch logs extraction script
        cmd = [
            sys.executable, 
            "extraction_script/extract_cloudwatch_logs.py", 
            input_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=os.getcwd())
        
        if result.returncode == 0:
            print(f"  ✅ CloudWatch logs extraction completed successfully")
            
            # Copy the output file to our output directory
            logs_output = os.path.join(input_path, "average_cloudwatch_logs_metrics.json")
            if os.path.exists(logs_output):
                dest_path = os.path.join(output_path, "cloudwatch_logs_metrics.json")
                shutil.copy2(logs_output, dest_path)
                print(f"  📁 CloudWatch logs metrics saved to: {dest_path}")
            else:
                print(f"  ⚠️  CloudWatch logs output file not found")
        else:
            print(f"  ❌ CloudWatch logs extraction failed:")
            print(f"     {result.stderr}")
            
    except Exception as e:
        print(f"  ❌ Error running CloudWatch logs extraction: {e}")


def run_cloudwatch_metrics_extraction(test_dir: str, base_path: str, output_base: str):
    """Run CloudWatch metrics extraction for each service"""
    print(f"\n💻 Running CloudWatch metrics extraction for: {test_dir}")
    
    input_path = os.path.join(base_path, test_dir)
    output_path = os.path.join(output_base, test_dir)
    
    services = ['order', 'product', 'user', 'payment']
    
    for service in services:
        service_input = os.path.join(input_path, service)
        service_output = os.path.join(output_path, service)
        
        if not os.path.exists(service_input):
            print(f"  ⚠️  Service directory not found: {service}")
            continue
            
        print(f"  🔧 Processing {service} service...")
        
        try:
            # Run the CloudWatch metrics extraction script
            cmd = [
                sys.executable, 
                "extraction_script/extract_cloudwatch_metrics.py", 
                service_input
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=os.getcwd())
            
            if result.returncode == 0:
                print(f"    ✅ {service} metrics extraction completed")
                
                # Copy the output file to our output directory
                metrics_output = os.path.join(service_input, "average_cloudwatch_metrics.json")
                if os.path.exists(metrics_output):
                    dest_path = os.path.join(service_output, "cloudwatch_metrics.json")
                    shutil.copy2(metrics_output, dest_path)
                    print(f"    📁 {service} metrics saved to: {dest_path}")
                else:
                    print(f"    ⚠️  {service} output file not found")
            else:
                print(f"    ❌ {service} metrics extraction failed:")
                print(f"       {result.stderr}")
                
        except Exception as e:
            print(f"    ❌ Error running {service} metrics extraction: {e}")


def create_summary_report(output_base: str, test_dirs: List[str]):
    """Create a summary report of all extractions"""
    print(f"\n📋 Creating summary report...")
    
    summary = {
        "extraction_summary": {
            "total_test_directories": len(test_dirs),
            "test_directories": test_dirs,
            "output_location": output_base,
            "extraction_scripts": [
                "extract_k6_metrics.py",
                "extract_cloudwatch_logs.py", 
                "extract_cloudwatch_metrics.py"
            ]
        },
        "results_structure": {
            "description": "Each test directory contains extracted metrics from all three scripts",
            "files_per_test_directory": {
                "k6_metrics.json": "k6 performance test results",
                "cloudwatch_logs_metrics.json": "CloudWatch logs latency metrics",
                "order/cloudwatch_metrics.json": "Order service infrastructure metrics",
                "product/cloudwatch_metrics.json": "Product service infrastructure metrics", 
                "user/cloudwatch_metrics.json": "User service infrastructure metrics",
                "payment/cloudwatch_metrics.json": "Payment service infrastructure metrics"
            }
        }
    }
    
    # Save summary report
    summary_path = os.path.join(output_base, "extraction_summary.json")
    try:
        import json
        with open(summary_path, 'w') as f:
            json.dump(summary, f, indent=2)
        print(f"  📁 Summary report saved to: {summary_path}")
    except Exception as e:
        print(f"  ❌ Error saving summary report: {e}")


def main():
    """Main function to run all extractions"""
    # Configuration
    base_path = "test-results"
    output_base = "extracted_metrics"
    
    print("🚀 Starting comprehensive metrics extraction...")
    print(f"📂 Input directory: {base_path}")
    print(f"📁 Output directory: {output_base}")
    
    # Check if input directory exists
    if not os.path.exists(base_path):
        print(f"❌ Error: Input directory '{base_path}' not found")
        sys.exit(1)
    
    # Get test directories
    test_dirs = get_test_directories(base_path)
    if not test_dirs:
        print(f"❌ No test directories found in '{base_path}'")
        sys.exit(1)
    
    print(f"\n📊 Found {len(test_dirs)} test directories:")
    for test_dir in test_dirs:
        print(f"  - {test_dir}")
    
    # Create output structure
    print(f"\n🏗️  Creating output directory structure...")
    create_output_structure(base_path, output_base)
    
    # Process each test directory
    for test_dir in test_dirs:
        print(f"\n{'='*60}")
        print(f"🔄 Processing: {test_dir}")
        print(f"{'='*60}")
        
        # Run k6 extraction
        run_k6_extraction(test_dir, base_path, output_base)
        
        # Run CloudWatch logs extraction
        run_cloudwatch_logs_extraction(test_dir, base_path, output_base)
        
        # Run CloudWatch metrics extraction for each service
        run_cloudwatch_metrics_extraction(test_dir, base_path, output_base)
    
    # Create summary report
    create_summary_report(output_base, test_dirs)
    
    print(f"\n🎉 All extractions completed!")
    print(f"📁 Results saved to: {output_base}")
    print(f"📋 Summary report: {os.path.join(output_base, 'extraction_summary.json')}")


if __name__ == "__main__":
    main()
