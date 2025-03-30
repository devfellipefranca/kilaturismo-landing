from app import db
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.email}>'

class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    telefone = db.Column(db.String(20))
    assunto = db.Column(db.String(100))
    mensagem = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Contact {self.nome}>'

class WaitlistSubscriber(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<WaitlistSubscriber {self.email}>'

class Destination(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String(255), nullable=False)
    old_price = db.Column(db.Float, nullable=False)
    price = db.Column(db.Float, nullable=False)
    is_featured = db.Column(db.Boolean, default=False)
    is_promotion = db.Column(db.Boolean, default=False)
    discount_percent = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Destination {self.name}>'
        
class SiteInfo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    site_name = db.Column(db.String(100), default="Kila Turismo")
    slogan = db.Column(db.String(255), default="Viaje bem, viaje Kila Turismo!")
    email = db.Column(db.String(100), default="peustylle01@gmail.com")
    phone1_name = db.Column(db.String(50), default="Pedro Ivo")
    phone1 = db.Column(db.String(20), default="+55 38 99850-2112")
    phone2_name = db.Column(db.String(50), default="Kila")
    phone2 = db.Column(db.String(20), default="+55 38 99121-3864")
    address = db.Column(db.String(255), default="Rua Santiago Piacenza, 596, Lourdes")
    city = db.Column(db.String(100), default="Montes Claros")
    state = db.Column(db.String(2), default="MG")
    zipcode = db.Column(db.String(10), default="39401-691")
    whatsapp = db.Column(db.String(20), default="5538998502112")
    
class ClientPhoto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    destination = db.Column(db.String(100), nullable=False)
    client_name = db.Column(db.String(100), nullable=False)
    image_url = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    is_featured = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<ClientPhoto {self.title}>'
