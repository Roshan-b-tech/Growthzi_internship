from celery import Celery
from flask_mail import Message
from . import mail, jwt
from .models.user import User
from .models.order import Order

celery = Celery('tasks', broker='redis://localhost:6379/1')

@celery.task
def send_order_confirmation(user_id, order_id):
    user = User.get_by_id(jwt.db, user_id)
    order = Order.get_by_id(jwt.db, order_id)
    
    if not user or not order:
        return
    
    msg = Message(
        subject='Order Confirmation',
        recipients=[user.email]
    )
    
    # Create HTML email template
    msg.html = f"""
    <h2>Order Confirmation</h2>
    <p>Dear {user.name},</p>
    <p>Thank you for your order! Your order has been confirmed.</p>
    <h3>Order Details:</h3>
    <p>Order ID: {order_id}</p>
    <p>Total Amount: ${order.total_amount:.2f}</p>
    <p>Status: {order.status}</p>
    <h3>Items:</h3>
    <ul>
    """
    
    for item in order.items:
        product = Product.get_by_id(jwt.db, item.product_id)
        if product:
            msg.html += f"""
            <li>{product.name} x {item.quantity} - ${item.price * item.quantity:.2f}</li>
            """
    
    msg.html += """
    </ul>
    <p>Thank you for shopping with us!</p>
    """
    
    mail.send(msg)

@celery.task
def send_order_status_update(user_id, order_id, new_status):
    user = User.get_by_id(jwt.db, user_id)
    order = Order.get_by_id(jwt.db, order_id)
    
    if not user or not order:
        return
    
    msg = Message(
        subject='Order Status Update',
        recipients=[user.email]
    )
    
    # Create HTML email template
    msg.html = f"""
    <h2>Order Status Update</h2>
    <p>Dear {user.name},</p>
    <p>Your order status has been updated.</p>
    <h3>Order Details:</h3>
    <p>Order ID: {order_id}</p>
    <p>New Status: {new_status}</p>
    <p>Total Amount: ${order.total_amount:.2f}</p>
    <h3>Items:</h3>
    <ul>
    """
    
    for item in order.items:
        product = Product.get_by_id(jwt.db, item.product_id)
        if product:
            msg.html += f"""
            <li>{product.name} x {item.quantity} - ${item.price * item.quantity:.2f}</li>
            """
    
    msg.html += """
    </ul>
    <p>Thank you for your patience!</p>
    """
    
    mail.send(msg) 