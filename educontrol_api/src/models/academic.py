from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date, time
import uuid

db = SQLAlchemy()

class Timetable(db.Model):
    __tablename__ = 'timetables'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    school_id = db.Column(db.String(36), db.ForeignKey('schools.id'), nullable=False)
    class_id = db.Column(db.String(36), db.ForeignKey('school_classes.id'), nullable=False)
    subject_id = db.Column(db.String(36), db.ForeignKey('subjects.id'), nullable=False)
    teacher_id = db.Column(db.String(36), db.ForeignKey('teachers.id'))
    day_of_week = db.Column(db.Integer, nullable=False)  # 1=Monday, 7=Sunday
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    room = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    school_class = db.relationship('SchoolClass', backref='timetable_entries', lazy=True)
    subject = db.relationship('Subject', backref='timetable_entries', lazy=True)
    
    def __repr__(self):
        return f'<Timetable {self.day_of_week}-{self.start_time}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'school_id': self.school_id,
            'class_id': self.class_id,
            'subject_id': self.subject_id,
            'teacher_id': self.teacher_id,
            'day_of_week': self.day_of_week,
            'start_time': self.start_time.strftime('%H:%M') if self.start_time else None,
            'end_time': self.end_time.strftime('%H:%M') if self.end_time else None,
            'room': self.room,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Attendance(db.Model):
    __tablename__ = 'attendance'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    student_id = db.Column(db.String(36), db.ForeignKey('students.id'), nullable=False)
    class_id = db.Column(db.String(36), db.ForeignKey('school_classes.id'), nullable=False)
    subject_id = db.Column(db.String(36), db.ForeignKey('subjects.id'))
    date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), nullable=False)  # present, absent, late, excused
    notes = db.Column(db.Text)
    marked_by = db.Column(db.String(36), db.ForeignKey('school_users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    school_class = db.relationship('SchoolClass', backref='attendance_records', lazy=True)
    subject = db.relationship('Subject', backref='attendance_records', lazy=True)
    marker = db.relationship('SchoolUser', backref='attendance_marked', lazy=True)
    
    __table_args__ = (db.UniqueConstraint('student_id', 'class_id', 'subject_id', 'date', name='unique_attendance'),)
    
    def __repr__(self):
        return f'<Attendance {self.student_id}-{self.date}-{self.status}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'class_id': self.class_id,
            'subject_id': self.subject_id,
            'date': self.date.isoformat() if self.date else None,
            'status': self.status,
            'notes': self.notes,
            'marked_by': self.marked_by,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Grade(db.Model):
    __tablename__ = 'grades'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    student_id = db.Column(db.String(36), db.ForeignKey('students.id'), nullable=False)
    subject_id = db.Column(db.String(36), db.ForeignKey('subjects.id'), nullable=False)
    class_id = db.Column(db.String(36), db.ForeignKey('school_classes.id'), nullable=False)
    academic_year_id = db.Column(db.String(36), db.ForeignKey('academic_years.id'), nullable=False)
    assessment_type = db.Column(db.String(50), nullable=False)  # assignment, quiz, exam, project
    assessment_name = db.Column(db.String(255), nullable=False)
    score = db.Column(db.Numeric(5, 2))
    max_score = db.Column(db.Numeric(5, 2), nullable=False)
    percentage = db.Column(db.Numeric(5, 2))
    grade = db.Column(db.String(5))
    date_assessed = db.Column(db.Date, default=date.today)
    teacher_id = db.Column(db.String(36), db.ForeignKey('teachers.id'))
    comments = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    subject = db.relationship('Subject', backref='grades', lazy=True)
    school_class = db.relationship('SchoolClass', backref='grades', lazy=True)
    academic_year = db.relationship('AcademicYear', backref='grades', lazy=True)
    
    def __repr__(self):
        return f'<Grade {self.student_id}-{self.assessment_name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'subject_id': self.subject_id,
            'class_id': self.class_id,
            'academic_year_id': self.academic_year_id,
            'assessment_type': self.assessment_type,
            'assessment_name': self.assessment_name,
            'score': float(self.score) if self.score else None,
            'max_score': float(self.max_score) if self.max_score else None,
            'percentage': float(self.percentage) if self.percentage else None,
            'grade': self.grade,
            'date_assessed': self.date_assessed.isoformat() if self.date_assessed else None,
            'teacher_id': self.teacher_id,
            'comments': self.comments,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Invoice(db.Model):
    __tablename__ = 'invoices'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    school_id = db.Column(db.String(36), db.ForeignKey('schools.id'), nullable=False)
    student_id = db.Column(db.String(36), db.ForeignKey('students.id'), nullable=False)
    invoice_number = db.Column(db.String(50), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    currency = db.Column(db.String(10), nullable=False)
    due_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, paid, overdue, cancelled
    payment_method = db.Column(db.String(50))
    payment_reference = db.Column(db.String(255))
    paid_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Invoice {self.invoice_number}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'school_id': self.school_id,
            'student_id': self.student_id,
            'invoice_number': self.invoice_number,
            'description': self.description,
            'amount': float(self.amount) if self.amount else None,
            'currency': self.currency,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'status': self.status,
            'payment_method': self.payment_method,
            'payment_reference': self.payment_reference,
            'paid_at': self.paid_at.isoformat() if self.paid_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Document(db.Model):
    __tablename__ = 'documents'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    school_id = db.Column(db.String(36), db.ForeignKey('schools.id'), nullable=False)
    uploaded_by = db.Column(db.String(36), db.ForeignKey('school_users.id'))
    student_id = db.Column(db.String(36), db.ForeignKey('students.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    file_url = db.Column(db.Text, nullable=False)
    file_type = db.Column(db.String(50))
    file_size = db.Column(db.Integer)
    category = db.Column(db.String(50))  # certificate, report, transcript, medical, other
    is_public = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    uploader = db.relationship('SchoolUser', backref='uploaded_documents', lazy=True)
    
    def __repr__(self):
        return f'<Document {self.title}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'school_id': self.school_id,
            'uploaded_by': self.uploaded_by,
            'student_id': self.student_id,
            'title': self.title,
            'description': self.description,
            'file_url': self.file_url,
            'file_type': self.file_type,
            'file_size': self.file_size,
            'category': self.category,
            'is_public': self.is_public,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Announcement(db.Model):
    __tablename__ = 'announcements'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    school_id = db.Column(db.String(36), db.ForeignKey('schools.id'), nullable=False)
    author_id = db.Column(db.String(36), db.ForeignKey('school_users.id'))
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    target_audience = db.Column(db.String(20), default='all')  # all, teachers, parents, students
    priority = db.Column(db.String(10), default='normal')  # low, normal, high, urgent
    is_published = db.Column(db.Boolean, default=False)
    published_at = db.Column(db.DateTime)
    expires_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    author = db.relationship('SchoolUser', backref='announcements', lazy=True)
    
    def __repr__(self):
        return f'<Announcement {self.title}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'school_id': self.school_id,
            'author_id': self.author_id,
            'title': self.title,
            'content': self.content,
            'target_audience': self.target_audience,
            'priority': self.priority,
            'is_published': self.is_published,
            'published_at': self.published_at.isoformat() if self.published_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Message(db.Model):
    __tablename__ = 'messages'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    school_id = db.Column(db.String(36), db.ForeignKey('schools.id'), nullable=False)
    sender_id = db.Column(db.String(36), db.ForeignKey('school_users.id'), nullable=False)
    recipient_id = db.Column(db.String(36), db.ForeignKey('school_users.id'), nullable=False)
    subject = db.Column(db.String(255))
    content = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    read_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    sender = db.relationship('SchoolUser', foreign_keys=[sender_id], backref='sent_messages', lazy=True)
    recipient = db.relationship('SchoolUser', foreign_keys=[recipient_id], backref='received_messages', lazy=True)
    
    def __repr__(self):
        return f'<Message {self.subject}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'school_id': self.school_id,
            'sender_id': self.sender_id,
            'recipient_id': self.recipient_id,
            'subject': self.subject,
            'content': self.content,
            'is_read': self.is_read,
            'read_at': self.read_at.isoformat() if self.read_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

