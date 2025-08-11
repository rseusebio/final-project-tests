# Set your variables
AWS_PROFILE="rse.eusebio"
NAMESPACE="ECS/ContainerInsights"

service="order"
start_time=$(date -u -r "1754741285" +"%Y-%m-%dT%H:%M:%SZ")
end_time=$(date -u -r "1754741346" +"%Y-%m-%dT%H:%M:%SZ")
cpu_metrics_file="cpu_metrics.json"
memory_metrics_file="memory_metrics.json"
network_rx_bytes_metrics_file="network_rx_bytes_metrics.json"
network_tx_bytes_metrics_file="network_tx_bytes_metrics.json"

echo "Downloading CPU metrics for $service from $start_time to $end_time"

aws cloudwatch get-metric-statistics \
            --namespace "$NAMESPACE" \
            --metric-name "TaskCpuUtilization" \
            --dimensions Name=ClusterName,Value="$service" \
            --start-time "2025-08-09T11:45:05Z" \
            --end-time "2025-08-09T11:59:06Z" \
            --period 60 \
            --statistics Maximum \
            --profile "$AWS_PROFILE" \
            --output json > "$cpu_metrics_file"

aws cloudwatch get-metric-statistics \
            --namespace "$NAMESPACE" \
            --metric-name "TaskMemoryUtilization" \
            --dimensions Name=ClusterName,Value="$service" \
            --start-time "2025-08-09T11:45:05Z" \
            --end-time "2025-08-09T11:59:06Z" \
            --period 60 \
            --statistics Maximum \
            --profile "$AWS_PROFILE" \
            --output json > "$memory_metrics_file"

aws cloudwatch get-metric-statistics \
            --namespace "$NAMESPACE" \
            --metric-name "NetworkRxBytes" \
            --dimensions Name=ClusterName,Value="$service" \
            --start-time "2025-08-09T11:45:05Z" \
            --end-time "2025-08-09T11:59:06Z" \
            --period 60 \
            --statistics Maximum \
            --profile "$AWS_PROFILE" \
            --output json > "$network_rx_bytes_metrics_file"

aws cloudwatch get-metric-statistics \
            --namespace "$NAMESPACE" \
            --metric-name "NetworkTxBytes" \
            --dimensions Name=ClusterName,Value="$service" \
            --start-time "2025-08-09T11:45:05Z" \
            --end-time "2025-08-09T11:59:06Z" \
            --period 60 \
            --statistics Maximum \
            --profile "$AWS_PROFILE" \
            --output json > "$network_tx_bytes_metrics"
