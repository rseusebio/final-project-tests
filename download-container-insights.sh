#!/bin/bash

# CloudWatch Container Insights Metrics Downloader
# Downloads CPU and memory utilization metrics for ECS services

# Configuration
AWS_PROFILE="rse.eusebio"
SERVICES=("user" "order" "payment" "product")
NAMESPACE="ECS/ContainerInsights"  # Container Insights namespace

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# Function to download Container Insights metrics
download_container_insights() {
    local test_name=$1
    local run_number=$2
    local start_timestamp=$3
    local end_timestamp=$4
    local output_dir=$5
    
    # Extract test protocol and type from test name
    local test_protocol=$(echo "$test_name" | cut -d':' -f1)
    local test_type=$(echo "$test_name" | cut -d':' -f2)
    
    print_status "Downloading Container Insights metrics for $test_name (Run $run_number)..."
    print_status "Test Protocol: $test_protocol, Test Type: $test_type"

    echo "Start timestamp: $start_timestamp"
    echo "End timestamp: $end_timestamp"

    # Convert timestamps to ISO format for AWS CLI (cross-platform)
    local start_time=$(date -u -r "$start_timestamp" +"%Y-%m-%dT%H:%M:%SZ")
    local end_time=$(date -u -r "$end_timestamp" +"%Y-%m-%dT%H:%M:%SZ")
    
    for service in "${SERVICES[@]}"; do
        print_status "Downloading metrics for $service service..."
        
        # Create output file for this service
        local output_file="$output_dir/run_${run_number}_${service}_container_insights.json"

        # Download CPU utilization metrics
        local cpu_metrics_file="$output_dir/run_${run_number}_${service}_cpu_metrics.json"
        if aws cloudwatch get-metric-statistics \
            --namespace "$NAMESPACE" \
            --metric-name "TaskCpuUtilization" \
            --dimensions Name=ClusterName,Value="$service" \
            --start-time "$start_time" \
            --end-time "$end_time" \
            --period 60 \
            --statistics Maximum \
            --profile "$AWS_PROFILE" \
            --output json > "$cpu_metrics_file" 2>/dev/null; then
            
            local cpu_data_points=$(jq '.Datapoints | length' "$cpu_metrics_file" 2>/dev/null || echo "0")
            if [ "$cpu_data_points" -gt 0 ]; then
                print_success "Downloaded $cpu_data_points CPU data points for $service"
            else
                print_warning "No CPU metrics found for $service"
            fi
        else
            print_error "Failed to download CPU metrics for $service"
        fi
        
        # Download memory utilization metrics
        local memory_metrics_file="$output_dir/run_${run_number}_${service}_memory_metrics.json"
        if aws cloudwatch get-metric-statistics \
            --namespace "$NAMESPACE" \
            --metric-name "TaskMemoryUtilization" \
            --dimensions Name=ClusterName,Value="$service" \
            --start-time "$start_time" \
            --end-time "$end_time" \
            --period 60 \
            --statistics Maximum \
            --profile "$AWS_PROFILE" \
            --output json > "$memory_metrics_file" 2>/dev/null; then
            
            local memory_data_points=$(jq '.Datapoints | length' "$memory_metrics_file" 2>/dev/null || echo "0")
            if [ "$memory_data_points" -gt 0 ]; then
                print_success "Downloaded $memory_data_points memory data points for $service"
            else
                print_warning "No memory metrics found for $service"
            fi
        else
            print_error "Failed to download memory metrics for $service"
        fi

        # download NetworkRxBytes metrics
        local network_rx_bytes_metrics_file="$output_dir/run_${run_number}_${service}_network_rx_bytes_metrics.json"
        if aws cloudwatch get-metric-statistics \
            --namespace "$NAMESPACE" \
            --metric-name "NetworkRxBytes" \
            --dimensions Name=ClusterName,Value="$service" \
            --start-time "$start_time" \
            --end-time "$end_time" \
            --period 60 \
            --statistics Maximum \
            --profile "$AWS_PROFILE" \
            --output json > "$network_rx_bytes_metrics_file" 2>/dev/null; then
            local network_rx_bytes_data_points=$(jq '.Datapoints | length' "$network_rx_bytes_metrics_file" 2>/dev/null || echo "0")
            if [ "$network_rx_bytes_data_points" -gt 0 ]; then
                print_success "Downloaded $network_rx_bytes_data_points network rx bytes data points for $service"
            else
                print_warning "No network rx bytes metrics found for $service"
            fi
        else
            print_error "Failed to download network rx bytes metrics for $service"
        fi

        # download NetworkTxBytes metrics
        local network_tx_bytes_metrics_file="$output_dir/run_${run_number}_${service}_network_tx_bytes_metrics.json"
        if aws cloudwatch get-metric-statistics \
            --namespace "$NAMESPACE" \
            --metric-name "NetworkTxBytes" \
            --dimensions Name=ClusterName,Value="$service" \
            --start-time "$start_time" \
            --end-time "$end_time" \
            --period 60 \
            --statistics Maximum \
            --profile "$AWS_PROFILE" \
            --output json > "$network_tx_bytes_metrics_file" 2>/dev/null; then
            local network_tx_bytes_data_points=$(jq '.Datapoints | length' "$network_tx_bytes_metrics_file" 2>/dev/null || echo "0")
            if [ "$network_tx_bytes_data_points" -gt 0 ]; then
                print_success "Downloaded $network_tx_bytes_data_points network tx bytes data points for $service"
            else
                print_warning "No network tx bytes metrics found for $service"
            fi
        else
            print_error "Failed to download network tx bytes metrics for $service"
        fi

    done
}

# Main function to download all Container Insights metrics
download_all_container_insights() {
    local test_name=$1
    local run_number=$2
    local start_timestamp=$3
    local end_timestamp=$4
    local output_dir=$5
    
    print_status "=== Downloading Container Insights Metrics ==="
    
    download_container_insights "$test_name" "$run_number" "$start_timestamp" "$end_timestamp" "$output_dir"
    
    print_success "Container Insights metrics download completed"
}

# If script is run directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    # Example usage
    if [ $# -eq 5 ]; then
        download_all_container_insights "$1" "$2" "$3" "$4" "$5"
    else
        echo "Usage: $0 <test_name> <run_number> <start_timestamp> <end_timestamp> <output_dir>"
        echo "Example: $0 'rest:high_load' 1 1704067200 1704153599 './test-results/rest:high_load'"
        exit 1
    fi
fi 