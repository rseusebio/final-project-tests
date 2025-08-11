// Interface definitions for k6 test results

export interface K6Options {
  summaryTrendStats: string[];
  summaryTimeUnit: string;
  noColor: boolean;
}

export interface K6State {
  isStdOutTTY: boolean;
  isStdErrTTY: boolean;
  testRunDurationMs: number;
}

export interface MetricValues {
  count?: number;
  rate?: number;
  value?: number;
  min?: number;
  max?: number;
  avg?: number;
  med?: number;
  p90?: number;
  p95?: number;
  passes?: number;
  fails?: number;
}

export interface MetricThreshold {
  ok: boolean;
}

export interface MetricThresholds {
  [key: string]: MetricThreshold;
}

export interface K6Metric {
  type: string;
  contains: string;
  values: MetricValues;
  thresholds?: MetricThresholds;
}

export interface K6Metrics {
  data_sent: K6Metric;
  data_received: K6Metric;
  iteration_duration: K6Metric;
  iterations: K6Metric;
  checks: K6Metric;
  grpc_req_duration: K6Metric;
  vus: K6Metric;
  vus_max: K6Metric;
  [key: string]: K6Metric;
}

export interface K6Check {
  name: string;
  path: string;
  id: string;
  passes: number;
  fails: number;
}

export interface K6Group {
  name: string;
  path: string;
  id: string;
  groups: K6Group[];
  checks: K6Check[];
}

export interface K6TestResults {
  options: K6Options;
  state: K6State;
  metrics: K6Metrics;
  root_group: K6Group;
} 