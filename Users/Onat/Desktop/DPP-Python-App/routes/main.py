from flask import Blueprint, render_template, jsonify

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def dashboard():
    """Main dashboard page"""
    # Import models inside function to avoid circular imports
    from models.dashboard import DashboardStats, DPPModule
    from models.garment import Garment
    from models.orders import Order
    
    # Get dashboard stats
    stats = DashboardStats.query.first()
    if not stats:
        stats = DashboardStats(active_dpps=15, manufacturing_processes=7, 
                             total_co2_monthly=156.8, monthly_operations=1200000)
        from app import db
        db.session.add(stats)
        db.session.commit()
    
    # Get DPP modules
    modules = DPPModule.query.all()
    
    # Get recent garments and orders
    recent_garments = Garment.query.order_by(Garment.created_date.desc()).limit(5).all()
    recent_orders = Order.query.order_by(Order.created_date.desc()).limit(5).all()
    
    return render_template('dashboard.html', 
                         stats=stats, 
                         modules=modules,
                         recent_garments=recent_garments,
                         recent_orders=recent_orders)

@main_bp.route('/api/stats')
def api_stats():
    """Get dashboard statistics"""
    try:
        # Import models inside function to avoid circular imports
        from models.dashboard import DashboardStats
        from models.garment import Garment
        from models.orders import Order
        
        stats = DashboardStats.query.first()
        total_garments = Garment.query.count()
        total_orders = Order.query.count()
        
        return jsonify({
            'success': True,
            'stats': stats.to_dict() if stats else {},
            'total_garments': total_garments,
            'total_orders': total_orders
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def create_default_modules():
    """Create default DPP modules"""
    # Import inside function to avoid circular imports
    from models.dashboard import DPPModule
    from app import db
    
    default_modules = [
        {"name": "Fibre DPP", "description": "Fiber traceability and sustainability", "icon": "fas fa-seedling", "url": "/fibre", "color": "success"},
        {"name": "Yarn DPP", "description": "Yarn production and quality tracking", "icon": "fas fa-thread", "url": "/yarn", "color": "info"},
        {"name": "Fabric DPP", "description": "Fabric manufacturing and properties", "icon": "fas fa-cut", "url": "/fabric", "color": "warning"},
        {"name": "Garment DPP", "description": "Complete garment lifecycle tracking", "icon": "fas fa-tshirt", "url": "/garment", "color": "primary"},
        {"name": "Chemical & Dyes", "description": "Chemical usage and safety tracking", "icon": "fas fa-flask", "url": "/chemicals", "color": "danger"},
        {"name": "Energy & Utilities", "description": "Energy consumption monitoring", "icon": "fas fa-bolt", "url": "/energy", "color": "warning"},
        {"name": "Finishing", "description": "Finishing processes and quality", "icon": "fas fa-magic", "url": "/finishing", "color": "info"},
        {"name": "IT DPP", "description": "IT infrastructure and digital tracking", "icon": "fas fa-laptop", "url": "/it", "color": "dark"},
        {"name": "Logistics", "description": "Supply chain and logistics management", "icon": "fas fa-truck", "url": "/logistics", "color": "success"},
        {"name": "Office DPP", "description": "Office operations and administration", "icon": "fas fa-building", "url": "/office", "color": "secondary"},
        {"name": "Office Supplies", "description": "Office supplies and waste management", "icon": "fas fa-paperclip", "url": "/supplies", "color": "info"},
        {"name": "Order Delivery", "description": "Order processing and delivery tracking", "icon": "fas fa-shipping-fast", "url": "/orders", "color": "primary"},
        {"name": "Packaging", "description": "Packaging materials and sustainability", "icon": "fas fa-box", "url": "/packaging", "color": "warning"},
        {"name": "Retail Distribution", "description": "Retail and distribution management", "icon": "fas fa-store", "url": "/retail", "color": "success"},
        {"name": "Transport DPP", "description": "Transportation and carbon footprint", "icon": "fas fa-car", "url": "/transport", "color": "danger"}
    ]
    
    for module_data in default_modules:
        module = DPPModule(**module_data)
        db.session.add(module)
    
    db.session.commit()