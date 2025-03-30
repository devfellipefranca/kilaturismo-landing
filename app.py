import os
import logging
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from datetime import datetime
import sqlite3

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "kila_turismo_secret_key")

# Configure the SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///kila_turismo.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database
db = SQLAlchemy(app)

# Initialize the login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Por favor, faça login para acessar esta página.'

# Load User model for login_manager
from models import User, Contact, WaitlistSubscriber, Destination, SiteInfo, ClientPhoto

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    """Render the home page"""
    site_info = SiteInfo.query.first()
    # If no site info exists, create default one
    if not site_info:
        site_info = SiteInfo()
        db.session.add(site_info)
        db.session.commit()
        
    # Get featured destinations
    destinations = Destination.query.filter_by(is_featured=True).limit(3).all()
    promotions = Destination.query.filter_by(is_promotion=True).limit(3).all()
    
    # Get featured client photos
    featured_photos = ClientPhoto.query.filter_by(is_featured=True).limit(6).all()
    
    return render_template('index.html', site_info=site_info, 
                          destinations=destinations, promotions=promotions,
                          featured_photos=featured_photos)
                          
@app.route('/galeria')
def gallery():
    """Render the client photo gallery page"""
    site_info = SiteInfo.query.first()
    photos = ClientPhoto.query.order_by(ClientPhoto.created_at.desc()).all()
    
    return render_template('gallery.html', site_info=site_info, photos=photos)

@app.route('/submit_contact', methods=['POST'])
def submit_contact():
    """Handle contact form submission"""
    if request.method == 'POST':
        # Get form data
        nome = request.form.get('nome')
        email = request.form.get('email')
        telefone = request.form.get('telefone')
        assunto = request.form.get('assunto')
        mensagem = request.form.get('mensagem')
        
        # Validate required fields
        if not nome or not email or not mensagem:
            flash('Por favor, preencha todos os campos obrigatórios.', 'danger')
            return redirect(url_for('index', _anchor='contato'))
        
        # Create new contact and store in database
        new_contact = Contact(
            nome=nome,
            email=email,
            telefone=telefone,
            assunto=assunto,
            mensagem=mensagem
        )
        
        db.session.add(new_contact)
        db.session.commit()
        
        # Log the contact submission
        logging.info(f"Contact form submitted by {nome} ({email})")
        
        # Show success message
        flash('Mensagem enviada com sucesso! Entraremos em contato em breve.', 'success')
        return redirect(url_for('index', _anchor='contato'))

@app.route('/subscribe_waitlist', methods=['POST'])
def subscribe_waitlist():
    """Handle waitlist form submission"""
    if request.method == 'POST':
        # Get form data
        nome = request.form.get('waitlist-nome')
        email = request.form.get('waitlist-email')
        
        # Validate required fields
        if not nome or not email:
            flash('Por favor, preencha todos os campos.', 'danger')
            return redirect(url_for('index', _anchor='waitlist'))
        
        # Check if email already exists
        existing_subscriber = WaitlistSubscriber.query.filter_by(email=email).first()
        if existing_subscriber:
            flash('Este email já está inscrito em nossa lista.', 'warning')
            return redirect(url_for('index', _anchor='waitlist'))
        
        # Add to waitlist with the database model
        new_subscriber = WaitlistSubscriber(
            nome=nome,
            email=email
        )
        
        db.session.add(new_subscriber)
        db.session.commit()
        
        # Log the waitlist subscription
        logging.info(f"Waitlist subscription by {nome} ({email})")
        
        # Show success message
        flash('Inscrição realizada com sucesso! Você receberá nossas ofertas exclusivas.', 'success')
        return redirect(url_for('index', _anchor='waitlist'))

# Admin routes
@app.route('/admin/login', methods=['GET', 'POST'])
def login():
    """Admin login page"""
    if current_user.is_authenticated:
        return redirect(url_for('admin_dashboard'))
        
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            login_user(user)
            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Email ou senha inválidos. Tente novamente.', 'danger')
    
    return render_template('admin/login.html')

@app.route('/admin/logout')
@login_required
def logout():
    """Admin logout"""
    logout_user()
    flash('Logout realizado com sucesso!', 'success')
    return redirect(url_for('index'))

@app.route('/admin')
@login_required
def admin_dashboard():
    """Admin dashboard"""
    if not current_user.is_admin:
        flash('Você não tem permissão para acessar esta página.', 'danger')
        return redirect(url_for('index'))
        
    contacts = Contact.query.order_by(Contact.created_at.desc()).all()
    waitlist = WaitlistSubscriber.query.order_by(WaitlistSubscriber.created_at.desc()).all()
    destinations = Destination.query.all()
    site_info = SiteInfo.query.first()
    
    return render_template('admin/dashboard.html', 
                          contacts=contacts, 
                          waitlist=waitlist,
                          destinations=destinations,
                          site_info=site_info)

@app.route('/admin/destinations')
@login_required
def admin_destinations():
    """Admin destinations management"""
    if not current_user.is_admin:
        flash('Você não tem permissão para acessar esta página.', 'danger')
        return redirect(url_for('index'))
        
    destinations = Destination.query.all()
    return render_template('admin/destinations.html', destinations=destinations)

@app.route('/admin/destination/add', methods=['GET', 'POST'])
@login_required
def add_destination():
    """Add a new destination"""
    if not current_user.is_admin:
        flash('Você não tem permissão para acessar esta página.', 'danger')
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        image_url = request.form.get('image_url')
        old_price = float(request.form.get('old_price'))
        price = float(request.form.get('price'))
        is_featured = bool(request.form.get('is_featured'))
        is_promotion = bool(request.form.get('is_promotion'))
        discount_percent = int(request.form.get('discount_percent', 0))
        
        destination = Destination(
            name=name,
            description=description,
            image_url=image_url,
            old_price=old_price,
            price=price,
            is_featured=is_featured,
            is_promotion=is_promotion,
            discount_percent=discount_percent
        )
        
        db.session.add(destination)
        db.session.commit()
        
        flash('Destino adicionado com sucesso!', 'success')
        return redirect(url_for('admin_destinations'))
    
    return render_template('admin/add_destination.html')

@app.route('/admin/destination/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_destination(id):
    """Edit a destination"""
    if not current_user.is_admin:
        flash('Você não tem permissão para acessar esta página.', 'danger')
        return redirect(url_for('index'))
        
    destination = Destination.query.get_or_404(id)
    
    if request.method == 'POST':
        destination.name = request.form.get('name')
        destination.description = request.form.get('description')
        destination.image_url = request.form.get('image_url')
        destination.old_price = float(request.form.get('old_price'))
        destination.price = float(request.form.get('price'))
        destination.is_featured = 'is_featured' in request.form
        destination.is_promotion = 'is_promotion' in request.form
        destination.discount_percent = int(request.form.get('discount_percent', 0))
        
        db.session.commit()
        
        flash('Destino atualizado com sucesso!', 'success')
        return redirect(url_for('admin_destinations'))
    
    return render_template('admin/edit_destination.html', destination=destination)

@app.route('/admin/destination/delete/<int:id>')
@login_required
def delete_destination(id):
    """Delete a destination"""
    if not current_user.is_admin:
        flash('Você não tem permissão para acessar esta página.', 'danger')
        return redirect(url_for('index'))
        
    destination = Destination.query.get_or_404(id)
    db.session.delete(destination)
    db.session.commit()
    
    flash('Destino excluído com sucesso!', 'success')
    return redirect(url_for('admin_destinations'))

@app.route('/admin/site-info', methods=['GET', 'POST'])
@login_required
def edit_site_info():
    """Edit site information"""
    if not current_user.is_admin:
        flash('Você não tem permissão para acessar esta página.', 'danger')
        return redirect(url_for('index'))
        
    site_info = SiteInfo.query.first()
    if not site_info:
        site_info = SiteInfo()
        db.session.add(site_info)
        db.session.commit()
    
    if request.method == 'POST':
        site_info.site_name = request.form.get('site_name')
        site_info.slogan = request.form.get('slogan')
        site_info.email = request.form.get('email')
        site_info.phone1_name = request.form.get('phone1_name')
        site_info.phone1 = request.form.get('phone1')
        site_info.phone2_name = request.form.get('phone2_name')
        site_info.phone2 = request.form.get('phone2')
        site_info.address = request.form.get('address')
        site_info.city = request.form.get('city')
        site_info.state = request.form.get('state')
        site_info.zipcode = request.form.get('zipcode')
        site_info.whatsapp = request.form.get('whatsapp')
        
        db.session.commit()
        
        flash('Informações do site atualizadas com sucesso!', 'success')
        return redirect(url_for('admin_dashboard'))
    
    return render_template('admin/edit_site_info.html', site_info=site_info)

@app.route('/admin/client-photos')
@login_required
def admin_client_photos():
    """Admin client photos management"""
    if not current_user.is_admin:
        flash('Você não tem permissão para acessar esta página.', 'danger')
        return redirect(url_for('index'))
        
    photos = ClientPhoto.query.order_by(ClientPhoto.created_at.desc()).all()
    return render_template('admin/client_photos.html', photos=photos)

@app.route('/admin/client-photo/add', methods=['GET', 'POST'])
@login_required
def add_client_photo():
    """Add a new client photo"""
    if not current_user.is_admin:
        flash('Você não tem permissão para acessar esta página.', 'danger')
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        title = request.form.get('title')
        destination = request.form.get('destination')
        client_name = request.form.get('client_name')
        image_url = request.form.get('image_url')
        description = request.form.get('description')
        is_featured = 'is_featured' in request.form
        
        photo = ClientPhoto(
            title=title,
            destination=destination,
            client_name=client_name,
            image_url=image_url,
            description=description,
            is_featured=is_featured
        )
        
        db.session.add(photo)
        db.session.commit()
        
        flash('Foto do cliente adicionada com sucesso!', 'success')
        return redirect(url_for('admin_client_photos'))
    
    return render_template('admin/add_client_photo.html')

@app.route('/admin/client-photo/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_client_photo(id):
    """Edit a client photo"""
    if not current_user.is_admin:
        flash('Você não tem permissão para acessar esta página.', 'danger')
        return redirect(url_for('index'))
        
    photo = ClientPhoto.query.get_or_404(id)
    
    if request.method == 'POST':
        photo.title = request.form.get('title')
        photo.destination = request.form.get('destination')
        photo.client_name = request.form.get('client_name')
        photo.image_url = request.form.get('image_url')
        photo.description = request.form.get('description')
        photo.is_featured = 'is_featured' in request.form
        
        db.session.commit()
        
        flash('Foto do cliente atualizada com sucesso!', 'success')
        return redirect(url_for('admin_client_photos'))
    
    return render_template('admin/edit_client_photo.html', photo=photo)

@app.route('/admin/client-photo/delete/<int:id>')
@login_required
def delete_client_photo(id):
    """Delete a client photo"""
    if not current_user.is_admin:
        flash('Você não tem permissão para acessar esta página.', 'danger')
        return redirect(url_for('index'))
        
    photo = ClientPhoto.query.get_or_404(id)
    db.session.delete(photo)
    db.session.commit()
    
    flash('Foto do cliente excluída com sucesso!', 'success')
    return redirect(url_for('admin_client_photos'))

@app.route('/whatsapp')
def redirect_to_whatsapp():
    """Redirect to WhatsApp"""
    site_info = SiteInfo.query.first()
    if site_info and site_info.whatsapp:
        whatsapp_number = site_info.whatsapp
        return redirect(f"https://wa.me/{whatsapp_number}")
    return redirect(url_for('index'))

@app.errorhandler(404)
def page_not_found(e):
    """Handle 404 errors"""
    return render_template('index.html'), 404

# Create admin user and site info function
def create_admin_user():
    """Create admin user if not exists"""
    admin_user = User.query.filter_by(email='peustylle01@gmail.com').first()
    if not admin_user:
        admin_user = User(
            email='peustylle01@gmail.com',
            name='Pedro Ivo',
            is_admin=True
        )
        admin_user.set_password('pedro123')
        db.session.add(admin_user)
        
        # Create initial site info
        site_info = SiteInfo()
        db.session.add(site_info)
        
        db.session.commit()
        logging.info("Admin user and site info created successfully")

# Create tables before first request
with app.app_context():
    db.create_all()
    create_admin_user()
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
