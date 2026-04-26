export interface User {
  id: string;
  email: string;
  full_name: string;
  role: 'cliente' | 'admin';
  created_at: string;
  last_login?: string;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterData {
  full_name: string;
  email: string;
  password: string;
}