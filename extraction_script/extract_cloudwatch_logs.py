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
                    continue  # Skip invalid latency values
        except Exception:
            print(f"Warning: Malformed message: {message}")
            continue  # Skip malformed messages            
    
    if not serialize_latencies and not deserialize_latencies:
        print(f"Warning: No valid latency data found in '{json_file_path}'")
        return []
    
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
    Process all CloudWatch logs files in service subdirectories and save per-service results
    
    Args:
        folder_path: Path to the folder containing service subdirectories
        output_file: Name of the output file for average metrics
    """
    if not os.path.isdir(folder_path):
        print(f"Error: '{folder_path}' is not a valid directory")
        sys.exit(1)
    
    # Look for service subdirectories
    services = ['order', 'product', 'user', 'payment']
    all_service_metrics = {}
    
    for service in services:
        service_dir = os.path.join(folder_path, service)
        if not os.path.exists(service_dir):
            continue
            
        print(f"\nProcessing {service} service...")
        
        # Find all CloudWatch logs files for this service
        pattern = os.path.join(service_dir, f"run_*_{service}_cloudwatch_logs.json")
        matching_files = glob.glob(pattern)
        
        if not matching_files:
            print(f"  No CloudWatch logs files found for {service} service")
            continue
            
        print(f"  Found {len(matching_files)} CloudWatch logs files for {service} service:")
        
        # Process each file for this service
        all_deserialize_metrics = []
        all_serialize_metrics = []
        
        for file_path in matching_files:
            file_name = os.path.basename(file_path)
            print(f"    Processing: {file_name}")
            
            # Extract metrics
            try:
                [deserialize_metrics, serialize_metrics] = extract_cloudwatch_logs_metrics(file_path)
                
                if deserialize_metrics and serialize_metrics:
                    all_deserialize_metrics.append(deserialize_metrics)
                    all_serialize_metrics.append(serialize_metrics)
                else:
                    print(f"      Failed to extract metrics from {file_name}")
            except Exception as e:
                print(f"      Error processing {file_name}: {e}")
                continue
        
        # Calculate averages for this service
        if all_deserialize_metrics and all_serialize_metrics:
            average_deserialize_metrics = calculate_average_metrics(all_deserialize_metrics)
            average_serialize_metrics = calculate_average_metrics(all_serialize_metrics)
            
            all_service_metrics[service] = {
                'deserialize': average_deserialize_metrics,
                'serialize': average_serialize_metrics
            }
            
            # Save per-service metrics
            service_output = os.path.join(service_dir, "cloudwatch_logs_metrics.json")
            save_metrics_to_file(all_service_metrics[service], service_output)
            print(f"  📁 {service} service metrics saved to: {service_output}")
        else:
            print(f"  ⚠️  No valid metrics extracted for {service} service")
    
    # Save combined metrics for all services
    if all_service_metrics:
        combined_output = os.path.join(folder_path, "average_cloudwatch_logs_metrics.json")
        save_metrics_to_file(all_service_metrics, combined_output)
        print(f"\n📁 Combined metrics for all services saved to: {combined_output}")
        
        total_files = sum(len(glob.glob(os.path.join(folder_path, service, f"run_*_{service}_cloudwatch_logs.json"))) 
                         for service in services if os.path.exists(os.path.join(folder_path, service)))
        print(f"Total CloudWatch logs files processed: {total_files}")
        
        return all_service_metrics
    else:
        print("No CloudWatch logs metrics extracted from any service")
        return {}
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

    if result:
        print("CloudWatch logs extraction completed successfully")
    else:
        print("No CloudWatch logs metrics extracted")


if __name__ == "__main__":
    main()



