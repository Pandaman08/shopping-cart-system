export interface OrderItem {
  id: string;
  product_id: string;
  product_name: string;
  quantity: number;
  unit_price: number;
  subtotal: number;
}

export interface Order {
  id: string;
  user_id: string;
  user_name: string;
  total_amount: number;
  status: 'pending' | 'paid' | 'shipped' | 'delivered' | 'cancelled';
  payment_method?: string;
  shipping_address?: string;
  items: OrderItem[];
  created_at: string;
  paid_at?: string;
}

export interface OrderCreate {
  payment_method: string;
  shipping_address: string;
}