from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import uuid

db = SQLAlchemy()

class School(db.Model):
    __tablename__ = 'schools'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(255), nullable=False)
    address = db.Column(db.Text)
    phone = db.Column(db.String(50))
    email = db.Column(db.String(255))
    website = db.Column(db.String(255))
    logo_url = db.Column(db.Text)
    timezone = db.Column(db.String(100), default='UTC')
    currency = db.Column(db.String(10), default='USD')
    locale = db.Column(db.String(10), default='en')
    subscription_plan = db.Column(db.String(50), default='basic')
    subscription_status = db.Column(db.String(20), default='active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    users = db.relationship('SchoolUser', backref='school', lazy=True, cascade='all, delete-orphan')
    academic_years = db.relationship('AcademicYear', backref='school', lazy=True, cascade='all, delete-orphan')
    classes = db.relationship('SchoolClass', backref='school', lazy=True, cascade='all, delete-orphan')
    subjects = db.relationship('Subject', backref='school', lazy=True, cascade='all, delete-orphan')
    students = db.relationship('Student', backref='school', lazy=True, cascade='all, delete-orphan')
    teachers = db.relationship('Teacher', backref='school', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<School {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'address': self.address,
            'phone': self.phone,
            'email': self.email,
            'website': self.website,
            'logo_url': self.logo_url,
            'timezone': self.timezone,
            'currency': self.currency,
            'locale': self.locale,
            'subscription_plan': self.subscription_plan,
            'subscription_status': self.subscription_status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class SchoolUser(db.Model):
    __tablename__ = 'school_users'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    school_id = db.Column(db.String(36), db.ForeignKey('schools.id'), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # admin, teacher, parent, student
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(50))
    avatar_url = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<SchoolUser {self.first_name} {self.last_name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'school_id': self.school_id,
            'role': self.role,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'phone': self.phone,
            'avatar_url': self.avatar_url,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class AcademicYear(db.Model):
    __tablename__ = 'academic_years'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    school_id = db.Column(db.String(36), db.ForeignKey('schools.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    is_current = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    classes = db.relationship('SchoolClass', backref='academic_year', lazy=True)
    
    def __repr__(self):
        return f'<AcademicYear {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'school_id': self.school_id,
            'name': self.name,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'is_current': self.is_current,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class SchoolClass(db.Model):
    __tablename__ = 'school_classes'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    school_id = db.Column(db.String(36), db.ForeignKey('schools.id'), nullable=False)
    academic_year_id = db.Column(db.String(36), db.ForeignKey('academic_years.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    capacity = db.Column(db.Integer, default=30)
    class_teacher_id = db.Column(db.String(36), db.ForeignKey('school_users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    students = db.relationship('Student', backref='school_class', lazy=True)
    
    def __repr__(self):
        return f'<SchoolClass {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'school_id': self.school_id,
            'academic_year_id': self.academic_year_id,
            'name': self.name,
            'description': self.description,
            'capacity': self.capacity,
            'class_teacher_id': self.class_teacher_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Subject(db.Model):
    __tablename__ = 'subjects'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    school_id = db.Column(db.String(36), db.ForeignKey('schools.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(20))
    description = db.Column(db.Text)
    color = db.Column(db.String(7), default='#3B82F6')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Subject {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'school_id': self.school_id,
            'name': self.name,
            'code': self.code,
            'description': self.description,
            'color': self.color,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

