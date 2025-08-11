#!/usr/bin/env python3
"""
K6 Test Results Metrics Extractor
Extracts key performance metrics from k6 test result JSON files
"""

import json
import sys
import os
import glob
from pathlib import Path
from typing import Dict, Any, List, Optional

def extract_k6_metrics(json_file_path: str) -> Dict[str, Any]:
    """
    Extract key metrics from k6 test results JSON file (supports both REST and gRPC)
    
    Args:
        json_file_path: Path to the k6 results JSON file
        
    Returns:
        Dictionary containing extracted metrics (flattened structure)
    """
    try:
        with open(json_file_path, 'r') as file:
            data = json.load(file)
    except FileNotFoundError:
        print(f"Error: File '{json_file_path}' not found")
        return {}
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in file '{json_file_path}'")
        return {}
    
    metrics = {}
    
    # Detect protocol type (REST vs gRPC)
    is_grpc = 'grpc_req_duration' in data.get('metrics', {})
    is_rest = 'http_req_duration' in data.get('metrics', {})
    
    # Extract data_sent and data_received
    if 'data_sent' in data.get('metrics', {}):
        data_sent = data['metrics']['data_sent']
        metrics['data_sent_count'] = data_sent.get('values', {}).get('count', 0)
        metrics['data_sent_rate'] = data_sent.get('values', {}).get('rate', 0)
    
    if 'data_received' in data.get('metrics', {}):
        data_received = data['metrics']['data_received']
        metrics['data_received_count'] = data_received.get('values', {}).get('count', 0)
        metrics['data_received_rate'] = data_received.get('values', {}).get('rate', 0)
    
    # Extract request duration metrics (REST or gRPC)
    if is_rest and 'http_req_duration' in data.get('metrics', {}):
        req_duration = data['metrics']['http_req_duration']
        metrics['request_duration_avg'] = req_duration.get('values', {}).get('avg', 0)
        metrics['request_duration_min'] = req_duration.get('values', {}).get('min', 0)
        metrics['request_duration_max'] = req_duration.get('values', {}).get('max', 0)
        metrics['request_duration_median'] = req_duration.get('values', {}).get('med', 0)
        metrics['request_duration_p90'] = req_duration.get('values', {}).get('p(90)', 0)
        metrics['request_duration_p95'] = req_duration.get('values', {}).get('p(95)', 0)
        metrics['request_duration_p99'] = req_duration.get('values', {}).get('p(99)', 0)
    elif is_grpc and 'grpc_req_duration' in data.get('metrics', {}):
        req_duration = data['metrics']['grpc_req_duration']
        metrics['request_duration_avg'] = req_duration.get('values', {}).get('avg', 0)
        metrics['request_duration_min'] = req_duration.get('values', {}).get('min', 0)
        metrics['request_duration_max'] = req_duration.get('values', {}).get('max', 0)
        metrics['request_duration_median'] = req_duration.get('values', {}).get('med', 0)
        metrics['request_duration_p90'] = req_duration.get('values', {}).get('p(90)', 0)
        metrics['request_duration_p95'] = req_duration.get('values', {}).get('p(95)', 0)
        metrics['request_duration_p99'] = req_duration.get('values', {}).get('p(99)', 0)
    
    # Extract VUs (Virtual Users) max
    if 'vus_max' in data.get('metrics', {}):
        vus_max = data['metrics']['vus_max']
        metrics['vus_max'] = vus_max.get('values', {}).get('value', 0)
    
    # Extract throughput (requests per second) - REST or gRPC
    if is_rest and 'http_reqs' in data.get('metrics', {}):
        http_reqs = data['metrics']['http_reqs']
        metrics['throughput_requests_per_second'] = http_reqs.get('values', {}).get('rate', 0)
        metrics['throughput_total_requests'] = http_reqs.get('values', {}).get('count', 0)
    elif is_grpc and 'iterations' in data.get('metrics', {}):
        # For gRPC, use iterations as throughput equivalent
        iterations = data['metrics']['iterations']
        metrics['throughput_requests_per_second'] = iterations.get('values', {}).get('rate', 0)
        metrics['throughput_total_requests'] = iterations.get('values', {}).get('count', 0)
    
    # Extract success rate from checks
    if 'checks' in data.get('metrics', {}):
        checks = data['metrics']['checks']
        metrics['success_rate_rate'] = checks.get('values', {}).get('rate', 0)
        metrics['success_rate_passes'] = checks.get('values', {}).get('passes', 0)
        metrics['success_rate_fails'] = checks.get('values', {}).get('fails', 0)
    
    return metrics

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

def calculate_average_metrics(all_metrics: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calculate average metrics across all files
    
    Args:
        all_metrics: List containing metrics from all files
        
    Returns:
        Dictionary containing averaged metrics
    """
    if not all_metrics:
        print("No metrics to average")
        raise Exception("No metrics to average")
    
    # Initialize counters and sums
    counters = {}
    sums = {}
    
    # Process each file's metrics
    for metrics in all_metrics:
        for metric_key, metric_value in metrics.items():
            if metric_key not in counters:
                counters[metric_key] = 0
                sums[metric_key] = 0
            
            counters[metric_key] += 1
            sums[metric_key] += metric_value
    
    # Calculate averages
    average_metrics = {}
    for metric_key in counters:
        if counters[metric_key] > 0:
            average_metrics[metric_key] = sums[metric_key] / counters[metric_key]
    
    return average_metrics

def process_k6_metrics(folder_path: str, output_file: str):
    """
    Process all k6 result files in a folder that match the pattern results_*_run_*.json
    
    Args:
        folder_path: Path to the folder containing k6 result files
        output_file: Name of the output file for average metrics
    """
    if not os.path.isdir(folder_path):
        print(f"Error: '{folder_path}' is not a valid directory")
        sys.exit(1)
    
    if not output_file:
        print("Error: Output file is required")
        sys.exit(1)
    
    # Find all files matching the pattern
    pattern = os.path.join(folder_path, "results_*_run_*.json")
    matching_files = glob.glob(pattern)
    
    if not matching_files:
        print(f"No files found matching pattern 'results_*_run_*.json' in {folder_path}")
        return {}
    
    print(f"Found {len(matching_files)} k6 result files to process:")
    
    # Process each file
    all_metrics = []
    for file_path in matching_files:
        file_name = os.path.basename(file_path)
        print(f"\nProcessing k6 file: {file_name}")
        
        # Extract metrics
        metrics = extract_k6_metrics(file_path)
        
        if not metrics:
            print(f"Failed to extract metrics from {file_name}")
            continue

        all_metrics.append(metrics)
    
    # Save combined metrics
    if len(all_metrics) <= 0:
        print("No k6 metrics extracted")
        return {}
        
    # Calculate and save average metrics
    average_metrics = calculate_average_metrics(all_metrics)

    return average_metrics

def run_k6_metrics_extraction(folder_path: str):
    """Main function to process command line arguments and extract metrics"""
    if len(sys.argv) < 2:
        print("WRONG USAGE: python extract_k6_metrics.py <folder_path>")
        sys.exit(1)
    
    folder_path = sys.argv[1]

    if not os.path.isdir(folder_path):
        print(f"Error: '{folder_path}' is not a valid directory")
        sys.exit(1)

    # Folder processing
    average_metrics = process_k6_metrics(folder_path, "average_k6_metrics.json")

    if average_metrics:
        average_output = os.path.join(folder_path, "average_k6_metrics.json")
        save_metrics_to_file(average_metrics, average_output)
        print(f"Average k6 metrics saved to: {average_output}")
        
        # Count processed files for summary
        pattern = os.path.join(folder_path, "results_*_run_*.json")
        matching_files = glob.glob(pattern)
        print(f"Processed {len(matching_files)} k6 files successfully")
    else:
        print("No k6 metrics extracted")

if __name__ == "__main__":
    run_k6_metrics_extraction(sys.argv[1])