from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date
import uuid

db = SQLAlchemy()

class Student(db.Model):
    __tablename__ = 'students'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('school_users.id'), nullable=False)
    school_id = db.Column(db.String(36), db.ForeignKey('schools.id'), nullable=False)
    class_id = db.Column(db.String(36), db.ForeignKey('school_classes.id'))
    student_id = db.Column(db.String(50), nullable=False, unique=True)
    date_of_birth = db.Column(db.Date)
    gender = db.Column(db.String(10))
    address = db.Column(db.Text)
    emergency_contact_name = db.Column(db.String(255))
    emergency_contact_phone = db.Column(db.String(50))
    enrollment_date = db.Column(db.Date, default=date.today)
    status = db.Column(db.String(20), default='active')  # active, inactive, graduated, transferred
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('SchoolUser', backref='student_profile', lazy=True)
    parent_relationships = db.relationship('ParentStudentRelationship', backref='student', lazy=True, cascade='all, delete-orphan')
    attendance_records = db.relationship('Attendance', backref='student', lazy=True, cascade='all, delete-orphan')
    grades = db.relationship('Grade', backref='student', lazy=True, cascade='all, delete-orphan')
    invoices = db.relationship('Invoice', backref='student', lazy=True, cascade='all, delete-orphan')
    documents = db.relationship('Document', backref='student', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Student {self.student_id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'school_id': self.school_id,
            'class_id': self.class_id,
            'student_id': self.student_id,
            'date_of_birth': self.date_of_birth.isoformat() if self.date_of_birth else None,
            'gender': self.gender,
            'address': self.address,
            'emergency_contact_name': self.emergency_contact_name,
            'emergency_contact_phone': self.emergency_contact_phone,
            'enrollment_date': self.enrollment_date.isoformat() if self.enrollment_date else None,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Teacher(db.Model):
    __tablename__ = 'teachers'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('school_users.id'), nullable=False)
    school_id = db.Column(db.String(36), db.ForeignKey('schools.id'), nullable=False)
    employee_id = db.Column(db.String(50), nullable=False, unique=True)
    qualification = db.Column(db.Text)
    specialization = db.Column(db.Text)
    hire_date = db.Column(db.Date, default=date.today)
    salary = db.Column(db.Numeric(10, 2))
    status = db.Column(db.String(20), default='active')  # active, inactive, terminated
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('SchoolUser', backref='teacher_profile', lazy=True)
    class_subjects = db.relationship('ClassSubject', backref='teacher', lazy=True)
    timetables = db.relationship('Timetable', backref='teacher', lazy=True)
    grades_given = db.relationship('Grade', backref='teacher', lazy=True)
    
    def __repr__(self):
        return f'<Teacher {self.employee_id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'school_id': self.school_id,
            'employee_id': self.employee_id,
            'qualification': self.qualification,
            'specialization': self.specialization,
            'hire_date': self.hire_date.isoformat() if self.hire_date else None,
            'salary': float(self.salary) if self.salary else None,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class ParentStudentRelationship(db.Model):
    __tablename__ = 'parent_student_relationships'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    parent_id = db.Column(db.String(36), db.ForeignKey('school_users.id'), nullable=False)
    student_id = db.Column(db.String(36), db.ForeignKey('students.id'), nullable=False)
    relationship = db.Column(db.String(50), nullable=False)  # father, mother, guardian, etc.
    is_primary = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    parent = db.relationship('SchoolUser', backref='student_relationships', lazy=True)
    
    __table_args__ = (db.UniqueConstraint('parent_id', 'student_id', name='unique_parent_student'),)
    
    def __repr__(self):
        return f'<ParentStudentRelationship {self.relationship}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'parent_id': self.parent_id,
            'student_id': self.student_id,
            'relationship': self.relationship,
            'is_primary': self.is_primary,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class ClassSubject(db.Model):
    __tablename__ = 'class_subjects'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    class_id = db.Column(db.String(36), db.ForeignKey('school_classes.id'), nullable=False)
    subject_id = db.Column(db.String(36), db.ForeignKey('subjects.id'), nullable=False)
    teacher_id = db.Column(db.String(36), db.ForeignKey('teachers.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    school_class = db.relationship('SchoolClass', backref='class_subjects', lazy=True)
    subject = db.relationship('Subject', backref='class_assignments', lazy=True)
    
    __table_args__ = (db.UniqueConstraint('class_id', 'subject_id', name='unique_class_subject'),)
    
    def __repr__(self):
        return f'<ClassSubject {self.class_id}-{self.subject_id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'class_id': self.class_id,
            'subject_id': self.subject_id,
            'teacher_id': self.teacher_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

