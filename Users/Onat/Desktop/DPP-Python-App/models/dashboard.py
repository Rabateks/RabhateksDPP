from app import db
from datetime import datetime

class DashboardStats(db.Model):
    __tablename__ = 'dashboard_stats'
    
    id = db.Column(db.Integer, primary_key=True)
    active_dpps = db.Column(db.Integer, default=0)
    manufacturing_processes = db.Column(db.Integer, default=0)
    total_co2_monthly = db.Column(db.Float, default=0.0)
    monthly_operations = db.Column(db.Float, default=0.0)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'active_dpps': self.active_dpps,
            'manufacturing_processes': self.manufacturing_processes,
            'total_co2_monthly': self.total_co2_monthly,
            'monthly_operations': self.monthly_operations,
            'last_updated': self.last_updated.isoformat() if self.last_updated else None
        }

class DPPModule(db.Model):
    __tablename__ = 'dpp_modules'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)  # manufacturing, supply-chain, corporate
    description = db.Column(db.Text)
    icon = db.Column(db.String(10), default='📊')
    url_path = db.Column(db.String(200))
    status = db.Column(db.String(20), default='active')  # active, optimizing, maintenance
    metric1_label = db.Column(db.String(50))
    metric1_value = db.Column(db.String(20))
    metric2_label = db.Column(db.String(50))
    metric2_value = db.Column(db.String(20))
    metric3_label = db.Column(db.String(50))
    metric3_value = db.Column(db.String(20))
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category,
            'description': self.description,
            'icon': self.icon,
            'url_path': self.url_path,
            'status': self.status,
            'metric1_label': self.metric1_label,
            'metric1_value': self.metric1_value,
            'metric2_label': self.metric2_label,
            'metric2_value': self.metric2_value,
            'metric3_label': self.metric3_label,
            'metric3_value': self.metric3_value
        }