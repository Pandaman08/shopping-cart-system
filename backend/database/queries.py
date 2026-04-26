# Common database queries
GET_USER_BY_EMAIL = "SELECT * FROM users WHERE email = $1"
GET_ACTIVE_CART = "SELECT * FROM carts WHERE user_id = $1 AND status = 'active'"
GET_PRODUCT_BY_ID = "SELECT * FROM products WHERE id = $1 AND is_active = true"

# You can add more queries as needed