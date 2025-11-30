"""
Agriculture and Forestry Management Flask Application
Uses 5 AWS Services: S3, DynamoDB, Lambda, EC2, CloudWatch
"""
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from functools import wraps
import os
import boto3
from botocore.exceptions import ClientError
from datetime import datetime

# Import custom library
from agri_lib.crop_manager import CropManager, CropAnalyzer

app = Flask(__name__)
app.config['SECRET_KEY'] = 'agriculture-forestry-secret-key-2025'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///agriculture.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'

# AWS Configuration
AWS_REGION = 'eu-north-1'
S3_BUCKET = 'agri-forestry-bucket-028061992080'
DYNAMODB_TABLE = 'agri-forestry-logs'

db = SQLAlchemy(app)

# Initialize AWS clients
def get_aws_clients():
    """Initialize AWS service clients"""
    try:
        s3_client = boto3.client('s3', region_name=AWS_REGION)
        dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)
        lambda_client = boto3.client('lambda', region_name=AWS_REGION)
        cloudwatch = boto3.client('cloudwatch', region_name=AWS_REGION)
        return s3_client, dynamodb, lambda_client, cloudwatch
    except Exception as e:
        print(f"AWS Client Error: {e}")
        return None, None, None, None

s3_client, dynamodb, lambda_client, cloudwatch = get_aws_clients()

# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    crops = db.relationship('Crop', backref='owner', lazy=True)

class Crop(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    crop_type = db.Column(db.String(50), nullable=False)  # agriculture or forestry
    area = db.Column(db.Float, nullable=False)  # in hectares
    planting_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(50), default='planted')
    image_url = db.Column(db.String(500))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login first.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# AWS Helper Functions
def upload_to_s3(file, filename):
    """Upload file to S3 bucket"""
    try:
        if s3_client:
            s3_client.upload_fileobj(file, S3_BUCKET, filename)
            return f"https://{S3_BUCKET}.s3.{AWS_REGION}.amazonaws.com/{filename}"
    except ClientError as e:
        print(f"S3 Upload Error: {e}")
    return None

def log_to_dynamodb(action, user_id, details):
    """Log actions to DynamoDB"""
    try:
        if dynamodb:
            table = dynamodb.Table(DYNAMODB_TABLE)
            table.put_item(Item={
                'log_id': f"{user_id}_{datetime.utcnow().timestamp()}",
                'action': action,
                'user_id': str(user_id),
                'details': details,
                'timestamp': str(datetime.utcnow())
            })
    except ClientError as e:
        print(f"DynamoDB Error: {e}")

def put_cloudwatch_metric(metric_name, value, unit='Count'):
    """Send custom metric to CloudWatch"""
    try:
        if cloudwatch:
            cloudwatch.put_metric_data(
                Namespace='AgriForestry',
                MetricData=[{
                    'MetricName': metric_name,
                    'Value': value,
                    'Unit': unit
                }]
            )
    except ClientError as e:
        print(f"CloudWatch Error: {e}")

def invoke_lambda_analysis(crop_data):
    """Invoke Lambda function for crop analysis"""
    try:
        if lambda_client:
            import json
            response = lambda_client.invoke(
                FunctionName='agri-forestry-analyzer',
                InvocationType='RequestResponse',
                Payload=json.dumps(crop_data)
            )
            return json.loads(response['Payload'].read())
    except ClientError as e:
        print(f"Lambda Error: {e}")
    return None

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists!', 'danger')
            return redirect(url_for('signup'))
        
        if User.query.filter_by(email=email).first():
            flash('Email already exists!', 'danger')
            return redirect(url_for('signup'))
        
        hashed_password = generate_password_hash(password)
        new_user = User(username=username, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        
        log_to_dynamodb('signup', new_user.id, f'New user registered: {username}')
        put_cloudwatch_metric('UserSignups', 1)
        
        flash('Account created successfully! Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['username'] = user.username
            
            log_to_dynamodb('login', user.id, f'User logged in: {username}')
            put_cloudwatch_metric('UserLogins', 1)
            
            flash('Logged in successfully!', 'success')
            return redirect(url_for('dashboard'))
        
        flash('Invalid username or password!', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    if 'user_id' in session:
        log_to_dynamodb('logout', session['user_id'], f"User logged out: {session['username']}")
    session.clear()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    crops = Crop.query.filter_by(user_id=session['user_id']).all()
    
    # Use custom library for analysis
    crop_manager = CropManager()
    for crop in crops:
        crop_manager.add_crop(crop.name, crop.crop_type, crop.area)
    
    analyzer = CropAnalyzer(crop_manager)
    stats = analyzer.get_statistics()
    
    return render_template('dashboard.html', crops=crops, stats=stats)

@app.route('/crops/add', methods=['GET', 'POST'])
@login_required
def add_crop():
    if request.method == 'POST':
        name = request.form['name']
        crop_type = request.form['crop_type']
        area = float(request.form['area'])
        planting_date = datetime.strptime(request.form['planting_date'], '%Y-%m-%d').date()
        
        image_url = None
        if 'image' in request.files:
            file = request.files['image']
            if file.filename:
                filename = secure_filename(f"{session['user_id']}_{datetime.utcnow().timestamp()}_{file.filename}")
                image_url = upload_to_s3(file, filename)
        
        new_crop = Crop(
            name=name,
            crop_type=crop_type,
            area=area,
            planting_date=planting_date,
            image_url=image_url,
            user_id=session['user_id']
        )
        db.session.add(new_crop)
        db.session.commit()
        
        log_to_dynamodb('add_crop', session['user_id'], f'Added crop: {name}')
        put_cloudwatch_metric('CropsAdded', 1)
        
        flash('Crop added successfully!', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('add_crop.html')

@app.route('/crops/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_crop(id):
    crop = Crop.query.get_or_404(id)
    
    if crop.user_id != session['user_id']:
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        crop.name = request.form['name']
        crop.crop_type = request.form['crop_type']
        crop.area = float(request.form['area'])
        crop.planting_date = datetime.strptime(request.form['planting_date'], '%Y-%m-%d').date()
        crop.status = request.form['status']
        
        if 'image' in request.files:
            file = request.files['image']
            if file.filename:
                filename = secure_filename(f"{session['user_id']}_{datetime.utcnow().timestamp()}_{file.filename}")
                image_url = upload_to_s3(file, filename)
                if image_url:
                    crop.image_url = image_url
        
        db.session.commit()
        
        log_to_dynamodb('edit_crop', session['user_id'], f'Edited crop: {crop.name}')
        put_cloudwatch_metric('CropsEdited', 1)
        
        flash('Crop updated successfully!', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('edit_crop.html', crop=crop)

@app.route('/crops/delete/<int:id>')
@login_required
def delete_crop(id):
    crop = Crop.query.get_or_404(id)
    
    if crop.user_id != session['user_id']:
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('dashboard'))
    
    crop_name = crop.name
    db.session.delete(crop)
    db.session.commit()
    
    log_to_dynamodb('delete_crop', session['user_id'], f'Deleted crop: {crop_name}')
    put_cloudwatch_metric('CropsDeleted', 1)
    
    flash('Crop deleted successfully!', 'success')
    return redirect(url_for('dashboard'))

@app.route('/analyze')
@login_required
def analyze():
    crops = Crop.query.filter_by(user_id=session['user_id']).all()
    
    # Use custom library for detailed analysis
    crop_manager = CropManager()
    for crop in crops:
        crop_manager.add_crop(crop.name, crop.crop_type, crop.area)
    
    analyzer = CropAnalyzer(crop_manager)
    analysis = analyzer.get_detailed_analysis()
    
    # Try Lambda analysis (will work if Lambda is deployed)
    crop_data = {'crops': [{'name': c.name, 'type': c.crop_type, 'area': c.area} for c in crops]}
    lambda_result = invoke_lambda_analysis(crop_data)
    
    return render_template('analyze.html', analysis=analysis, lambda_result=lambda_result)

# Create database tables
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(host='0.0.0.0', port=5000, debug=True)
