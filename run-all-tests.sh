#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
RUNS_PER_TEST=5
RESULTS_DIR="test-results"

# Test scripts to run (excluding smoke tests)
TESTS=(
    "rest:average_load"
    "grpc:average_load"
    "rest:high_load"
    "grpc:high_load"    
    "rest:spike"
    "grpc:spike"
    "rest:breakpoint"
    "grpc:breakpoint"
)

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

# Function to create directories
setup_directories() {
    local test_name=$1
    print_status "Setting up directories..."
    
    # Create main results directory
    mkdir -p "$RESULTS_DIR/$1"
    
    print_success "Directories created successfully"
}

# Function to download CloudWatch logs
download_cloudwatch_logs() {
    local test_name=$1
    local run_number=$2
    local start_timestamp=$3
    local end_timestamp=$4
    
    AWS_PROFILE="rse.eusebio"
    SERVICES=("user" "order" "payment" "product")
    
    # Extract test protocol and type from test name
    local test_protocol=$(echo "$test_name" | cut -d':' -f1)
    local test_type=$(echo "$test_name" | cut -d':' -f2)
    
    print_status "Downloading CloudWatch logs for $test_name (Run $run_number)..."
    print_status "Test Protocol: $test_protocol, Test Type: $test_type"
    
    for service in "${SERVICES[@]}"; do
        local log_group_name="/ecs/$service"
        local output_file="$RESULTS_DIR/$test_name/run_${run_number}_${service}_cloudwatch_logs.json"
        
        # Convert timestamps to milliseconds for AWS CLI
        local start_time_ms=$((start_timestamp * 1000))
        local end_time_ms=$((end_timestamp * 1000))
        
        print_status "Downloading logs for $service service ($log_group_name)..."
        
        # Build AWS CLI command
        local aws_cmd="aws logs filter-log-events"
        aws_cmd="$aws_cmd --log-group-name \"$log_group_name\""
        aws_cmd="$aws_cmd --start-time $start_time_ms"
        aws_cmd="$aws_cmd --end-time $end_time_ms"
        aws_cmd="$aws_cmd --profile \"$AWS_PROFILE\""
        aws_cmd="$aws_cmd --output json"
        
        # Download logs for this service
        if eval "$aws_cmd" > "$output_file" 2>/dev/null; then
            
            # Check if logs were found
            local log_count=$(jq '.events | length' "$output_file" 2>/dev/null || echo "0")
            if [ "$log_count" -gt 0 ]; then
                print_success "Downloaded $log_count logs for $service service"
            else
                print_warning "No logs found for $service service in the specified time range"
            fi
        else
            print_error "Failed to download logs for $service service"
        fi
    done
}

# Function to download Container Insights metrics
download_container_insights_metrics() {
    local test_name=$1
    local run_number=$2
    local start_timestamp=$3
    local end_timestamp=$4
    
    print_status "Downloading Container Insights metrics for $test_name (Run $run_number)..."
    
    # Source the Container Insights script if it exists
    if [ -f "download-container-insights.sh" ]; then
        source "download-container-insights.sh"
        download_all_container_insights "$test_name" "$run_number" "$start_timestamp" "$end_timestamp" "$RESULTS_DIR/$test_name"
    else
        print_warning "download-container-insights.sh not found, skipping Container Insights metrics"
    fi
}

# Function to run a single test
run_test() {
    local test_name=$1
    local run_number=$2
    local output_file="$RESULTS_DIR/$test_name/results_${test_name}_run_${run_number}.json"
    
    print_status "Running $test_name (Run $run_number/$RUNS_PER_TEST)..."
    
    # Record start time
    local start_time=$(date +"%Y-%m-%d %H:%M:%S")
    local start_timestamp=$(date +%s)
    
    # Run the test and capture output
    echo "Running $test_name (Run $run_number/$RUNS_PER_TEST)..."
    echo "Output file: $output_file"
    
    npm run "$test_name" -- --env FILE_PATH="$output_file"

        echo "Test $test_name (Run $run_number/$RUNS_PER_TEST) completed successfully"
        local end_time=$(date +"%Y-%m-%d %H:%M:%S")
        local end_timestamp=$(date +%s)
        local duration=$((end_timestamp - start_timestamp))

        echo "local variables: $test_name, $run_number, $start_time, $end_time, $start_timestamp, $end_timestamp, $duration"
        
        # Save timing information
        cat > "$RESULTS_DIR/$test_name/results_${test_name}_run_${run_number}_timing.json" << EOF
{
    "test_name": "$test_name",
    "run_number": $run_number,
    "start_time": "$start_time",
    "end_time": "$end_time",
    "start_timestamp": $start_timestamp,
    "end_timestamp": $end_timestamp,
    "duration_seconds": $duration
}
EOF

        echo "Sleeping for 30 seconds..."
        # sleep for 60 seconds 
        sleep 30
        echo "Done sleeping"

        # Download CloudWatch logs for this test run
        download_cloudwatch_logs "$test_name" "$run_number" "$start_timestamp" "$end_timestamp"
        
        # Download Container Insights metrics for this test run
        download_container_insights_metrics "$test_name" "$run_number" "$start_timestamp" "$end_timestamp"
        
        print_success "$test_name Run $run_number completed in ${duration}s"
        return 0
}

# Function to run all tests
run_all_tests() {
    local total_tests=$((${#TESTS[@]} * RUNS_PER_TEST))
    local current_test=0
    local failed_tests=()
    
    print_status "Starting test execution..."
    print_status "Total tests to run: $total_tests"
    print_status "Results will be saved to: $RESULTS_DIR"
    
    for test in "${TESTS[@]}"; do
        print_status "Starting test suite: $test"
        
        for run in $(seq 1 $RUNS_PER_TEST); do
            current_test=$((current_test + 1))
            print_status "Progress: $current_test/$total_tests"
            
            if ! run_test "$test" "$run"; then
                failed_tests+=("$test (Run $run)")
            fi
        done
        
        print_success "Completed test suite: $test"
        echo
    done

    if [ ${#failed_tests[@]} -eq 0 ]; then
        print_success "All tests completed successfully!"
    else
        print_warning "Some tests failed:"
        for failed in "${failed_tests[@]}"; do
            print_error "  - $failed"
        done
    fi
}

# Main execution
main() {
    print_status "=== k6 Load Testing Suite ==="
    print_status "Starting comprehensive test execution..."
    
    # Check if npm is available
    if ! command -v npm &> /dev/null; then
        print_error "npm is not installed or not in PATH"
        exit 1
    fi
    
    # Check if we're in the right directory
    if [ ! -f "package.json" ]; then
        print_error "package.json not found. Please run this script from the project root."
        exit 1
    fi
    
    # Setup directories
    for test in "${TESTS[@]}"; do
        setup_directories "$test"
    done
    
    # Run all tests
    run_all_tests
    
    print_status "=== EXECUTION COMPLETE ==="
    print_status "Check $RESULTS_DIR for all results and reports"
}

# Run the main function
main "$@" 