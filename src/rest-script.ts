import http from 'k6/http';
import { check, sleep } from 'k6';
import { generateRandomRequestBody, timeout } from './request-generator.ts';
import { restOptions } from './test-config.ts';
import { orderServiceUrl } from './order-service-config.ts';
import { K6TestResults } from './k6-results.interface.ts';

export { restOptions as options };

export default function () {
  const payload = generateRandomRequestBody();

  const response = http.post(orderServiceUrl, JSON.stringify(payload), {
    headers: { 'Content-Type': 'application/json' },
    timeout // No timeout (infinity)
  });

  check(response, {
    'status OK': (r) => r.status === 200,
    'response validation': (r) => {
      const message = JSON.parse(r.body as string) as any;
      return message.succeeded === true && message.order;
    },
  });

  sleep(1);
}

export function handleSummary(data: K6TestResults) {
  const jsonContent = JSON.stringify(data, null, 2);
    
  return {
    [__ENV.FILE_PATH]: jsonContent,
    'stdout': jsonContent
  };
}