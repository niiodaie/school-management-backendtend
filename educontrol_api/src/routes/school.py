from flask import Blueprint, jsonify, request
from src.models.school import School, SchoolUser, AcademicYear, SchoolClass, Subject, db
from datetime import datetime

school_bp = Blueprint('school', __name__)

@school_bp.route('/schools', methods=['GET'])
def get_schools():
    """Get all schools"""
    schools = School.query.all()
    return jsonify([school.to_dict() for school in schools])

@school_bp.route('/schools', methods=['POST'])
def create_school():
    """Create a new school"""
    data = request.json
    
    # Validate required fields
    required_fields = ['name']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    school = School(
        name=data['name'],
        address=data.get('address'),
        phone=data.get('phone'),
        email=data.get('email'),
        website=data.get('website'),
        logo_url=data.get('logo_url'),
        timezone=data.get('timezone', 'UTC'),
        currency=data.get('currency', 'USD'),
        locale=data.get('locale', 'en'),
        subscription_plan=data.get('subscription_plan', 'basic'),
        subscription_status=data.get('subscription_status', 'active')
    )
    
    db.session.add(school)
    db.session.commit()
    
    return jsonify(school.to_dict()), 201

@school_bp.route('/schools/<school_id>', methods=['GET'])
def get_school(school_id):
    """Get a specific school"""
    school = School.query.get_or_404(school_id)
    return jsonify(school.to_dict())

@school_bp.route('/schools/<school_id>', methods=['PUT'])
def update_school(school_id):
    """Update a school"""
    school = School.query.get_or_404(school_id)
    data = request.json
    
    # Update fields
    updatable_fields = ['name', 'address', 'phone', 'email', 'website', 'logo_url', 
                       'timezone', 'currency', 'locale', 'subscription_plan', 'subscription_status']
    
    for field in updatable_fields:
        if field in data:
            setattr(school, field, data[field])
    
    school.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify(school.to_dict())

@school_bp.route('/schools/<school_id>', methods=['DELETE'])
def delete_school(school_id):
    """Delete a school"""
    school = School.query.get_or_404(school_id)
    db.session.delete(school)
    db.session.commit()
    return '', 204

# School Users endpoints
@school_bp.route('/schools/<school_id>/users', methods=['GET'])
def get_school_users(school_id):
    """Get all users in a school"""
    users = SchoolUser.query.filter_by(school_id=school_id).all()
    return jsonify([user.to_dict() for user in users])

@school_bp.route('/schools/<school_id>/users', methods=['POST'])
def create_school_user(school_id):
    """Create a new user in a school"""
    data = request.json
    
    # Validate required fields
    required_fields = ['role', 'first_name', 'last_name', 'email']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    # Validate role
    valid_roles = ['admin', 'teacher', 'parent', 'student']
    if data['role'] not in valid_roles:
        return jsonify({'error': f'Invalid role. Must be one of: {valid_roles}'}), 400
    
    user = SchoolUser(
        school_id=school_id,
        role=data['role'],
        first_name=data['first_name'],
        last_name=data['last_name'],
        email=data['email'],
        phone=data.get('phone'),
        avatar_url=data.get('avatar_url'),
        is_active=data.get('is_active', True)
    )
    
    db.session.add(user)
    db.session.commit()
    
    return jsonify(user.to_dict()), 201

@school_bp.route('/schools/<school_id>/users/<user_id>', methods=['GET'])
def get_school_user(school_id, user_id):
    """Get a specific user in a school"""
    user = SchoolUser.query.filter_by(id=user_id, school_id=school_id).first_or_404()
    return jsonify(user.to_dict())

@school_bp.route('/schools/<school_id>/users/<user_id>', methods=['PUT'])
def update_school_user(school_id, user_id):
    """Update a user in a school"""
    user = SchoolUser.query.filter_by(id=user_id, school_id=school_id).first_or_404()
    data = request.json
    
    # Update fields
    updatable_fields = ['role', 'first_name', 'last_name', 'email', 'phone', 'avatar_url', 'is_active']
    
    for field in updatable_fields:
        if field in data:
            if field == 'role':
                valid_roles = ['admin', 'teacher', 'parent', 'student']
                if data[field] not in valid_roles:
                    return jsonify({'error': f'Invalid role. Must be one of: {valid_roles}'}), 400
            setattr(user, field, data[field])
    
    user.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify(user.to_dict())

@school_bp.route('/schools/<school_id>/users/<user_id>', methods=['DELETE'])
def delete_school_user(school_id, user_id):
    """Delete a user from a school"""
    user = SchoolUser.query.filter_by(id=user_id, school_id=school_id).first_or_404()
    db.session.delete(user)
    db.session.commit()
    return '', 204

# Academic Years endpoints
@school_bp.route('/schools/<school_id>/academic-years', methods=['GET'])
def get_academic_years(school_id):
    """Get all academic years for a school"""
    academic_years = AcademicYear.query.filter_by(school_id=school_id).all()
    return jsonify([year.to_dict() for year in academic_years])

@school_bp.route('/schools/<school_id>/academic-years', methods=['POST'])
def create_academic_year(school_id):
    """Create a new academic year"""
    data = request.json
    
    # Validate required fields
    required_fields = ['name', 'start_date', 'end_date']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    try:
        start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
        end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
    
    academic_year = AcademicYear(
        school_id=school_id,
        name=data['name'],
        start_date=start_date,
        end_date=end_date,
        is_current=data.get('is_current', False)
    )
    
    db.session.add(academic_year)
    db.session.commit()
    
    return jsonify(academic_year.to_dict()), 201

# Classes endpoints
@school_bp.route('/schools/<school_id>/classes', methods=['GET'])
def get_school_classes(school_id):
    """Get all classes for a school"""
    classes = SchoolClass.query.filter_by(school_id=school_id).all()
    return jsonify([cls.to_dict() for cls in classes])

@school_bp.route('/schools/<school_id>/classes', methods=['POST'])
def create_school_class(school_id):
    """Create a new class"""
    data = request.json
    
    # Validate required fields
    required_fields = ['name', 'academic_year_id']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    school_class = SchoolClass(
        school_id=school_id,
        academic_year_id=data['academic_year_id'],
        name=data['name'],
        description=data.get('description'),
        capacity=data.get('capacity', 30),
        class_teacher_id=data.get('class_teacher_id')
    )
    
    db.session.add(school_class)
    db.session.commit()
    
    return jsonify(school_class.to_dict()), 201

# Subjects endpoints
@school_bp.route('/schools/<school_id>/subjects', methods=['GET'])
def get_school_subjects(school_id):
    """Get all subjects for a school"""
    subjects = Subject.query.filter_by(school_id=school_id).all()
    return jsonify([subject.to_dict() for subject in subjects])

@school_bp.route('/schools/<school_id>/subjects', methods=['POST'])
def create_school_subject(school_id):
    """Create a new subject"""
    data = request.json
    
    # Validate required fields
    required_fields = ['name']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    subject = Subject(
        school_id=school_id,
        name=data['name'],
        code=data.get('code'),
        description=data.get('description'),
        color=data.get('color', '#3B82F6')
    )
    
    db.session.add(subject)
    db.session.commit()
    
    return jsonify(subject.to_dict()), 201

