// Function to get the test scenario based on environment variable
export function getTestScenario() {
  const testType = __ENV.TEST_TYPE || 'smoke';
  
  const scenarios = {
    smoke: {
      executor: 'constant-vus',
      vus: 3,
      duration: '1m',
      tags: { test_type: 'smoke' },
    },
    
    average_load: {
      executor: 'ramping-vus',
      startVUs: 10,
      stages: [
        { duration: '30s', target: 50 },  // Ramp up to 50 users
        { duration: '5m', target: 50 },  // Stay at 50 users
        { duration: '30s', target: 0 },   // Ramp down to 0
      ],
      tags: { test_type: 'average_load' },
    },
    
    high_load: {
      executor: 'ramping-vus',
      startVUs: 50,
      stages: [
        { duration: '30s', target: 200 },  // Ramp up to 200 users
        { duration: '5m', target: 200 },  // Stay at 200 users
        { duration: '30s', target: 0 },    // Ramp down to 0
      ],
      tags: { test_type: 'high_load' },
    },
    
    spike: {
      executor: 'ramping-vus',
      startVUs: 10,
      stages: [
        { duration: '1m', target: 10 },   // Baseline
        { duration: '30s', target: 1000 }, // Spike to 500 users
        { duration: '1m', target: 1000 },  // Hold spike
        { duration: '30s', target: 10 },  // Return to baseline
      ],
      tags: { test_type: 'spike' },
    },
    
    breakpoint: {
      executor: 'ramping-vus',
      startVUs: 1,
      stages: [
        { duration: '1m', target: 10 },    // Start with 10 users
        { duration: '1m', target: 25 },    // Increase to 25 users
        { duration: '1m', target: 50 },    // Increase to 50 users
        { duration: '1m', target: 100 },   // Increase to 100 users
        { duration: '1m', target: 200 },   // Increase to 200 users
        { duration: '1m', target: 400 },   // Increase to 400 users
        { duration: '1m', target: 600 },   // Increase to 600 users
        { duration: '1m', target: 800 },   // Increase to 800 users
        { duration: '1m', target: 1000 },  // Increase to 1000 users
        { duration: '1m', target: 1200 },  // Increase to 1200 users
        { duration: '1m', target: 1400 },  // Increase to 1400 users
        { duration: '1m', target: 1600 },  // Increase to 1600 users
      ],
      tags: { test_type: 'breakpoint' },
    },

    // New scenario specifically for protocol comparison
    comparison: {
      executor: 'ramping-vus',
      startVUs: 1,
      stages: [
        { duration: '30s', target: 10 },    // Warm up
        { duration: '1m', target: 50 },    // Low load
        { duration: '2m', target: 100 },   // Medium load
        { duration: '2m', target: 200 },   // High load
        { duration: '2m', target: 0 },     // Ramp down
      ],
      tags: { test_type: 'comparison' },
    },
  };
  
  return scenarios[testType] || scenarios.smoke;
}

// Unified thresholds for fair comparison
export const getUnifiedThresholds = (testType: string) => {
  const baseThresholds = {
    // Common metrics for both protocols
    iteration_duration: ['p(95)<10000'], // Overall iteration time (10s)
    checks: ['rate>0.99'],              // Success rate
  };

  const loadBasedThresholds = {
    smoke: {
      req_duration: ['p(95)<3000'],      // 3s for both protocols (realistic for current performance)
      error_rate: ['rate<0.01'],        // 1% error rate
    },
    average_load: {
      req_duration: ['p(95)<5000'],      // 5s for both protocols
      error_rate: ['rate<0.02'],        // 2% error rate
    },
    high_load: {
      req_duration: ['p(95)<8000'],      // 8s for both protocols
      error_rate: ['rate<0.05'],        // 5% error rate
    },
    spike: {
      req_duration: ['p(95)<12000'],     // 12s for both protocols
      error_rate: ['rate<0.10'],        // 10% error rate
    },
    breakpoint: {
      req_duration: ['p(95)<15000'],     // 15s for both protocols
      error_rate: ['rate<0.15'],        // 15% error rate
    },
    comparison: {
      req_duration: ['p(95)<6000'],     // 6s for both protocols
      error_rate: ['rate<0.05'],        // 5% error rate
    },
  };

  return {
    ...baseThresholds,
    ...loadBasedThresholds[testType] || loadBasedThresholds.smoke,
  };
};

// Legacy threshold functions for backward compatibility
export const getRestThresholds = (testType: string) => {
  const unified = getUnifiedThresholds(testType);
  return {
    http_req_duration: unified.req_duration,
    http_req_failed: unified.error_rate,
    checks: unified.checks,
    iteration_duration: unified.iteration_duration,
  };
};

export const getGrpcThresholds = (testType: string) => {
  const unified = getUnifiedThresholds(testType);
  return {
    grpc_req_duration: unified.req_duration,
    checks: unified.checks,
    iteration_duration: unified.iteration_duration,
  };
};

// k6 options with proper thresholds and metrics
export const restOptions = {
  scenarios: {
    [__ENV.TEST_TYPE || 'smoke']: getTestScenario(),
  },
  thresholds: getRestThresholds(__ENV.TEST_TYPE || 'smoke'),
  // Additional metrics for better comparison
  summaryTrendStats: ['avg', 'min', 'med', 'max', 'p(90)', 'p(95)', 'p(99)'],
  summaryTimeUnit: 'ms',
}; 

export const grpcOptions = {
  scenarios: {
    [__ENV.TEST_TYPE || 'smoke']: getTestScenario(),
  },
  thresholds: getGrpcThresholds(__ENV.TEST_TYPE || 'smoke'),
  // Additional metrics for better comparison
  summaryTrendStats: ['avg', 'min', 'med', 'max', 'p(90)', 'p(95)', 'p(99)'],
  summaryTimeUnit: 'ms',
};