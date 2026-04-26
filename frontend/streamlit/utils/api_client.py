import requests
import streamlit as st
import os
from typing import Optional, Dict, Any

class APIClient:
    def __init__(self, token: str):
        self.base_url = os.getenv("API_BASE_URL", "http://localhost:8000/api")
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
    
    def get(self, endpoint: str, params: Optional[Dict] = None) -> Any:
        try:
            response = requests.get(
                f"{self.base_url}/{endpoint}",
                headers=self.headers,
                params=params
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            st.error(f"Error en la petición: {e}")
            return None
    
    def post(self, endpoint: str, data: Dict) -> Any:
        try:
            response = requests.post(
                f"{self.base_url}/{endpoint}",
                headers=self.headers,
                json=data
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            st.error(f"Error en la petición: {e}")
            return None
    
    def post_pdf(self, endpoint: str, data: Dict) -> Optional[bytes]:
        try:
            response = requests.post(
                f"{self.base_url}/{endpoint}",
                headers=self.headers,
                json=data
            )
            response.raise_for_status()
            return response.content
        except Exception as e:
            st.error(f"Error generando PDF: {e}")
            return None
    
    # Métodos específicos para estadísticas
    def get_statistics_daily(self, date: Optional[str] = None) -> Dict:
        if not date:
            from datetime import datetime
            date = datetime.now().date().isoformat()
        return self.get(f"statistics/sales/daily?date={date}") or {}
    
    def get_sales_timeline(self, days: int = 30) -> list:
        return self.get(f"statistics/sales/timeline?days={days}") or []
    
    def get_top_products(self, days: int = 30, limit: int = 10) -> list:
        return self.get(f"statistics/top-products?days={days}&limit={limit}") or []
    
    def get_products_by_category(self) -> list:
        return self.get("statistics/products/by-category") or []
    
    def get_customer_statistics(self) -> Dict:
        return self.get("statistics/customer/avg-purchase") or {}
    
    def generate_orders_report(self, filters: Dict) -> Optional[bytes]:
        return self.post_pdf("reports/orders-pdf", filters)
    
    def generate_executive_report(self, filters: Dict) -> Optional[bytes]:
        return self.post_pdf("reports/executive-pdf", filters)