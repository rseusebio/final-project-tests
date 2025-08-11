#!/usr/bin/env python3
"""
K6 Test Results Metrics Extractor
Extracts key performance metrics from k6 test result JSON files
"""

import json
import sys
import os
import glob
from typing import Dict, Any, List


def extract_cloudwatch_logs_metrics(json_file_path: str) -> List[Dict[str, Any]]:
    """
    Extract latency metrics from CloudWatch logs JSON file, separated by operation
    
    Args:
        json_file_path: Path to the CloudWatch logs JSON file
        
    Returns:
        Dictionary containing extracted latency metrics separated by operation
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
    
    if 'events' not in data:
        print(f"Error: No 'events' found in file '{json_file_path}'")
        return {}
    
    # Extract latency values from log messages, separated by operation
    serialize_latencies = []
    deserialize_latencies = []    
    for event in data['events']:
        message = event.get('message', '')
        if not message:
            continue
            
        # Parse CSV-like message: "id","protocol","operation","endpoint","timestamp","latency"
        try:
            # Remove quotes and split by comma
            parts = [part.strip('"') for part in message.split(',')]
            if len(parts) >= 6:
                request_id, protocol, operation, endpoint, timestamp, latency_str = parts[:6]
                
                # Convert latency to float
                try:
                    latency = float(latency_str)
                    
                    # Store latency based on operation
                    if operation.lower() == 'serialize':
                        serialize_latencies.append(latency)
                    elif operation.lower() == 'deserialize':
                        deserialize_latencies.append(latency)
                except ValueError:
                    print(f"Warning: Invalid latency value: {latency_str}")
                    sys.exit(1)  # Skip invalid latency values
        except Exception:
            print(f"Warning: Malformed message: {message}")
            sys.exit(1)  # Skip malformed messages            
    
    if not serialize_latencies and not deserialize_latencies:
        print(f"Warning: No valid latency data found in '{json_file_path}'")
        sys.exit(1)
    
    metrics = {}
    
    # Calculate statistics for serialize operation
    if serialize_latencies:
        serialize_latencies.sort()
        n_serialize = len(serialize_latencies)
        metrics['serialize'] = {
            'total_requests': n_serialize,
            'latency_min': serialize_latencies[0],
            'latency_max': serialize_latencies[-1],
            'latency_avg': sum(serialize_latencies) / n_serialize,
            'latency_median': serialize_latencies[n_serialize // 2] if n_serialize % 2 == 1 else (serialize_latencies[n_serialize // 2 - 1] + serialize_latencies[n_serialize // 2]) / 2,
            'latency_p90': serialize_latencies[int(0.9 * n_serialize)] if n_serialize > 0 else 0,
            'latency_p95': serialize_latencies[int(0.95 * n_serialize)] if n_serialize > 0 else 0,
            'latency_p99': serialize_latencies[int(0.99 * n_serialize)] if n_serialize > 0 else 0
        }
    
    # Calculate statistics for deserialize operation
    if deserialize_latencies:
        deserialize_latencies.sort()
        n_deserialize = len(deserialize_latencies)
        metrics['deserialize'] = {
            'total_requests': n_deserialize,
            'latency_min': deserialize_latencies[0],
            'latency_max': deserialize_latencies[-1],
            'latency_avg': sum(deserialize_latencies) / n_deserialize,
            'latency_median': deserialize_latencies[n_deserialize // 2] if n_deserialize % 2 == 1 else (deserialize_latencies[n_deserialize // 2 - 1] + deserialize_latencies[n_deserialize // 2]) / 2,
            'latency_p90': deserialize_latencies[int(0.9 * n_deserialize)] if n_deserialize > 0 else 0,
            'latency_p95': deserialize_latencies[int(0.95 * n_deserialize)] if n_deserialize > 0 else 0,
            'latency_p99': deserialize_latencies[int(0.99 * n_deserialize)] if n_deserialize > 0 else 0
        }
        
    return [
        metrics['deserialize'],
        metrics['serialize']
    ]


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
    Calculate average metrics across all files (primitive values only)
    
    Args:
        all_metrics: List containing metrics from all files
        
    Returns:
        Dictionary containing averaged metrics
    """
    if not all_metrics:
        return {}
    
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


def process_cloudwatch_logs(folder_path: str, output_file: str):
    """
    Process all CloudWatch logs files in a folder
    
    Args:
        folder_path: Path to the folder containing CloudWatch logs files
        output_file: Name of the output file for average metrics
    """
    if not os.path.isdir(folder_path):
        print(f"Error: '{folder_path}' is not a valid directory")
        sys.exit(1)
    
    # Find all files matching the pattern run_{number}_{service}_cloudwatch_logs.json
    pattern = os.path.join(folder_path, "run_*_*_cloudwatch_logs.json")
    matching_files = glob.glob(pattern)
    
    if not matching_files:
        print(f"No files found matching pattern 'run_*_*_cloudwatch_logs.json' in {folder_path}")
        return
    
    print(f"Found {len(matching_files)} CloudWatch logs files to process:")
    
    # Process each file
    all_deserialize_metrics = []
    all_serialize_metrics = []
    for file_path in matching_files:
        file_name = os.path.basename(file_path)
        print(f"\nProcessing: {file_name}")
        
        # Extract metrics
        [deserialize_metrics, serialize_metrics] = extract_cloudwatch_logs_metrics(file_path)
        
        if not deserialize_metrics or not serialize_metrics:
            print(f"Failed to extract metrics from {file_name}")
            continue

        all_deserialize_metrics.append(deserialize_metrics)
        all_serialize_metrics.append(serialize_metrics)
    
    # Save combined metrics
    if len(all_deserialize_metrics) <= 0 or len(all_serialize_metrics) <= 0:
        print("No CloudWatch logs metrics extracted")
        return
        
    # Calculate and save average metrics
    average_deserialize_metrics = calculate_average_metrics(all_deserialize_metrics)
    average_serialize_metrics = calculate_average_metrics(all_serialize_metrics)
    
    return [
        average_deserialize_metrics,
        average_serialize_metrics
    ]
def main():
    """Main function to process command line arguments and extract metrics"""
    if len(sys.argv) < 2:
        print("WRONG USAGE: python extract_cloudwatch_logs.py <folder_path>")
        sys.exit(1)
    
    folder_path = sys.argv[1]

    if not os.path.isdir(folder_path):
        print(f"Error: '{folder_path}' is not a valid directory")
        sys.exit(1)

    # Process CloudWatch logs
    result = process_cloudwatch_logs(folder_path, "average_cloudwatch_logs_metrics.json")

    if result and len(result) == 2:
        average_deserialize_metrics, average_serialize_metrics = result
        
        if average_deserialize_metrics and average_serialize_metrics:
            # Combine both metrics into a single structure
            combined_metrics = {
                'deserialize': average_deserialize_metrics,
                'serialize': average_serialize_metrics
            }
            
            average_output = os.path.join(folder_path, "average_cloudwatch_logs_metrics.json")
            save_metrics_to_file(combined_metrics, average_output)
            print(f"Average CloudWatch logs metrics saved to: {average_output}")
            
            # Count processed files for summary
            pattern = os.path.join(folder_path, "run_*_*_cloudwatch_logs.json")
            matching_files = glob.glob(pattern)
            print(f"Processed {len(matching_files)} CloudWatch logs files successfully")
        else:
            print("No CloudWatch logs metrics extracted")
    else:
        print("No CloudWatch logs metrics extracted")


if __name__ == "__main__":
    main()



