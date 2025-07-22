from flask import Blueprint, jsonify, request
from src.models.academic import Timetable, Attendance, Grade, Invoice, Document, Announcement, Message, db
from src.models.student import Student
from datetime import datetime, time

academic_bp = Blueprint('academic', __name__)

# Timetable endpoints
@academic_bp.route('/schools/<school_id>/timetables', methods=['GET'])
def get_timetables(school_id):
    """Get all timetables for a school"""
    timetables = Timetable.query.filter_by(school_id=school_id).all()
    return jsonify([timetable.to_dict() for timetable in timetables])

@academic_bp.route('/schools/<school_id>/timetables', methods=['POST'])
def create_timetable(school_id):
    """Create a new timetable entry"""
    data = request.json
    
    # Validate required fields
    required_fields = ['class_id', 'subject_id', 'day_of_week', 'start_time', 'end_time']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    try:
        start_time = datetime.strptime(data['start_time'], '%H:%M').time()
        end_time = datetime.strptime(data['end_time'], '%H:%M').time()
    except ValueError:
        return jsonify({'error': 'Invalid time format. Use HH:MM'}), 400
    
    if not (1 <= data['day_of_week'] <= 7):
        return jsonify({'error': 'day_of_week must be between 1 (Monday) and 7 (Sunday)'}), 400
    
    timetable = Timetable(
        school_id=school_id,
        class_id=data['class_id'],
        subject_id=data['subject_id'],
        teacher_id=data.get('teacher_id'),
        day_of_week=data['day_of_week'],
        start_time=start_time,
        end_time=end_time,
        room=data.get('room')
    )
    
    db.session.add(timetable)
    db.session.commit()
    
    return jsonify(timetable.to_dict()), 201

@academic_bp.route('/schools/<school_id>/timetables/<timetable_id>', methods=['PUT'])
def update_timetable(school_id, timetable_id):
    """Update a timetable entry"""
    timetable = Timetable.query.filter_by(id=timetable_id, school_id=school_id).first_or_404()
    data = request.json
    
    # Update fields
    updatable_fields = ['class_id', 'subject_id', 'teacher_id', 'day_of_week', 'start_time', 'end_time', 'room']
    
    for field in updatable_fields:
        if field in data:
            if field in ['start_time', 'end_time']:
                try:
                    setattr(timetable, field, datetime.strptime(data[field], '%H:%M').time())
                except ValueError:
                    return jsonify({'error': f'Invalid time format for {field}. Use HH:MM'}), 400
            elif field == 'day_of_week':
                if not (1 <= data[field] <= 7):
                    return jsonify({'error': 'day_of_week must be between 1 (Monday) and 7 (Sunday)'}), 400
                setattr(timetable, field, data[field])
            else:
                setattr(timetable, field, data[field])
    
    timetable.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify(timetable.to_dict())

@academic_bp.route('/schools/<school_id>/timetables/<timetable_id>', methods=['DELETE'])
def delete_timetable(school_id, timetable_id):
    """Delete a timetable entry"""
    timetable = Timetable.query.filter_by(id=timetable_id, school_id=school_id).first_or_404()
    db.session.delete(timetable)
    db.session.commit()
    return '', 204

# Attendance endpoints
@academic_bp.route('/schools/<school_id>/attendance', methods=['GET'])
def get_attendance(school_id):
    """Get attendance records for a school"""
    # Filter by date range if provided
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    student_id = request.args.get('student_id')
    class_id = request.args.get('class_id')
    
    query = db.session.query(Attendance).join(Student).filter(Student.school_id == school_id)
    
    if start_date:
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            query = query.filter(Attendance.date >= start_date)
        except ValueError:
            return jsonify({'error': 'Invalid start_date format. Use YYYY-MM-DD'}), 400
    
    if end_date:
        try:
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            query = query.filter(Attendance.date <= end_date)
        except ValueError:
            return jsonify({'error': 'Invalid end_date format. Use YYYY-MM-DD'}), 400
    
    if student_id:
        query = query.filter(Attendance.student_id == student_id)
    
    if class_id:
        query = query.filter(Attendance.class_id == class_id)
    
    attendance_records = query.all()
    return jsonify([record.to_dict() for record in attendance_records])

@academic_bp.route('/schools/<school_id>/attendance', methods=['POST'])
def create_attendance(school_id):
    """Create a new attendance record"""
    data = request.json
    
    # Validate required fields
    required_fields = ['student_id', 'class_id', 'date', 'status']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    # Validate student belongs to school
    student = Student.query.filter_by(id=data['student_id'], school_id=school_id).first()
    if not student:
        return jsonify({'error': 'Student not found in this school'}), 400
    
    try:
        attendance_date = datetime.strptime(data['date'], '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
    
    valid_statuses = ['present', 'absent', 'late', 'excused']
    if data['status'] not in valid_statuses:
        return jsonify({'error': f'Invalid status. Must be one of: {valid_statuses}'}), 400
    
    attendance = Attendance(
        student_id=data['student_id'],
        class_id=data['class_id'],
        subject_id=data.get('subject_id'),
        date=attendance_date,
        status=data['status'],
        notes=data.get('notes'),
        marked_by=data.get('marked_by')
    )
    
    db.session.add(attendance)
    db.session.commit()
    
    return jsonify(attendance.to_dict()), 201

# Grades endpoints
@academic_bp.route('/schools/<school_id>/grades', methods=['GET'])
def get_grades(school_id):
    """Get grades for a school"""
    student_id = request.args.get('student_id')
    subject_id = request.args.get('subject_id')
    class_id = request.args.get('class_id')
    academic_year_id = request.args.get('academic_year_id')
    
    query = db.session.query(Grade).join(Student).filter(Student.school_id == school_id)
    
    if student_id:
        query = query.filter(Grade.student_id == student_id)
    if subject_id:
        query = query.filter(Grade.subject_id == subject_id)
    if class_id:
        query = query.filter(Grade.class_id == class_id)
    if academic_year_id:
        query = query.filter(Grade.academic_year_id == academic_year_id)
    
    grades = query.all()
    return jsonify([grade.to_dict() for grade in grades])

@academic_bp.route('/schools/<school_id>/grades', methods=['POST'])
def create_grade(school_id):
    """Create a new grade"""
    data = request.json
    
    # Validate required fields
    required_fields = ['student_id', 'subject_id', 'class_id', 'academic_year_id', 
                      'assessment_type', 'assessment_name', 'max_score']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    # Validate student belongs to school
    student = Student.query.filter_by(id=data['student_id'], school_id=school_id).first()
    if not student:
        return jsonify({'error': 'Student not found in this school'}), 400
    
    try:
        date_assessed = None
        if data.get('date_assessed'):
            date_assessed = datetime.strptime(data['date_assessed'], '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
    
    valid_assessment_types = ['assignment', 'quiz', 'exam', 'project']
    if data['assessment_type'] not in valid_assessment_types:
        return jsonify({'error': f'Invalid assessment_type. Must be one of: {valid_assessment_types}'}), 400
    
    # Calculate percentage if score is provided
    percentage = None
    if data.get('score') and data['max_score']:
        percentage = (float(data['score']) / float(data['max_score'])) * 100
    
    grade = Grade(
        student_id=data['student_id'],
        subject_id=data['subject_id'],
        class_id=data['class_id'],
        academic_year_id=data['academic_year_id'],
        assessment_type=data['assessment_type'],
        assessment_name=data['assessment_name'],
        score=data.get('score'),
        max_score=data['max_score'],
        percentage=percentage,
        grade=data.get('grade'),
        date_assessed=date_assessed,
        teacher_id=data.get('teacher_id'),
        comments=data.get('comments')
    )
    
    db.session.add(grade)
    db.session.commit()
    
    return jsonify(grade.to_dict()), 201

# Invoice endpoints
@academic_bp.route('/schools/<school_id>/invoices', methods=['GET'])
def get_invoices(school_id):
    """Get invoices for a school"""
    student_id = request.args.get('student_id')
    status = request.args.get('status')
    
    query = Invoice.query.filter_by(school_id=school_id)
    
    if student_id:
        query = query.filter_by(student_id=student_id)
    if status:
        query = query.filter_by(status=status)
    
    invoices = query.all()
    return jsonify([invoice.to_dict() for invoice in invoices])

@academic_bp.route('/schools/<school_id>/invoices', methods=['POST'])
def create_invoice(school_id):
    """Create a new invoice"""
    data = request.json
    
    # Validate required fields
    required_fields = ['student_id', 'invoice_number', 'description', 'amount', 'currency', 'due_date']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    # Validate student belongs to school
    student = Student.query.filter_by(id=data['student_id'], school_id=school_id).first()
    if not student:
        return jsonify({'error': 'Student not found in this school'}), 400
    
    try:
        due_date = datetime.strptime(data['due_date'], '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'error': 'Invalid due_date format. Use YYYY-MM-DD'}), 400
    
    invoice = Invoice(
        school_id=school_id,
        student_id=data['student_id'],
        invoice_number=data['invoice_number'],
        description=data['description'],
        amount=data['amount'],
        currency=data['currency'],
        due_date=due_date,
        status=data.get('status', 'pending')
    )
    
    db.session.add(invoice)
    db.session.commit()
    
    return jsonify(invoice.to_dict()), 201

# Announcements endpoints
@academic_bp.route('/schools/<school_id>/announcements', methods=['GET'])
def get_announcements(school_id):
    """Get announcements for a school"""
    target_audience = request.args.get('target_audience')
    is_published = request.args.get('is_published')
    
    query = Announcement.query.filter_by(school_id=school_id)
    
    if target_audience:
        query = query.filter_by(target_audience=target_audience)
    if is_published is not None:
        query = query.filter_by(is_published=is_published.lower() == 'true')
    
    announcements = query.order_by(Announcement.created_at.desc()).all()
    return jsonify([announcement.to_dict() for announcement in announcements])

@academic_bp.route('/schools/<school_id>/announcements', methods=['POST'])
def create_announcement(school_id):
    """Create a new announcement"""
    data = request.json
    
    # Validate required fields
    required_fields = ['title', 'content']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    valid_audiences = ['all', 'teachers', 'parents', 'students']
    target_audience = data.get('target_audience', 'all')
    if target_audience not in valid_audiences:
        return jsonify({'error': f'Invalid target_audience. Must be one of: {valid_audiences}'}), 400
    
    valid_priorities = ['low', 'normal', 'high', 'urgent']
    priority = data.get('priority', 'normal')
    if priority not in valid_priorities:
        return jsonify({'error': f'Invalid priority. Must be one of: {valid_priorities}'}), 400
    
    announcement = Announcement(
        school_id=school_id,
        author_id=data.get('author_id'),
        title=data['title'],
        content=data['content'],
        target_audience=target_audience,
        priority=priority,
        is_published=data.get('is_published', False)
    )
    
    if data.get('published_at'):
        try:
            announcement.published_at = datetime.fromisoformat(data['published_at'])
        except ValueError:
            return jsonify({'error': 'Invalid published_at format. Use ISO format'}), 400
    
    if data.get('expires_at'):
        try:
            announcement.expires_at = datetime.fromisoformat(data['expires_at'])
        except ValueError:
            return jsonify({'error': 'Invalid expires_at format. Use ISO format'}), 400
    
    db.session.add(announcement)
    db.session.commit()
    
    return jsonify(announcement.to_dict()), 201

