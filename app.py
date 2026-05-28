

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import json
import os
from datetime import datetime
import io
import heapq
from math import sqrt
import tempfile

app = Flask(__name__)
app.config['SECRET_KEY'] = 'evacuation-planner-pro-secret-key-2024'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:1234@localhost:5432/evacuation_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    buildings = db.relationship('Building', backref='owner', lazy=True)
    paths = db.relationship('EvacuationPath', backref='creator', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Building(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    floors = db.Column(db.Integer, default=1)
    width = db.Column(db.Integer, nullable=False)
    height = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    hazards = db.relationship('Hazard', backref='building', lazy=True)
    paths = db.relationship('EvacuationPath', backref='building', lazy=True)

class Hazard(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    building_id = db.Column(db.Integer, db.ForeignKey('building.id'), nullable=False)
    floor = db.Column(db.Integer, default=1)
    x = db.Column(db.Integer, nullable=False)
    y = db.Column(db.Integer, nullable=False)
    type = db.Column(db.String(50), nullable=False)
    intensity = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class EvacuationPath(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    building_id = db.Column(db.Integer, db.ForeignKey('building.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    start_x = db.Column(db.Integer, nullable=False)
    start_y = db.Column(db.Integer, nullable=False)
    end_x = db.Column(db.Integer, nullable=False)
    end_y = db.Column(db.Integer, nullable=False)
    path_data = db.Column(db.Text, nullable=False)
    total_cost = db.Column(db.Float, nullable=False)
    steps = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def get_path(self):
        return json.loads(self.path_data)

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


class AdvancedPathFinder:
    @staticmethod
    def heuristic(a, b):
        """Euclidean distance heuristic for A* algorithm"""
        return sqrt((a[0] - b[0])**2 + (a[1] - b[1])**2)

    @staticmethod
    def find_path(start, end, width, height, hazards):
        """
        Find the safest and shortest path using A* algorithm with hazard avoidance
        """
        # Create hazard cost map
        hazard_map = {}
        hazard_weights = {
            'fire': 3.0, 
            'smoke': 2.0, 
            'blocked': 100.0, 
            'water': 1.5, 
            'chemical': 5.0,
            'structural': 50.0
        }
        
        for hazard in hazards:
            hazard_map[(hazard.x, hazard.y)] = {
                'type': hazard.type,
                'intensity': hazard.intensity
            }

        # Priority queue: (f_cost, g_cost, position, path)
        open_set = []
        heapq.heappush(open_set, (0, 0, start, [start]))
        visited = set()
        g_costs = {start: 0}

        while open_set:
            current_f, current_g, current_pos, path = heapq.heappop(open_set)
            
            if current_pos in visited:
                continue
            visited.add(current_pos)

           
            if current_pos == end:
                return path, current_g

            
            for dx, dy in [(0,1), (1,0), (0,-1), (-1,0), (1,1), (1,-1), (-1,1), (-1,-1)]:
                neighbor = (current_pos[0] + dx, current_pos[1] + dy)
                
                
                if (neighbor[0] < 0 or neighbor[0] >= width or 
                    neighbor[1] < 0 or neighbor[1] >= height):
                    continue

                
                move_cost = 1.4 if (dx != 0 and dy != 0) else 1.0
                
                
                hazard_cost = 0
                if neighbor in hazard_map:
                    hazard_data = hazard_map[neighbor]
                   
                    if (hazard_data['type'] == 'blocked' or 
                        hazard_data['intensity'] >= 4 or
                        (hazard_data['type'] == 'structural' and hazard_data['intensity'] >= 2)):
                        continue
                    hazard_cost = hazard_weights.get(hazard_data['type'], 1) * hazard_data['intensity'] * 2
                
                total_cost = current_g + move_cost + hazard_cost

               
                if neighbor not in g_costs or total_cost < g_costs[neighbor]:
                    g_costs[neighbor] = total_cost
                    f_cost = total_cost + AdvancedPathFinder.heuristic(neighbor, end)
                    heapq.heappush(open_set, (f_cost, total_cost, neighbor, path + [neighbor]))

        return None, float('inf')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        if password != confirm_password:
            flash('❌ Passwords do not match', 'error')
            return render_template('register.html')
        
        if User.query.filter_by(username=username).first():
            flash('❌ Username already exists', 'error')
            return render_template('register.html')
        
        if User.query.filter_by(email=email).first():
            flash('❌ Email already registered', 'error')
            return render_template('register.html')
        
        try:
            user = User(username=username, email=email)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            flash('🎉 Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            flash('❌ Registration failed. Please try again.', 'error')
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        remember = bool(request.form.get('remember'))
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user, remember=remember)
            flash(f'🎊 Welcome back, {username}!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('dashboard'))
        else:
            flash('❌ Invalid username or password', 'error')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('👋 You have been logged out successfully.', 'info')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    buildings = Building.query.filter_by(user_id=current_user.id).all()
    paths = EvacuationPath.query.filter_by(user_id=current_user.id).all()
    
    stats = {
        'buildings_count': len(buildings),
        'paths_count': len(paths),
        'total_hazards': sum(len(building.hazards) for building in buildings),
        'recent_buildings': buildings[-3:] if buildings else []
    }
    
    return render_template('dashboard.html', **stats)

@app.route('/buildings', methods=['GET', 'POST'])
@login_required
def buildings():
    if request.method == 'POST':
        try:
            name = request.form['name']
            width = int(request.form['width'])
            height = int(request.form['height'])
            floors = int(request.form.get('floors', 1))
            
            if not name or width < 5 or height < 5:
                flash('❌ Please provide valid building parameters', 'error')
                return render_template('buildings.html')
            
            building = Building(
                name=name, 
                width=width, 
                height=height, 
                floors=floors, 
                user_id=current_user.id
            )
            db.session.add(building)
            db.session.commit()
            flash(f'🏢 Building "{name}" created successfully!', 'success')
            return redirect(url_for('buildings'))
        except Exception as e:
            db.session.rollback()
            flash('❌ Error creating building', 'error')
    
    buildings = Building.query.filter_by(user_id=current_user.id).all()
    return render_template('buildings.html', buildings=buildings)

@app.route('/building/<int:building_id>')
@login_required
def building_map(building_id):
    building = db.session.get(Building, building_id)
    if not building or building.user_id != current_user.id:
        flash('🚫 Access denied', 'error')
        return redirect(url_for('buildings'))
    
    hazards = Hazard.query.filter_by(building_id=building_id).all()
    return render_template('map.html', building=building, hazards=hazards)

@app.route('/api/hazard', methods=['POST', 'DELETE'])
@login_required
def manage_hazard():
    try:
        data = request.get_json()
        building_id = data['building_id']
        x = data['x']
        y = data['y']
        
        building = db.session.get(Building, building_id)
        if not building or building.user_id != current_user.id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        if request.method == 'POST':
            hazard_type = data.get('type', 'fire')
            intensity = data.get('intensity', 1)
        
            existing = Hazard.query.filter_by(building_id=building_id, x=x, y=y).first()
            if existing:
                existing.type = hazard_type
                existing.intensity = intensity
            else:
                hazard = Hazard(
                    building_id=building_id, 
                    x=x, 
                    y=y, 
                    type=hazard_type, 
                    intensity=intensity
                )
                db.session.add(hazard)
            
            db.session.commit()
            return jsonify({'success': True})
        
        elif request.method == 'DELETE':
            Hazard.query.filter_by(building_id=building_id, x=x, y=y).delete()
            db.session.commit()
            return jsonify({'success': True})
            
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Server error'}), 500

@app.route('/api/hazard/clear', methods=['POST'])
@login_required
def clear_hazards():
    try:
        data = request.get_json()
        building_id = data['building_id']
        
        building = db.session.get(Building, building_id)
        if not building or building.user_id != current_user.id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        Hazard.query.filter_by(building_id=building_id).delete()
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'All hazards cleared'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Server error'}), 500

@app.route('/api/path', methods=['POST'])
@login_required
def calculate_path():
    try:
        data = request.get_json()
        building_id = data['building_id']
        start_x = data['start_x']
        start_y = data['start_y']
        end_x = data['end_x']
        end_y = data['end_y']
        name = data.get('name', f'Path {datetime.now().strftime("%H:%M")}')
        
        building = db.session.get(Building, building_id)
        if not building or building.user_id != current_user.id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        hazards = Hazard.query.filter_by(building_id=building_id).all()
        path, cost = AdvancedPathFinder.find_path(
            (start_x, start_y), 
            (end_x, end_y), 
            building.width, 
            building.height, 
            hazards
        )
        
        if path:
            evacuation_path = EvacuationPath(
                building_id=building_id,
                name=name,
                start_x=start_x,
                start_y=start_y,
                end_x=end_x,
                end_y=end_y,
                path_data=json.dumps(path),
                total_cost=cost,
                steps=len(path),
                user_id=current_user.id
            )
            db.session.add(evacuation_path)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'path': path,
                'cost': cost,
                'steps': len(path),
                'path_id': evacuation_path.id
            })
        else:
            return jsonify({'success': False, 'error': '🚧 No safe path found. Hazards may be blocking all routes.'})
            
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Server error'}), 500

@app.route('/evacuation')
@login_required
def evacuation():
    paths = EvacuationPath.query.filter_by(user_id=current_user.id).order_by(EvacuationPath.created_at.desc()).all()
    return render_template('evacuation.html', paths=paths)

@app.route('/export/path/<int:path_id>')
@login_required
def export_path(path_id):
    path = db.session.get(EvacuationPath, path_id)
    if not path or path.user_id != current_user.id:
        flash('🚫 Access denied', 'error')
        return redirect(url_for('evacuation'))
    
    data = {
        'name': path.name,
        'start': [path.start_x, path.start_y],
        'end': [path.end_x, path.end_y],
        'path': json.loads(path.path_data),
        'cost': path.total_cost,
        'steps': path.steps,
        'created_at': path.created_at.isoformat(),
        'metadata': {
            'exported_at': datetime.now().isoformat(),
            'app': 'Evacuation Planner Pro'
        }
    }
    
    json_data = json.dumps(data, indent=2)
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        f.write(json_data)
        temp_path = f.name
    
    try:
        return send_file(
            temp_path,
            as_attachment=True,
            download_name=f'evacuation_path_{path.id}.json'
        )
    finally:
        os.unlink(temp_path)

@app.route('/delete/building/<int:building_id>', methods=['POST'])
@login_required
def delete_building(building_id):
    building = db.session.get(Building, building_id)
    if not building or building.user_id != current_user.id:
        flash('🚫 Access denied', 'error')
        return redirect(url_for('buildings'))
    
    try:
      
        Hazard.query.filter_by(building_id=building_id).delete()
        EvacuationPath.query.filter_by(building_id=building_id).delete()
        db.session.delete(building)
        db.session.commit()
        flash('🗑️ Building deleted successfully', 'success')
    except Exception as e:
        db.session.rollback()
        flash('❌ Error deleting building', 'error')
    
    return redirect(url_for('buildings'))

@app.route('/delete/path/<int:path_id>', methods=['POST'])
@login_required
def delete_path(path_id):
    path = db.session.get(EvacuationPath, path_id)
    if not path or path.user_id != current_user.id:
        flash('🚫 Access denied', 'error')
        return redirect(url_for('evacuation'))
    
    try:
        db.session.delete(path)
        db.session.commit()
        flash('🗑️ Path deleted successfully', 'success')
    except Exception as e:
        db.session.rollback()
        flash('❌ Error deleting path', 'error')
    
    return redirect(url_for('evacuation'))

@app.route('/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'service': 'Emergency Evacuation Planner Pro',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })


@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500

@app.errorhandler(403)
def forbidden_error(error):
    return render_template('403.html'), 403

def init_db():
    with app.app_context():
        db.create_all()
        print("✅ Database tables created successfully!")
        
       
        if not User.query.first():
            demo_user = User(username='demo', email='demo@example.com')
            demo_user.set_password('demo123')
            db.session.add(demo_user)
            db.session.commit()
            print("✅ Demo user created: username='demo', password='demo123'")

if __name__ == '__main__':
    
    init_db()
    
    print("=" * 60)
    print("🚨 EMERGENCY EVACUATION PLANNER PRO - STARTING UP")
    print("=" * 60)
    print("✅ Database initialized")
    print("✅ Pathfinding algorithm loaded")
    print("✅ Web server starting...")
    print("🌐 Access the application at: http://localhost:5000")
    print("👤 Demo credentials: username='demo', password='demo123'")
    print("=" * 60)
  
    app.run(debug=True, host='0.0.0.0', port=5000)
