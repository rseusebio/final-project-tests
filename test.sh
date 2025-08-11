#!/bin/bash

test_name="rest:smoke"
run_number=1
RESULTS_DIR="test-results"
output_file="$RESULTS_DIR/$test_name/run_${test_name}_${run_number}.json"

echo "Running $test_name (Run $run_number)..."

npm run "$test_name" -- --env TEST_TYPE=smoke --env FILE_PATH="$output_file"