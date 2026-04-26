export interface CartItem {
  id: string;
  product_id: string;
  product_name: string;
  product_price: number;
  product_image?: string;
  quantity: number;
  unit_price: number;
  subtotal: number;
}

export interface Cart {
  id: string;
  user_id: string;
  items: CartItem[];
  total: number;
  item_count: number;
  created_at: string;
  updated_at: string;
}