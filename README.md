# E-commerce API System

A robust e-commerce API system built with Flask, MongoDB, and Redis.

## Features

- JWT Authentication for Users and Admins
- Product Management (CRUD operations)
- Shopping Cart System
- Order Processing
- Discount & Coupon System
- Redis Caching
- Rate Limiting
- Background Task Processing
- AWS Deployment Ready

## Tech Stack

- Flask
- MongoDB
- Redis
- Celery
- JWT Authentication
- AWS (for deployment)

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
MONGODB_URI=your_mongodb_uri
REDIS_URL=your_redis_url
JWT_SECRET_KEY=your_jwt_secret
AWS_ACCESS_KEY=your_aws_access_key
AWS_SECRET_KEY=your_aws_secret_key
AWS_BUCKET_NAME=your_bucket_name
```

4. Run the application:

```bash
python run.py
```

## API Documentation

### Authentication

- POST /api/auth/register - Register a new user
- POST /api/auth/login - Login user
- POST /api/auth/refresh - Refresh JWT token

### Products

- GET /api/products - Get all products
- GET /api/products/<id> - Get product by ID
- POST /api/products - Create new product (Admin only)
- PUT /api/products/<id> - Update product (Admin only)
- DELETE /api/products/<id> - Delete product (Admin only)

### Cart

- GET /api/cart - Get user's cart
- POST /api/cart/items - Add item to cart
- DELETE /api/cart/items/<id> - Remove item from cart

### Orders

- POST /api/orders - Create new order
- GET /api/orders - Get user's orders
- GET /api/orders/<id> - Get order details
- PUT /api/orders/<id>/status - Update order status (Admin only)

### Coupons

- POST /api/coupons - Create new coupon (Admin only)
- GET /api/coupons - Get all coupons
- POST /api/coupons/apply - Apply coupon to cart

## Security Features

- JWT Authentication
- Password Hashing
- Rate Limiting
- Input Validation
- CORS Protection
- AWS S3 for secure file storage

## Deployment

The application is configured for deployment on AWS with:

- Gunicorn as WSGI server
- Redis for caching
- Celery for background tasks
- MongoDB Atlas for database
- AWS S3 for file storage
