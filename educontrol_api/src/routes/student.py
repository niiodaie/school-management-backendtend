from flask import Blueprint, jsonify, request
from src.models.student import Student, Teacher, ParentStudentRelationship, ClassSubject, db
from src.models.school import SchoolUser
from datetime import datetime

student_bp = Blueprint('student', __name__)

# Student endpoints
@student_bp.route('/schools/<school_id>/students', methods=['GET'])
def get_students(school_id):
    """Get all students in a school"""
    students = Student.query.filter_by(school_id=school_id).all()
    return jsonify([student.to_dict() for student in students])

@student_bp.route('/schools/<school_id>/students', methods=['POST'])
def create_student(school_id):
    """Create a new student"""
    data = request.json
    
    # Validate required fields
    required_fields = ['user_id', 'student_id']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    # Validate that user exists and is a student
    user = SchoolUser.query.filter_by(id=data['user_id'], school_id=school_id, role='student').first()
    if not user:
        return jsonify({'error': 'User not found or not a student'}), 400
    
    try:
        date_of_birth = None
        if data.get('date_of_birth'):
            date_of_birth = datetime.strptime(data['date_of_birth'], '%Y-%m-%d').date()
        
        enrollment_date = None
        if data.get('enrollment_date'):
            enrollment_date = datetime.strptime(data['enrollment_date'], '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
    
    student = Student(
        user_id=data['user_id'],
        school_id=school_id,
        class_id=data.get('class_id'),
        student_id=data['student_id'],
        date_of_birth=date_of_birth,
        gender=data.get('gender'),
        address=data.get('address'),
        emergency_contact_name=data.get('emergency_contact_name'),
        emergency_contact_phone=data.get('emergency_contact_phone'),
        enrollment_date=enrollment_date,
        status=data.get('status', 'active')
    )
    
    db.session.add(student)
    db.session.commit()
    
    return jsonify(student.to_dict()), 201

@student_bp.route('/schools/<school_id>/students/<student_id>', methods=['GET'])
def get_student(school_id, student_id):
    """Get a specific student"""
    student = Student.query.filter_by(id=student_id, school_id=school_id).first_or_404()
    return jsonify(student.to_dict())

@student_bp.route('/schools/<school_id>/students/<student_id>', methods=['PUT'])
def update_student(school_id, student_id):
    """Update a student"""
    student = Student.query.filter_by(id=student_id, school_id=school_id).first_or_404()
    data = request.json
    
    # Update fields
    updatable_fields = ['class_id', 'date_of_birth', 'gender', 'address', 
                       'emergency_contact_name', 'emergency_contact_phone', 
                       'enrollment_date', 'status']
    
    for field in updatable_fields:
        if field in data:
            if field in ['date_of_birth', 'enrollment_date'] and data[field]:
                try:
                    setattr(student, field, datetime.strptime(data[field], '%Y-%m-%d').date())
                except ValueError:
                    return jsonify({'error': f'Invalid date format for {field}. Use YYYY-MM-DD'}), 400
            else:
                setattr(student, field, data[field])
    
    student.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify(student.to_dict())

@student_bp.route('/schools/<school_id>/students/<student_id>', methods=['DELETE'])
def delete_student(school_id, student_id):
    """Delete a student"""
    student = Student.query.filter_by(id=student_id, school_id=school_id).first_or_404()
    db.session.delete(student)
    db.session.commit()
    return '', 204

# Teacher endpoints
@student_bp.route('/schools/<school_id>/teachers', methods=['GET'])
def get_teachers(school_id):
    """Get all teachers in a school"""
    teachers = Teacher.query.filter_by(school_id=school_id).all()
    return jsonify([teacher.to_dict() for teacher in teachers])

@student_bp.route('/schools/<school_id>/teachers', methods=['POST'])
def create_teacher(school_id):
    """Create a new teacher"""
    data = request.json
    
    # Validate required fields
    required_fields = ['user_id', 'employee_id']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    # Validate that user exists and is a teacher
    user = SchoolUser.query.filter_by(id=data['user_id'], school_id=school_id, role='teacher').first()
    if not user:
        return jsonify({'error': 'User not found or not a teacher'}), 400
    
    try:
        hire_date = None
        if data.get('hire_date'):
            hire_date = datetime.strptime(data['hire_date'], '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
    
    teacher = Teacher(
        user_id=data['user_id'],
        school_id=school_id,
        employee_id=data['employee_id'],
        qualification=data.get('qualification'),
        specialization=data.get('specialization'),
        hire_date=hire_date,
        salary=data.get('salary'),
        status=data.get('status', 'active')
    )
    
    db.session.add(teacher)
    db.session.commit()
    
    return jsonify(teacher.to_dict()), 201

@student_bp.route('/schools/<school_id>/teachers/<teacher_id>', methods=['GET'])
def get_teacher(school_id, teacher_id):
    """Get a specific teacher"""
    teacher = Teacher.query.filter_by(id=teacher_id, school_id=school_id).first_or_404()
    return jsonify(teacher.to_dict())

@student_bp.route('/schools/<school_id>/teachers/<teacher_id>', methods=['PUT'])
def update_teacher(school_id, teacher_id):
    """Update a teacher"""
    teacher = Teacher.query.filter_by(id=teacher_id, school_id=school_id).first_or_404()
    data = request.json
    
    # Update fields
    updatable_fields = ['qualification', 'specialization', 'hire_date', 'salary', 'status']
    
    for field in updatable_fields:
        if field in data:
            if field == 'hire_date' and data[field]:
                try:
                    setattr(teacher, field, datetime.strptime(data[field], '%Y-%m-%d').date())
                except ValueError:
                    return jsonify({'error': f'Invalid date format for {field}. Use YYYY-MM-DD'}), 400
            else:
                setattr(teacher, field, data[field])
    
    teacher.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify(teacher.to_dict())

@student_bp.route('/schools/<school_id>/teachers/<teacher_id>', methods=['DELETE'])
def delete_teacher(school_id, teacher_id):
    """Delete a teacher"""
    teacher = Teacher.query.filter_by(id=teacher_id, school_id=school_id).first_or_404()
    db.session.delete(teacher)
    db.session.commit()
    return '', 204

# Parent-Student relationship endpoints
@student_bp.route('/schools/<school_id>/parent-student-relationships', methods=['GET'])
def get_parent_student_relationships(school_id):
    """Get all parent-student relationships in a school"""
    relationships = db.session.query(ParentStudentRelationship).join(Student).filter(
        Student.school_id == school_id
    ).all()
    return jsonify([rel.to_dict() for rel in relationships])

@student_bp.route('/schools/<school_id>/parent-student-relationships', methods=['POST'])
def create_parent_student_relationship(school_id):
    """Create a new parent-student relationship"""
    data = request.json
    
    # Validate required fields
    required_fields = ['parent_id', 'student_id', 'relationship']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    # Validate that parent exists and is a parent
    parent = SchoolUser.query.filter_by(id=data['parent_id'], school_id=school_id, role='parent').first()
    if not parent:
        return jsonify({'error': 'Parent not found'}), 400
    
    # Validate that student exists in the school
    student = Student.query.filter_by(id=data['student_id'], school_id=school_id).first()
    if not student:
        return jsonify({'error': 'Student not found'}), 400
    
    relationship = ParentStudentRelationship(
        parent_id=data['parent_id'],
        student_id=data['student_id'],
        relationship=data['relationship'],
        is_primary=data.get('is_primary', False)
    )
    
    db.session.add(relationship)
    db.session.commit()
    
    return jsonify(relationship.to_dict()), 201

@student_bp.route('/schools/<school_id>/parent-student-relationships/<relationship_id>', methods=['DELETE'])
def delete_parent_student_relationship(school_id, relationship_id):
    """Delete a parent-student relationship"""
    relationship = db.session.query(ParentStudentRelationship).join(Student).filter(
        ParentStudentRelationship.id == relationship_id,
        Student.school_id == school_id
    ).first_or_404()
    
    db.session.delete(relationship)
    db.session.commit()
    return '', 204

# Class-Subject assignment endpoints
@student_bp.route('/schools/<school_id>/class-subjects', methods=['GET'])
def get_class_subjects(school_id):
    """Get all class-subject assignments in a school"""
    class_subjects = db.session.query(ClassSubject).join(
        'school_class'
    ).filter_by(school_id=school_id).all()
    
    return jsonify([cs.to_dict() for cs in class_subjects])

@student_bp.route('/schools/<school_id>/class-subjects', methods=['POST'])
def create_class_subject(school_id):
    """Create a new class-subject assignment"""
    data = request.json
    
    # Validate required fields
    required_fields = ['class_id', 'subject_id']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    class_subject = ClassSubject(
        class_id=data['class_id'],
        subject_id=data['subject_id'],
        teacher_id=data.get('teacher_id')
    )
    
    db.session.add(class_subject)
    db.session.commit()
    
    return jsonify(class_subject.to_dict()), 201

@student_bp.route('/schools/<school_id>/class-subjects/<class_subject_id>', methods=['PUT'])
def update_class_subject(school_id, class_subject_id):
    """Update a class-subject assignment"""
    class_subject = db.session.query(ClassSubject).join(
        'school_class'
    ).filter(
        ClassSubject.id == class_subject_id,
        'school_class.school_id' == school_id
    ).first_or_404()
    
    data = request.json
    
    if 'teacher_id' in data:
        class_subject.teacher_id = data['teacher_id']
    
    db.session.commit()
    
    return jsonify(class_subject.to_dict())

@student_bp.route('/schools/<school_id>/class-subjects/<class_subject_id>', methods=['DELETE'])
def delete_class_subject(school_id, class_subject_id):
    """Delete a class-subject assignment"""
    class_subject = db.session.query(ClassSubject).join(
        'school_class'
    ).filter(
        ClassSubject.id == class_subject_id,
        'school_class.school_id' == school_id
    ).first_or_404()
    
    db.session.delete(class_subject)
    db.session.commit()
    return '', 204

