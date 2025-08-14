from app import db
from datetime import datetime
from sqlalchemy import func

class Garment(db.Model):
    __tablename__ = 'garments'
    
    id = db.Column(db.Integer, primary_key=True)
    country = db.Column(db.String(100), nullable=False)
    production_facility = db.Column(db.String(200), nullable=False)
    po_number = db.Column(db.String(50), nullable=False, unique=True)
    style_name = db.Column(db.String(100), nullable=False)
    product_type = db.Column(db.String(100), nullable=False)
    fabric_type = db.Column(db.String(100), nullable=False)
    fabric_name = db.Column(db.String(100))
    fabric_construction = db.Column(db.String(100))
    fabric_weight = db.Column(db.Float)  # in grams
    quantity = db.Column(db.Integer, nullable=False)
    carbon_footprint = db.Column(db.Float, default=0.0)  # in kg CO2
    sustainability_score = db.Column(db.Integer, default=50)  # 0-100
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    updated_date = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Garment {self.style_name} - {self.po_number}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'country': self.country,
            'production_facility': self.production_facility,
            'po_number': self.po_number,
            'style_name': self.style_name,
            'product_type': self.product_type,
            'fabric_type': self.fabric_type,
            'fabric_name': self.fabric_name,
            'fabric_construction': self.fabric_construction,
            'fabric_weight': self.fabric_weight,
            'quantity': self.quantity,
            'carbon_footprint': self.carbon_footprint,
            'sustainability_score': self.sustainability_score,
            'created_date': self.created_date.isoformat() if self.created_date else None,
            'updated_date': self.updated_date.isoformat() if self.updated_date else None
        }
    
    @classmethod
    def get_stats(cls):
        """Get garment statistics"""
        total_count = cls.query.count()
        total_quantity = db.session.query(func.sum(cls.quantity)).scalar() or 0
        unique_styles = db.session.query(func.count(func.distinct(cls.style_name))).scalar() or 0
        avg_weight = db.session.query(func.avg(cls.fabric_weight)).scalar() or 0
        total_carbon = db.session.query(func.sum(cls.carbon_footprint)).scalar() or 0
        
        return {
            'total_count': total_count,
            'total_quantity': total_quantity,
            'unique_styles': unique_styles,
            'avg_weight': round(avg_weight, 2) if avg_weight else 0,
            'total_carbon': round(total_carbon, 2) if total_carbon else 0
        }