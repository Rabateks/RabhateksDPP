from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'rabateks-dpp-secret-key-2024'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database/dpp.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# REMOVE ALL MODEL AND ROUTE IMPORTS FROM HERE
# They will be imported inside functions to avoid circular imports

@app.before_first_request
def create_tables():
    """Create database tables before first request"""
    # Create database directory if it doesn't exist
    db_dir = os.path.dirname(app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', ''))
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir)
    
    # Import models here to avoid circular imports
    from models.garment import Garment
    from models.dashboard import DashboardStats, DPPModule
    from models.orders import Order
    
    # Create all tables
    db.create_all()
    
    # Initialize sample data if tables are empty
    if DPPModule.query.count() == 0:
        sample_modules = [
            DPPModule(name="Fibre DPP", description="Fiber traceability and sustainability", icon="fas fa-seedling", url="/fibre", color="success"),
            DPPModule(name="Yarn DPP", description="Yarn production and quality tracking", icon="fas fa-thread", url="/yarn", color="info"),
            DPPModule(name="Fabric DPP", description="Fabric manufacturing and properties", icon="fas fa-cut", url="/fabric", color="warning"),
            DPPModule(name="Garment DPP", description="Complete garment lifecycle tracking", icon="fas fa-tshirt", url="/garment", color="primary"),
            DPPModule(name="Chemical & Dyes", description="Chemical usage and safety tracking", icon="fas fa-flask", url="/chemicals", color="danger"),
            DPPModule(name="Energy & Utilities", description="Energy consumption monitoring", icon="fas fa-bolt", url="/energy", color="warning"),
            DPPModule(name="Finishing", description="Finishing processes and quality", icon="fas fa-magic", url="/finishing", color="info"),
            DPPModule(name="IT DPP", description="IT infrastructure and digital tracking", icon="fas fa-laptop", url="/it", color="dark"),
            DPPModule(name="Logistics", description="Supply chain and logistics management", icon="fas fa-truck", url="/logistics", color="success"),
            DPPModule(name="Office DPP", description="Office operations and administration", icon="fas fa-building", url="/office", color="secondary"),
            DPPModule(name="Office Supplies", description="Office supplies and waste management", icon="fas fa-paperclip", url="/supplies", color="info"),
            DPPModule(name="Order Delivery", description="Order processing and delivery tracking", icon="fas fa-shipping-fast", url="/orders", color="primary"),
            DPPModule(name="Packaging", description="Packaging materials and sustainability", icon="fas fa-box", url="/packaging", color="warning"),
            DPPModule(name="Retail Distribution", description="Retail and distribution management", icon="fas fa-store", url="/retail", color="success"),
            DPPModule(name="Transport DPP", description="Transportation and carbon footprint", icon="fas fa-car", url="/transport", color="danger")
        ]
        
        for module in sample_modules:
            db.session.add(module)
        
        db.session.commit()
        print("✅ Sample DPP modules initialized!")

# API Routes
@app.route('/api/stats')
def api_stats():
    """Get general statistics"""
    try:
        # Import models here to avoid circular imports
        from models.garment import Garment
        from models.orders import Order
        
        total_garments = Garment.query.count()
        total_orders = Order.query.count()
        
        return jsonify({
            'success': True,
            'total_garments': total_garments,
            'total_orders': total_orders,
            'status': 'connected'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'status': 'error'
        }), 500

if __name__ == '__main__':
    # Import and register blueprints here to avoid circular imports
    from routes.main import main_bp
    from routes.garment import garment_bp
    from routes.orders import orders_bp
    
    # Register blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(garment_bp, url_prefix='/garment')
    app.register_blueprint(orders_bp, url_prefix='/orders')
    
    print("🚀 Starting Rabateks DPP Flask Application...")
    print("📊 Dashboard: http://localhost:5000")
    print("👕 Garment DPP: http://localhost:5000/garment")
    print("📦 Orders: http://localhost:5000/orders")
    print("🎲 Random Creator: http://localhost:5000/orders/random-creator")
    app.run(debug=True, host='0.0.0.0', port=5000)