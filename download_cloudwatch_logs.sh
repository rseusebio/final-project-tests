# Set your variables
SERVICE_NAME="user"
LOG_GROUP_NAME="/ecs/$SERVICE_NAME"
LOG_STREAM_NAME="/$LOG_GROUP_NAME/a6535c86670849cd904805d1ea5f27a0"
TEST_PROTOCOL="grpc"
TEST_TYPE="average_load"
# START_TIME=$(date -j -f "%Y-%m-%dT%H:%M:%SZ" "2025-07-27T16:17:00Z" +%s000)
# END_TIME=$(date -j -f "%Y-%m-%dT%H:%M:%SZ" "2025-07-27T16:24:59Z" +%s000)
START_TIME=$(date -j -f "%Y-%m-%dT%H:%M:%SZ" "2025-08-07T23:00:52Z" +%s000)
END_TIME=$(date -j -f "%Y-%m-%dT%H:%M:%SZ" "2025-08-07T23:20:25Z" +%s000)

AWS_PROFILE="rse.eusebio"
OUTPUT_FILE="$TEST_PROTOCOL-$SERVICE_NAME-$TEST_TYPE-logs.json"


echo "Downloading logs for $SERVICE_NAME from $START_TIME to $END_TIME"

# Download logs with specified interval
aws logs filter-log-events \
  --log-group-name "$LOG_GROUP_NAME" \
  --start-time "$START_TIME" \
  --end-time "$END_TIME" \
  --profile "$AWS_PROFILE" \
  --output json > "$OUTPUT_FILE"