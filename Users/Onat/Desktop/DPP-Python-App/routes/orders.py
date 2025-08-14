from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from app import db
from models.orders import Order
from datetime import datetime
import random

orders_bp = Blueprint('orders', __name__)

@orders_bp.route('/')
def index():
    """Orders main page"""
    orders = Order.query.order_by(Order.created_date.desc()).all()
    total_orders = Order.query.count()
    pending_orders = Order.query.filter_by(status='pending').count()
    completed_orders = Order.query.filter_by(status='completed').count()
    
    stats = {
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'completed_orders': completed_orders,
        'processing_orders': Order.query.filter_by(status='processing').count()
    }
    
    return render_template('orders.html', orders=orders, stats=stats)

@orders_bp.route('/random-creator')
def random_creator():
    """Random Order Creator page"""
    return render_template('random_creator.html')

@orders_bp.route('/api/orders')
def api_orders():
    """API endpoint for all orders"""
    orders = Order.query.order_by(Order.created_date.desc()).all()
    return jsonify([order.to_dict() for order in orders])

@orders_bp.route('/api/orders/<int:order_id>')
def api_order_detail(order_id):
    """API endpoint for specific order"""
    order = Order.query.get_or_404(order_id)
    return jsonify(order.to_dict())

@orders_bp.route('/api/orders', methods=['POST'])
def api_create_order():
    """API endpoint to create new order"""
    try:
        data = request.get_json()
        
        order = Order(
            country=data.get('country'),
            facility=data.get('facility'),
            po_number=data.get('po_number'),
            style_name=data.get('style_name'),
            product_type=data.get('product_type'),
            fabric_type=data.get('fabric_type'),
            fabric_name=data.get('fabric_name'),
            fabric_construction=data.get('fabric_construction'),
            fabric_weight=float(data.get('fabric_weight', 0)),
            quantity=int(data.get('quantity', 0)),
            status=data.get('status', 'pending')
        )
        
        db.session.add(order)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Order created successfully',
            'order': order.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error creating order: {str(e)}'
        }), 400

@orders_bp.route('/api/orders/random', methods=['POST'])
def api_create_random_order():
    """API endpoint to create random order"""
    try:
        count = int(request.json.get('count', 1))
        created_orders = []
        
        for _ in range(min(count, 50)):  # Limit to 50 orders at once
            order = Order.create_random_order()
            db.session.add(order)
            created_orders.append(order)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'{len(created_orders)} random orders created successfully',
            'orders': [order.to_dict() for order in created_orders]
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error creating random orders: {str(e)}'
        }), 400

@orders_bp.route('/api/orders/<int:order_id>', methods=['PUT'])
def api_update_order(order_id):
    """API endpoint to update order"""
    try:
        order = Order.query.get_or_404(order_id)
        data = request.get_json()
        
        # Update fields
        for field in ['country', 'facility', 'po_number', 'style_name', 
                     'product_type', 'fabric_type', 'fabric_name', 'fabric_construction', 'status']:
            if field in data:
                setattr(order, field, data[field])
        
        if 'fabric_weight' in data:
            order.fabric_weight = float(data['fabric_weight'])
        if 'quantity' in data:
            order.quantity = int(data['quantity'])
        
        order.updated_date = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Order updated successfully',
            'order': order.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error updating order: {str(e)}'
        }), 400

@orders_bp.route('/api/orders/<int:order_id>', methods=['DELETE'])
def api_delete_order(order_id):
    """API endpoint to delete order"""
    try:
        order = Order.query.get_or_404(order_id)
        db.session.delete(order)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Order deleted successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error deleting order: {str(e)}'
        }), 400

@orders_bp.route('/api/orders/bulk-delete', methods=['POST'])
def api_bulk_delete_orders():
    """API endpoint to delete all orders"""
    try:
        deleted_count = Order.query.count()
        Order.query.delete()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'{deleted_count} orders deleted successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error deleting orders: {str(e)}'
        }), 400