# k6 Load Testing Scripts

This project contains k6 load testing scripts designed to test different scenarios for your application using both HTTP and gRPC protocols.

## Available Test Scenarios

### HTTP Tests (script.ts)
- **Smoke Test**: Minimal load to verify the system works (1 minute, 1 user)
- **Average Load Test**: Normal expected load (9 minutes, ramps to 50 users)
- **High Load Test**: Stress the system under high load (9 minutes, ramps to 200 users)
- **Spike Test**: Test system behavior under sudden traffic spikes (3 minutes, spikes to 500 users)
- **Breakpoint Test**: Gradually increase load until system breaks (18 minutes, increases to 1000 users)

### gRPC Tests (grpc-script.ts)
- **Smoke Test**: Minimal load to verify the gRPC system works (1 minute, 1 user)
- **Average Load Test**: Normal expected load for gRPC (9 minutes, ramps to 50 users)
- **High Load Test**: Stress the gRPC system under high load (9 minutes, ramps to 200 users)
- **Spike Test**: Test gRPC system behavior under sudden traffic spikes (3 minutes, spikes to 500 users)
- **Breakpoint Test**: Gradually increase gRPC load until system breaks (18 minutes, increases to 1000 users)

## Running Individual Tests

### HTTP Tests
```bash
# Run HTTP smoke test (recommended to start with)
npm run test:smoke

# Run HTTP average load test
npm run test:average_load

# Run HTTP high load test
npm run test:high_load

# Run HTTP spike test
npm run test:spike

# Run HTTP breakpoint test
npm run test:breakpoint
```

### gRPC Tests
```bash
# Run gRPC smoke test
npm run grpc:smoke

# Run gRPC average load test
npm run grpc:average_load

# Run gRPC high load test
npm run grpc:high_load

# Run gRPC spike test
npm run grpc:spike

# Run gRPC breakpoint test
npm run grpc:breakpoint
```

## Running All Tests

```bash
# Run all HTTP tests sequentially
npm run test:all

# Run all gRPC tests sequentially
npm run grpc:all

# Run both HTTP and gRPC test suites
npm run test:both
```

## Test Configuration

Each test scenario is configured with:
- **Performance thresholds**: 95% of requests should complete in under 2 seconds
- **Error rate threshold**: Error rate should be less than 10%
- **Dynamic payload generation**: Each request generates random customer data, products, and payment information

## Target Endpoints

### HTTP Endpoint
```
http://54.198.53.242:8080/order
```

### gRPC Endpoint
```
54.198.53.242:9090
```

To change the target endpoints, modify the `url` variable in `script.ts` and the connection address in `grpc-script.ts`.

## Protocol Comparison

| Aspect | HTTP | gRPC |
|--------|------|------|
| Protocol | HTTP/1.1 | HTTP/2 |
| Serialization | JSON | Protocol Buffers |
| Performance | Good | Better (binary, multiplexing) |
| Browser Support | Native | Limited (requires gRPC-Web) |
| Streaming | Limited | Full support |
| Code Generation | Manual | Automatic from .proto |

## Prerequisites

Make sure you have k6 installed on your system:

```bash
# macOS
brew install k6

# Windows
choco install k6

# Linux
sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys C5AD17C747E3415A3642D57D77C6C491D6AC1D69
echo "deb https://dl.k6.io/deb stable main" | sudo tee /etc/apt/sources.list.d/k6.list
sudo apt-get update
sudo apt-get install k6
```

## Understanding Results

k6 will output detailed metrics including:

### HTTP Metrics
- `http_req_duration`: Request duration percentiles
- `http_req_rate`: Request rate
- `http_req_failed`: Error rate
- `http_reqs`: Total requests

### gRPC Metrics
- `grpc_req_duration`: Request duration percentiles
- `grpc_req_rate`: Request rate
- `grpc_req_failed`: Error rate
- `grpc_reqs`: Total requests

### Common Metrics
- `vus`: Virtual user count
- `data_received`: Data transfer rates
- `data_sent`: Data sent rates

Look for any failed checks or threshold violations to identify performance issues.

## File Structure

```
final-project-tests/
├── script.ts          # HTTP load test script
├── grpc-script.ts     # gRPC load test script
├── order.proto        # Protocol buffer definition
├── package.json       # NPM scripts and dependencies
└── README.md          # This documentation
```

## Troubleshooting

### gRPC Connection Issues
- Ensure the gRPC server is running on the specified port (9090)
- Check if the server supports insecure connections (plaintext)
- Verify the .proto file matches the server's service definition

### HTTP Connection Issues
- Ensure the HTTP server is running on the specified port (8080)
- Check if the endpoint accepts POST requests with JSON payloads
- Verify the response format matches the expected structure

## Test Scenarios

### 1. Smoke Test
- **Purpose**: Verify the system works under minimal load
- **Configuration**: 1 virtual user for 1 minute
- **Use Case**: Quick validation that the API is responding correctly

### 2. Average Load Test
- **Purpose**: Test normal expected load
- **Configuration**: Ramps from 10 to 50 users over 2 minutes, maintains 50 users for 5 minutes, then ramps down
- **Use Case**: Simulate typical production load

### 3. High Load Test
- **Purpose**: Stress test the system
- **Configuration**: Ramps from 50 to 200 users over 2 minutes, maintains 200 users for 5 minutes, then ramps down
- **Use Case**: Test system performance under high stress

### 4. Spike Test
- **Purpose**: Test system behavior during sudden traffic spikes
- **Configuration**: Baseline of 10 users, spikes to 500 users for 1 minute, then returns to baseline
- **Use Case**: Simulate traffic spikes (e.g., flash sales, viral content)

### 5. Breakpoint Test
- **Purpose**: Find the system's breaking point by gradually increasing load
- **Configuration**: Gradually increases from 1 to 1000 users in 2-minute stages (10, 25, 50, 100, 200, 400, 600, 800, 1000)
- **Use Case**: Determine maximum capacity and identify performance degradation patterns
- **What to Watch**: 
  - Response time degradation
  - Error rate increases
  - System resource exhaustion
  - Point where performance thresholds are exceeded

## Performance Thresholds

The script includes performance thresholds:
- 95% of requests should complete within 2 seconds
- Error rate should be less than 10%

## Running the Tests

### Prerequisites
1. Install k6: https://k6.io/docs/getting-started/installation/
2. Make sure your API endpoint is running at `http://34.201.38.94:8080/order`

### Run All Scenarios
```bash
k6 run script.ts
```

### Run Specific Scenarios
You can run individual scenarios by modifying the script or using k6's scenario filtering:

```bash
# Run only smoke test
k6 run --env TEST_TYPE=smoke script.ts

# Run only average load test
k6 run --env TEST_TYPE=average_load script.ts

# Run only high load test
k6 run --env TEST_TYPE=high_load script.ts

# Run only spike test
k6 run --env TEST_TYPE=spike script.ts

# Run only breakpoint test
k6 run --env TEST_TYPE=breakpoint script.ts
```

### Customize Test Parameters
You can modify the following parameters in the script:
- `vus`: Number of virtual users
- `duration`: Test duration
- `stages`: Ramp-up/ramp-down patterns
- `thresholds`: Performance criteria

## Expected Results

The script will generate:
- Real-time metrics during test execution
- Summary report with pass/fail status for each threshold
- Detailed metrics for each test scenario

## Monitoring

Watch for:
- Response times exceeding thresholds
- High error rates
- System resource usage
- API endpoint availability

### Breakpoint Test Analysis
When running the breakpoint test, pay special attention to:
1. **Response Time Curve**: Look for the point where response times start increasing exponentially
2. **Error Rate Spike**: Identify when errors start occurring frequently
3. **Throughput Plateau**: Notice when request rate stops increasing despite more users
4. **Resource Bottlenecks**: Monitor CPU, memory, and network usage

## Troubleshooting

1. **Connection errors**: Verify the API endpoint URL is correct and accessible
2. **High error rates**: Check if the API can handle the load
3. **Timeout errors**: Consider increasing response time thresholds or reducing load
4. **Memory issues**: Reduce the number of virtual users if your system can't handle the load 