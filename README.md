# E-commerce API System

A robust e-commerce API system built with Flask, MongoDB, and Redis. This system provides a complete backend solution for an e-commerce platform with features like user authentication, product management, shopping cart, order processing, and coupon management.

## Features

- **User Authentication & Authorization**

  - JWT-based authentication
  - Role-based access control (User/Admin)
  - Token refresh mechanism
  - Secure password hashing
  - Profile management

- **Product Management**

  - CRUD operations for products
  - Product categorization
  - Featured products
  - Product search
  - Stock management

- **Shopping Cart System**

  - Add/remove items
  - Update quantities
  - Cart total calculation
  - Persistent cart storage

- **Order Processing**

  - Order creation
  - Order status tracking
  - Order history
  - Shipping address management

- **Coupon System**

  - Create and manage coupons
  - Apply discounts to orders
  - Coupon validation
  - Usage tracking

- **Security Features**
  - JWT Authentication
  - Password Hashing
  - Rate Limiting
  - Input Validation
  - CORS Protection
  - Token Blacklisting

## Tech Stack

- **Backend Framework**: Flask
- **Database**: MongoDB
- **Caching**: Redis
- **Task Queue**: Celery
- **Authentication**: JWT
- **Email**: Flask-Mail
- **Deployment**: AWS (ready)

## Project Structure

```
app/
├── __init__.py          # Application factory
├── config.py            # Configuration settings
├── models/              # Database models
│   ├── user.py
│   ├── product.py
│   ├── cart.py
│   ├── order.py
│   └── coupon.py
├── routes/              # API endpoints
│   ├── auth.py
│   ├── products.py
│   ├── cart.py
│   ├── orders.py
│   └── coupons.py
└── utils/               # Utility functions
    └── email.py
```

## Setup

1. Create a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Set up environment variables:
   Create a `.env` file with the following variables:

```
MONGODB_URI=mongodb://localhost:27017/ecommerce
REDIS_URL=redis://localhost:6379/0
JWT_SECRET_KEY=your_jwt_secret
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your_email@gmail.com
MAIL_PASSWORD=your_email_password
```

4. Run the application:

```bash
python run.py
```

## API Documentation

### Authentication Endpoints

- **Register User**

  ```http
  POST /api/auth/register
  Content-Type: application/json
  {
    "username": "testuser",
    "email": "test@example.com",
    "password": "your_password",
    "role": "user"  # or "admin"
  }
  ```

- **Login**

  ```http
  POST /api/auth/login
  Content-Type: application/json
  {
    "email": "test@example.com",
    "password": "your_password"
  }
  ```

- **Logout**

  ```http
  POST /api/auth/logout
  Authorization: Bearer your_access_token
  ```

- **Refresh Token**
  ```http
  POST /api/auth/refresh
  Authorization: Bearer your_refresh_token
  ```

### Product Endpoints

- **Get All Products**

  ```http
  GET /api/products
  ```

- **Get Featured Products**

  ```http
  GET /api/products/featured
  ```

- **Get Single Product**

  ```http
  GET /api/products/{product_id}
  ```

- **Create Product** (Admin only)
  ```http
  POST /api/products
  Authorization: Bearer your_admin_token
  Content-Type: application/json
  {
    "name": "Product Name",
    "description": "Product Description",
    "price": 99.99,
    "category": "Electronics",
    "stock": 100,
    "image_url": "https://example.com/image.jpg"
  }
  ```

### Cart Endpoints

- **Get Cart**

  ```http
  GET /api/cart
  Authorization: Bearer your_access_token
  ```

- **Add to Cart**

  ```http
  POST /api/cart
  Authorization: Bearer your_access_token
  Content-Type: application/json
  {
    "product_id": "product_id_here",
    "quantity": 1
  }
  ```

- **Update Cart Item**

  ```http
  PUT /api/cart/{product_id}
  Authorization: Bearer your_access_token
  Content-Type: application/json
  {
    "quantity": 2
  }
  ```

- **Remove from Cart**
  ```http
  DELETE /api/cart/{product_id}
  Authorization: Bearer your_access_token
  ```

### Order Endpoints

- **Create Order**

  ```http
  POST /api/orders
  Authorization: Bearer your_access_token
  Content-Type: application/json
  {
    "shipping_address": {
      "street": "123 Main St",
      "city": "Example City",
      "state": "Example State",
      "country": "Example Country",
      "zip_code": "12345"
    },
    "payment_method": "credit_card",
    "coupon_code": "DISCOUNT10"  # Optional
  }
  ```

- **Get Orders**
  ```http
  GET /api/orders
  Authorization: Bearer your_access_token
  ```

### Coupon Endpoints (Admin only)

- **Create Coupon**
  ```http
  POST /api/coupons
  Authorization: Bearer your_admin_token
  Content-Type: application/json
  {
    "code": "SUMMER2024",
    "discount_percent": 20,
    "valid_from": "2024-06-01T00:00:00Z",
    "valid_until": "2024-08-31T23:59:59Z",
    "min_purchase": 50,
    "max_discount": 100,
    "usage_limit": 100
  }
  ```

## Security Features

- **JWT Authentication**: Secure token-based authentication
- **Password Hashing**: Passwords are hashed using Werkzeug's security functions
- **Rate Limiting**: API endpoints are protected against abuse
- **Input Validation**: All inputs are validated before processing
- **CORS Protection**: Cross-Origin Resource Sharing is properly configured
- **Token Blacklisting**: Revoked tokens are stored in a blacklist

## Error Handling

The API uses standard HTTP status codes:

- 200: Success
- 201: Created
- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 409: Conflict
- 422: Unprocessable Entity
- 429: Too Many Requests
- 500: Internal Server Error

## Testing

To test the API:

1. Register a new user
2. Login to get access and refresh tokens
3. Use the access token in the Authorization header for protected endpoints
4. Create products (as admin)
5. Add products to cart
6. Create orders
7. Apply coupons

## Deployment

The application is configured for deployment on AWS with:

- Gunicorn as WSGI server
- Redis for caching
- Celery for background tasks
- MongoDB Atlas for database
- AWS S3 for file storage

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License.
