import grpc from 'k6/net/grpc';
import { check, sleep } from 'k6';
import { grpcOptions } from './test-config.ts';
import { generateRandomRequestBody, timeout } from './request-generator.ts';
import { orderServiceGrpcUrl } from './order-service-config.ts';
import { K6TestResults } from './k6-results.interface.ts';

export { grpcOptions as options };

const client = new grpc.Client();
client.load(['.'], 'order.proto');

export default function () {
  const payload = generateRandomRequestBody();

  client.connect(orderServiceGrpcUrl, { 
    plaintext: true,
    timeout // No timeout (infinity)
  });
  
  const response = client.invoke('order.OrderService/createOrder', payload, {
    timeout // No timeout (infinity)
  });
  
  client.close();

  check(response, {
    'status OK': (r) => r && r.status === grpc.StatusOK,
    'response validation': (r) => {
      const message = r.message as any;
      return message.status === 'success' && message.order && message.errors.length === 0;
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