export const orderServiceConfig = {
    ip: '54.236.30.76',
    restPort: 8080,
    grpcPort: 50051,
}

export const orderServiceUrl = `http://${orderServiceConfig.ip}:${orderServiceConfig.restPort}/order`;
export const orderServiceGrpcUrl = `${orderServiceConfig.ip}:${orderServiceConfig.grpcPort}`;