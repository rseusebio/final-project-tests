// @ts-ignore - k6-utils is a k6-specific library
import { randomString, randomIntBetween } from 'https://jslib.k6.io/k6-utils/1.2.0/index.js';

// Helper function to generate random string with prefix
function generateId(prefix: string, length: number = 9): string {
  return `${prefix}_${randomString(length, '0123456789')}`;
}

// Helper function to generate random email
function generateEmail(): string {
  const names = ['John', 'Jane', 'Mike', 'Sarah', 'David', 'Lisa', 'Robert', 'Emma', 'James', 'Maria'];
  const domains = ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', 'example.com'];
  const name = names[randomIntBetween(0, names.length - 1)];
  const domain = domains[randomIntBetween(0, domains.length - 1)];
  return `${name.toLowerCase()}.${randomString(5, 'abcdefghijklmnopqrstuvwxyz')}@${domain}`;
}

// Helper function to generate random phone number
function generatePhone(): string {
  const areaCode = randomIntBetween(200, 999);
  const prefix = randomIntBetween(200, 999);
  const line = randomIntBetween(1000, 9999);
  return `1-${areaCode}-${prefix}-${line}`;
}

// Helper function to generate random address
function generateAddress(): {
  street: string;
  city: string;
  state: string;
  country: string;
  postalCode: string;
} {
  const streets = ['Main St', 'Oak Ave', 'Pine Rd', 'Elm St', 'Maple Dr', 'Cedar Ln', 'Birch Way', 'Spruce Ct'];
  const cities = ['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix', 'Philadelphia', 'San Antonio', 'San Diego'];
  const states = ['New York', 'California', 'Texas', 'Florida', 'Illinois', 'Pennsylvania', 'Ohio', 'Georgia'];
  const countries = ['US'];
  
  return {
    street: `${randomIntBetween(1, 9999)} ${streets[randomIntBetween(0, streets.length - 1)]}`,
    city: cities[randomIntBetween(0, cities.length - 1)],
    state: states[randomIntBetween(0, states.length - 1)],
    country: countries[randomIntBetween(0, countries.length - 1)],
    postalCode: randomString(5, '0123456789'),
  };
}

// Helper function to generate random product attributes
function generateProductAttributes(): {
  color: string;
  size: string;
  variantId: string;
  material: string;
  weight: number;
  dimensions: {
    lengthCm: number;
    widthCm: number;
    heightCm: number;
  };
} {
  const colors = ['Red', 'Blue', 'Green', 'Yellow', 'Black', 'White', 'Purple', 'Orange'];
  const sizes = ['Small', 'Medium', 'Large', 'X-Large'];
  const materials = ['Aluminum', 'Plastic', 'Steel', 'Wood', 'Glass', 'Ceramic'];
  
  const color = colors[randomIntBetween(0, colors.length - 1)];
  const size = sizes[randomIntBetween(0, sizes.length - 1)];
  const material = materials[randomIntBetween(0, materials.length - 1)];
  
  return {
    color,
    size,
    variantId: `var_${randomString(3, '0123456789')}_${color.toLowerCase()}_${size.charAt(0).toLowerCase()}`,
    material,
    weight: parseFloat((Math.random() * 2 + 0.1).toFixed(2)),
    dimensions: {
      lengthCm: randomIntBetween(5, 50),
      widthCm: randomIntBetween(3, 30),
      heightCm: randomIntBetween(2, 20),
    },
  };
}

// Helper function to generate random pricing
function generatePricing(): {
  unitPrice: number;
  discountApplied: number;
  promotionCode: string;
} {
  const unitPrice = parseFloat((Math.random() * 100 + 5).toFixed(2));
  // Always generate a positive discount to satisfy validation
  const discountApplied = parseFloat((Math.random() * 10 + 0.01).toFixed(2));
  const promotionCodes = ['SUMMER25', 'FREESHIP', 'WELCOME10', 'LOYALTY15', 'HOLIDAY20', ''];
  const promotionCode = promotionCodes[randomIntBetween(0, promotionCodes.length - 1)];
  
  return {
    unitPrice,
    discountApplied,
    promotionCode,
  };
}

// Helper function to generate random customization
function generateCustomization(): {
  engraving: string;
  giftWrap: boolean;
} {
  const engravings = ['Gift for Alice', 'Happy Birthday', 'Congratulations', 'Best Wishes', 'Love You', 'tests'];
  const engraving = Math.random() > 0.5 ? engravings[randomIntBetween(0, engravings.length - 1)] : 'test';
  
  return {
    engraving,
    giftWrap: true, // Always true to satisfy validation
  };
}

// Helper function to generate random fulfillment
function generateFulfillment(): {
  type: string;
  warehouseId?: string;
  pickupLocationId?: string;
  expectedDeliveryDate?: string;
} {
  const types = ['ship', 'pickup'];
  const type = types[randomIntBetween(0, types.length - 1)];
  
  if (type === 'ship') {
    return {
      type,
      warehouseId: `wh_${randomString(3, '0123456789')}`,
      expectedDeliveryDate: `2025-${String(randomIntBetween(7, 12)).padStart(2, '0')}-${String(randomIntBetween(1, 28)).padStart(2, '0')}`,
    };
  } else {
    return {
      type,
      pickupLocationId: `store_${randomString(3, '0123456789')}`,
      warehouseId: `wh_${randomString(3, '0123456789')}`,
    };
  }
}

// Helper function to generate random restrictions
function generateRestrictions(): {
  maxQuantityPerOrder: number;
  requiresAgeVerification: boolean;
  hazardousMaterial: boolean;
} {
  return {
    maxQuantityPerOrder: randomIntBetween(1, 20),
    requiresAgeVerification: true, // Always true to satisfy validation
    hazardousMaterial: true, // Always true to satisfy validation
  };
}

// Helper function to generate random product
function generateProduct(): {
  productId: string;
  sku: string;
  quantity: number;
  attributes: any;
  pricing: any;
  customization: any;
  fulfillment: any;
  restrictions: any;
} {
  const productId = `prod_${String(randomIntBetween(1, 999)).padStart(3, '0')}`;
  const sku = `WIDGET-${String.fromCharCode(65 + randomIntBetween(0, 25))}-${['RED', 'BLUE', 'GREEN', 'BLACK', 'WHITE'][randomIntBetween(0, 4)]}`;
  
  return {
    productId,
    sku,
    quantity: randomIntBetween(1, 5),
    attributes: generateProductAttributes(),
    pricing: generatePricing(),
    customization: generateCustomization(),
    fulfillment: generateFulfillment(),
    restrictions: generateRestrictions(),
  };
}

// Helper function to generate random payment method
function generatePaymentMethod(): {
  paymentMethodId: string;
  type: string;
  token: string;
  lastFour: string;
  brand: string;
  expirationDate: string;
  cvv: string;
  cardholderName: string;
  billingAddress: any;
} {
  const brands = ['Visa', 'Mastercard', 'American Express', 'Discover'];
  const brand = brands[randomIntBetween(0, brands.length - 1)];
  const lastFour = randomString(4, '0123456789');
  const month = String(randomIntBetween(1, 12)).padStart(2, '0');
  const year = String(randomIntBetween(26, 30));
  
  const address = generateAddress();
  
  return {
    paymentMethodId: generateId('pm', 9),
    type: 'credit_card',
    token: `tok_${brand.toLowerCase()}_${randomString(9, '0123456789')}`,
    lastFour,
    brand,
    expirationDate: `${month}/${year}`,
    cvv: '***',
    cardholderName: `${['John', 'Jane', 'Mike', 'Sarah', 'David', 'Lisa'][randomIntBetween(0, 5)]} ${['Smith', 'Johnson', 'Williams', 'Brown', 'Jones'][randomIntBetween(0, 4)]}`,
    billingAddress: {
      addressId: generateId('addr', 9),
      ...address,
      deliveryInstructions: Math.random() > 0.5 ? 'Deliver to reception' : '',
    },
  };
}

// Helper function to generate random shipping address
function generateShippingAddress(): {
  addressId: string;
  addressType: string;
  street: string;
  city: string;
  state: string;
  country: string;
  postalCode: string;
  deliveryInstructions: string;
  coordinates: {
    latitude: number;
    longitude: number;
  };
} {
  const addressTypes = ['home', 'work', 'other'];
  const address = generateAddress();
  
  return {
    addressId: generateId('addr', 9),
    addressType: addressTypes[randomIntBetween(0, addressTypes.length - 1)],
    ...address,
    deliveryInstructions: Math.random() > 0.5 ? 'Leave package at front gate' : '',
    coordinates: {
      latitude: parseFloat((Math.random() * 180 - 90).toFixed(6)),
      longitude: parseFloat((Math.random() * 360 - 180).toFixed(6)),
    },
  };
}

// Helper function to generate random customer details
function generateCustomerDetails(): {
  email: string;
  phone: string;
  loyaltyProgram: {
    memberId: string;
    tier: string;
  };
} {
  const tiers = ['bronze', 'silver', 'gold', 'platinum'];
  
  return {
    email: generateEmail(),
    phone: generatePhone(),
    loyaltyProgram: {
      memberId: generateId('loyal', 6),
      tier: tiers[randomIntBetween(0, tiers.length - 1)],
    },
  };
}

// Helper function to generate random client metadata
function generateClientMetadata(): {
  deviceId: string;
  ipAddress: string;
  userAgent: string;
  browserLanguage: string;
  timezone: string;
} {
  const userAgents = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 14_7_1 like Mac OS X) AppleWebKit/605.1.15',
  ];
  const languages = ['en-US', 'en-GB', 'es-ES', 'fr-FR', 'de-DE', 'pt-BR'];
  const timezones = ['America/New_York', 'America/Los_Angeles', 'Europe/London', 'Europe/Berlin', 'Asia/Tokyo', 'America/Sao_Paulo'];
  
  return {
    deviceId: generateId('dev', 9),
    ipAddress: `${randomIntBetween(192, 223)}.${randomIntBetween(1, 255)}.${randomIntBetween(1, 255)}.${randomIntBetween(1, 255)}`,
    userAgent: userAgents[randomIntBetween(0, userAgents.length - 1)],
    browserLanguage: languages[randomIntBetween(0, languages.length - 1)],
    timezone: timezones[randomIntBetween(0, timezones.length - 1)],
  };
}

// Main function to generate random request body
export function generateRandomRequestBody(): any {
  const requestId = generateId('req', 9);
  const customerId = randomIntBetween(100000000, 999999999);
  const orderId = generateId('ord', 9);
  const cartId = generateId('cart', 6);
  const sessionId = generateId('sess', 6);
  
  // Generate random number of products (1-5)
  const productCount = randomIntBetween(1, 5);
  const products: any[] = [];
  for (let i = 0; i < productCount; i++) {
    products.push(generateProduct());
  }
  
  // Generate random promotion codes
  const promotionCodes: string[] = [];
  if (Math.random() > 0.5) {
    const codes = ['SUMMER25', 'FREESHIP', 'WELCOME10', 'LOYALTY15', 'HOLIDAY20'];
    const numCodes = randomIntBetween(0, 2);
    for (let i = 0; i < numCodes; i++) {
      promotionCodes.push(codes[randomIntBetween(0, codes.length - 1)]);
    }
  }
  
  // Generate timestamp
  const now = new Date();
  const timestamp = now.toISOString().replace('Z', '-03:00');
  
  return {
    requestId,
    customerId,
    orderDetails: {
      orderId,
      channel: 'web',
      cartId,
      sessionId,
      promotionCodes,
      currency: 'USD',
      timestamp,
    },
    products,
    paymentMethod: generatePaymentMethod(),
    shippingAddress: generateShippingAddress(),
    customerDetails: generateCustomerDetails(),
    clientMetadata: generateClientMetadata(),
    options: {
      validateStock: true,
      validatePayment: true,
      reserveStock: true,
      allowPartialFulfillment: true, // Changed to true to satisfy validation
      notifyOnSuccess: true,
      maxResponseTimeMs: 2000,
    },
    audit: {
      initiatedBy: 'web_client',
      initiatorId: generateId('user', 9),
      operationReference: `ord_create_${randomString(6, '0123456789')}`,
    },
    fake: false,
  };
}

export const timeout = '999999999s';