#!/usr/bin/env python3
"""
CloudWatch Metrics Extractor
Extracts and averages CPU, memory, and network metrics from CloudWatch JSON files
"""

import json
import sys
import os
import glob
from typing import Dict, Any, List


def extract_cpu_metrics(json_file_path: str) -> float:
    """
    Extract maximum CPU utilization from CloudWatch CPU metrics file
    
    Args:
        json_file_path: Path to the CPU metrics JSON file
        
    Returns:
        Average maximum CPU utilization
    """
    try:
        with open(json_file_path, 'r') as file:
            data = json.load(file)
    except FileNotFoundError:
        print(f"Error: File '{json_file_path}' not found")
        return 0.0
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in file '{json_file_path}'")
        return 0.0
    
    if 'Datapoints' not in data:
        print(f"Error: No 'Datapoints' found in file '{json_file_path}'")
        return 0.0
    
    # Extract maximum CPU utilization values
    max_values = []
    for datapoint in data['Datapoints']:
        if 'Maximum' in datapoint:
            max_values.append(datapoint['Maximum'])
    
    if not max_values:
        print(f"Warning: No maximum values found in '{json_file_path}'")
        return 0.0
    
    # Calculate average
    return sum(max_values) / len(max_values)


def extract_memory_metrics(json_file_path: str) -> float:
    """
    Extract maximum memory utilization from CloudWatch memory metrics file
    
    Args:
        json_file_path: Path to the memory metrics JSON file
        
    Returns:
        Average maximum memory utilization
    """
    try:
        with open(json_file_path, 'r') as file:
            data = json.load(file)
    except FileNotFoundError:
        print(f"Error: File '{json_file_path}' not found")
        return 0.0
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in file '{json_file_path}'")
        return 0.0
    
    if 'Datapoints' not in data:
        print(f"Error: No 'Datapoints' found in file '{json_file_path}'")
        return 0.0
    
    # Extract maximum memory utilization values
    max_values = []
    for datapoint in data['Datapoints']:
        if 'Maximum' in datapoint:
            max_values.append(datapoint['Maximum'])
    
    if not max_values:
        print(f"Warning: No maximum values found in '{json_file_path}'")
        return 0.0
    
    # Calculate average
    return sum(max_values) / len(max_values)


def extract_network_rx_metrics(json_file_path: str) -> float:
    """
    Extract maximum network RX bytes from CloudWatch network metrics file
    
    Args:
        json_file_path: Path to the network RX metrics JSON file
        
    Returns:
        Average maximum network RX bytes
    """
    try:
        with open(json_file_path, 'r') as file:
            data = json.load(file)
    except FileNotFoundError:
        print(f"Error: File '{json_file_path}' not found")
        return 0.0
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in file '{json_file_path}'")
        return 0.0
    
    if 'Datapoints' not in data:
        print(f"Error: No 'Datapoints' found in file '{json_file_path}'")
        return 0.0
    
    # Extract maximum network RX bytes values
    max_values = []
    for datapoint in data['Datapoints']:
        if 'Maximum' in datapoint:
            max_values.append(datapoint['Maximum'])
    
    if not max_values:
        print(f"Warning: No maximum values found in '{json_file_path}'")
        return 0.0
    
    # Calculate average
    return sum(max_values) / len(max_values)


def extract_network_tx_metrics(json_file_path: str) -> float:
    """
    Extract maximum network TX bytes from CloudWatch network metrics file
    
    Args:
        json_file_path: Path to the network TX metrics JSON file
        
    Returns:
        Average maximum network TX bytes
    """
    try:
        with open(json_file_path, 'r') as file:
            data = json.load(file)
    except FileNotFoundError:
        print(f"Error: File '{json_file_path}' not found")
        return 0.0
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in file '{json_file_path}'")
        return 0.0
    
    if 'Datapoints' not in data:
        print(f"Error: No 'Datapoints' found in file '{json_file_path}'")
        return 0.0
    
    # Extract maximum network TX bytes values
    max_values = []
    for datapoint in data['Datapoints']:
        if 'Maximum' in datapoint:
            max_values.append(datapoint['Maximum'])
    
    if not max_values:
        print(f"Warning: No maximum values found in '{json_file_path}'")
        return 0.0
    
    # Calculate average
    return sum(max_values) / len(max_values)


def save_metrics_to_file(metrics: Dict[str, Any], output_file: str):
    """
    Save extracted metrics to a JSON file
    
    Args:
        metrics: Dictionary of extracted metrics
        output_file: Output file path
    """
    try:
        with open(output_file, 'w') as file:
            json.dump(metrics, file, indent=2)
        print(f"Metrics saved to: {output_file}")
    except Exception as e:
        print(f"Error saving metrics: {e}")


def process_cloudwatch_metrics(folder_path: str, output_file: str):
    """
    Process all CloudWatch metrics files in a folder
    
    Args:
        folder_path: Path to the folder containing CloudWatch metrics files
        output_file: Name of the output file for combined metrics
    """
    if not os.path.isdir(folder_path):
        print(f"Error: '{folder_path}' is not a valid directory")
        sys.exit(1)
    
    print(f"Processing CloudWatch metrics in: {folder_path}")
    
    # Find all metrics files
    cpu_files = glob.glob(os.path.join(folder_path, "*_cpu_metrics.json"))
    memory_files = glob.glob(os.path.join(folder_path, "*_memory_metrics.json"))
    network_rx_files = glob.glob(os.path.join(folder_path, "*_network_rx_bytes_metrics.json"))
    network_tx_files = glob.glob(os.path.join(folder_path, "*_network_tx_bytes_metrics.json"))
    
    print(f"Found {len(cpu_files)} CPU metrics files")
    print(f"Found {len(memory_files)} memory metrics files")
    print(f"Found {len(network_rx_files)} network RX metrics files")
    print(f"Found {len(network_tx_files)} network TX metrics files")
    
    # Process CPU metrics
    cpu_values = []
    for file_path in cpu_files:
        file_name = os.path.basename(file_path)
        print(f"  Processing CPU: {file_name}")
        value = extract_cpu_metrics(file_path)
        if value > 0:
            cpu_values.append(value)
    
    # Process memory metrics
    memory_values = []
    for file_path in memory_files:
        file_name = os.path.basename(file_path)
        print(f"  Processing memory: {file_name}")
        value = extract_memory_metrics(file_path)
        if value > 0:
            memory_values.append(value)
    
    # Process network RX metrics
    network_rx_values = []
    for file_path in network_rx_files:
        file_name = os.path.basename(file_path)
        print(f"  Processing network RX: {file_name}")
        value = extract_network_rx_metrics(file_path)
        if value > 0:
            network_rx_values.append(value)
    
    # Process network TX metrics
    network_tx_values = []
    for file_path in network_tx_files:
        file_name = os.path.basename(file_path)
        print(f"  Processing network TX: {file_name}")
        value = extract_network_tx_metrics(file_path)
        if value > 0:
            network_tx_values.append(value)
    
    # Calculate averages
    metrics = {}
    
    if cpu_values:
        metrics['cpu_utilization'] = {
            'average_maximum': sum(cpu_values) / len(cpu_values),
            'total_files_processed': len(cpu_values),
            'unit': 'Percent'
        }
    
    if memory_values:
        metrics['memory_utilization'] = {
            'average_maximum': sum(memory_values) / len(memory_values),
            'total_files_processed': len(memory_values),
            'unit': 'Percent'
        }
    
    if network_rx_values:
        metrics['network_rx_bytes'] = {
            'average_maximum': sum(network_rx_values) / len(network_rx_values),
            'total_files_processed': len(network_rx_values),
            'unit': 'Bytes'
        }
    
    if network_tx_values:
        metrics['network_tx_bytes'] = {
            'average_maximum': sum(network_tx_values) / len(network_tx_values),
            'total_files_processed': len(network_tx_values),
            'unit': 'Bytes'
        }
    
    # Save metrics
    if metrics:
        output_path = os.path.join(folder_path, output_file)
        save_metrics_to_file(metrics, output_path)
        print(f"\nProcessed metrics successfully:")
        print(f"  CPU files: {len(cpu_values)}")
        print(f"  Memory files: {len(memory_values)}")
        print(f"  Network RX files: {len(network_rx_values)}")
        print(f"  Network TX files: {len(network_tx_values)}")
    else:
        print("No metrics extracted")


def main():
    """Main function to process command line arguments and extract metrics"""
    if len(sys.argv) < 2:
        print("Usage: python extract_cloudwatch_metrics.py <folder_path>")
        sys.exit(1)
    
    folder_path = sys.argv[1]

    if not os.path.isdir(folder_path):
        print(f"Error: '{folder_path}' is not a valid directory")
        sys.exit(1)

    # Process CloudWatch metrics
    process_cloudwatch_metrics(folder_path, "average_cloudwatch_metrics.json")


if __name__ == "__main__":
    main()
