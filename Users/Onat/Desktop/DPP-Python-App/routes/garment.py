from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from app import db
from models.garment import Garment
from datetime import datetime

garment_bp = Blueprint('garment', __name__)

@garment_bp.route('/')
def index():
    """Garment DPP main page"""
    garments = Garment.query.order_by(Garment.created_date.desc()).all()
    stats = Garment.get_stats()
    return render_template('garment.html', garments=garments, stats=stats)

@garment_bp.route('/api/garments')
def api_garments():
    """API endpoint for all garments"""
    garments = Garment.query.all()
    return jsonify([garment.to_dict() for garment in garments])

@garment_bp.route('/api/garments/<int:garment_id>')
def api_garment_detail(garment_id):
    """API endpoint for specific garment"""
    garment = Garment.query.get_or_404(garment_id)
    return jsonify(garment.to_dict())

@garment_bp.route('/api/garments', methods=['POST'])
def api_create_garment():
    """API endpoint to create new garment"""
    try:
        data = request.get_json()
        
        garment = Garment(
            country=data.get('country'),
            production_facility=data.get('production_facility'),
            po_number=data.get('po_number'),
            style_name=data.get('style_name'),
            product_type=data.get('product_type'),
            fabric_type=data.get('fabric_type'),
            fabric_name=data.get('fabric_name'),
            fabric_construction=data.get('fabric_construction'),
            fabric_weight=float(data.get('fabric_weight', 0)),
            quantity=int(data.get('quantity', 0)),
            carbon_footprint=float(data.get('carbon_footprint', 0)),
            sustainability_score=int(data.get('sustainability_score', 50))
        )
        
        db.session.add(garment)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Garment created successfully',
            'garment': garment.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error creating garment: {str(e)}'
        }), 400

@garment_bp.route('/api/garments/<int:garment_id>', methods=['PUT'])
def api_update_garment(garment_id):
    """API endpoint to update garment"""
    try:
        garment = Garment.query.get_or_404(garment_id)
        data = request.get_json()
        
        # Update fields
        for field in ['country', 'production_facility', 'po_number', 'style_name', 
                     'product_type', 'fabric_type', 'fabric_name', 'fabric_construction']:
            if field in data:
                setattr(garment, field, data[field])
        
        if 'fabric_weight' in data:
            garment.fabric_weight = float(data['fabric_weight'])
        if 'quantity' in data:
            garment.quantity = int(data['quantity'])
        if 'carbon_footprint' in data:
            garment.carbon_footprint = float(data['carbon_footprint'])
        if 'sustainability_score' in data:
            garment.sustainability_score = int(data['sustainability_score'])
        
        garment.updated_date = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Garment updated successfully',
            'garment': garment.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error updating garment: {str(e)}'
        }), 400

@garment_bp.route('/api/garments/<int:garment_id>', methods=['DELETE'])
def api_delete_garment(garment_id):
    """API endpoint to delete garment"""
    try:
        garment = Garment.query.get_or_404(garment_id)
        db.session.delete(garment)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Garment deleted successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error deleting garment: {str(e)}'
        }), 400

@garment_bp.route('/api/stats')
def api_garment_stats():
    """API endpoint for garment statistics"""
    stats = Garment.get_stats()
    return jsonify(stats)