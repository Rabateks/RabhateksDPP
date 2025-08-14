from app import db
from datetime import datetime
import uuid
import random

class Order(db.Model):
    __tablename__ = 'orders'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.String(50), unique=True, nullable=False)
    country = db.Column(db.String(100), nullable=False)
    facility = db.Column(db.String(200), nullable=False)
    po_number = db.Column(db.String(50), nullable=False)
    style_name = db.Column(db.String(100), nullable=False)
    product_type = db.Column(db.String(100), nullable=False)
    fabric_type = db.Column(db.String(100))
    fabric_name = db.Column(db.String(100))
    fabric_construction = db.Column(db.String(100))
    fabric_weight = db.Column(db.Float)  # in grams
    quantity = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, processing, completed, cancelled
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    updated_date = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __init__(self, **kwargs):
        super(Order, self).__init__(**kwargs)
        if not self.order_id:
            self.order_id = f"ORD-{str(uuid.uuid4())[:8].upper()}"
    
    def __repr__(self):
        return f'<Order {self.order_id} - {self.style_name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'order_id': self.order_id,
            'country': self.country,
            'facility': self.facility,
            'po_number': self.po_number,
            'style_name': self.style_name,
            'product_type': self.product_type,
            'fabric_type': self.fabric_type,
            'fabric_name': self.fabric_name,
            'fabric_construction': self.fabric_construction,
            'fabric_weight': self.fabric_weight,
            'quantity': self.quantity,
            'status': self.status,
            'created_date': self.created_date.isoformat() if self.created_date else None,
            'updated_date': self.updated_date.isoformat() if self.updated_date else None
        }
    
    @classmethod
    def create_random_order(cls):
        """Create a random order for testing"""
        countries = ['Turkey', 'Bangladesh', 'Vietnam', 'China', 'India', 'Pakistan']
        facilities = [
            'Rabateks Textile Manufacturing',
            'Mango Apparel Facilities',
            'Global Textile Solutions',
            'Premium Garment Factory',
            'Sustainable Fashion Hub',
            'Modern Textile Complex'
        ]
        product_types = ['T-Shirt', 'Polo Shirt', 'Dress Shirt', 'Casual Shirt', 'Blouse', 'Tank Top']
        fabric_types = ['Cotton', 'Polyester', 'Cotton Blend', 'Linen', 'Viscose', 'Modal']
        fabric_names = ['Premium Cotton', 'Eco-Friendly Blend', 'Organic Cotton', 'Recycled Polyester', 'Bamboo Fiber']
        constructions = ['Jersey', 'Poplin', 'Twill', 'Canvas', 'Interlock', 'Rib']
        
        return cls(
            country=random.choice(countries),
            facility=random.choice(facilities),
            po_number=f"PO-{random.randint(10000, 99999)}",
            style_name=f"Style-{random.randint(1000, 9999)}",
            product_type=random.choice(product_types),
            fabric_type=random.choice(fabric_types),
            fabric_name=random.choice(fabric_names),
            fabric_construction=random.choice(constructions),
            fabric_weight=round(random.uniform(120, 300), 1),
            quantity=random.randint(100, 5000),
            status=random.choice(['pending', 'processing', 'completed'])
        )