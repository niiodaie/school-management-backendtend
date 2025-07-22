-- EduControl Authentication Policies
-- Row Level Security (RLS) policies to ensure multi-tenant data isolation

-- Enable RLS on all tables
ALTER TABLE schools ENABLE ROW LEVEL SECURITY;
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE academic_years ENABLE ROW LEVEL SECURITY;
ALTER TABLE classes ENABLE ROW LEVEL SECURITY;
ALTER TABLE subjects ENABLE ROW LEVEL SECURITY;
ALTER TABLE students ENABLE ROW LEVEL SECURITY;
ALTER TABLE teachers ENABLE ROW LEVEL SECURITY;
ALTER TABLE parent_student_relationships ENABLE ROW LEVEL SECURITY;
ALTER TABLE class_subjects ENABLE ROW LEVEL SECURITY;
ALTER TABLE timetables ENABLE ROW LEVEL SECURITY;
ALTER TABLE attendance ENABLE ROW LEVEL SECURITY;
ALTER TABLE grades ENABLE ROW LEVEL SECURITY;
ALTER TABLE invoices ENABLE ROW LEVEL SECURITY;
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE announcements ENABLE ROW LEVEL SECURITY;
ALTER TABLE messages ENABLE ROW LEVEL SECURITY;

-- Helper function to get current user's school_id
CREATE OR REPLACE FUNCTION get_user_school_id()
RETURNS UUID AS $$
BEGIN
    RETURN (SELECT school_id FROM users WHERE id = auth.uid());
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Helper function to get current user's role
CREATE OR REPLACE FUNCTION get_user_role()
RETURNS TEXT AS $$
BEGIN
    RETURN (SELECT role FROM users WHERE id = auth.uid());
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Schools policies
CREATE POLICY "Users can view their own school" ON schools
    FOR SELECT USING (id = get_user_school_id());

CREATE POLICY "School admins can update their school" ON schools
    FOR UPDATE USING (id = get_user_school_id() AND get_user_role() = 'admin');

CREATE POLICY "School admins can insert schools" ON schools
    FOR INSERT WITH CHECK (get_user_role() = 'admin');

-- Users policies
CREATE POLICY "Users can view users in their school" ON users
    FOR SELECT USING (school_id = get_user_school_id());

CREATE POLICY "Users can update their own profile" ON users
    FOR UPDATE USING (id = auth.uid());

CREATE POLICY "School admins can manage users in their school" ON users
    FOR ALL USING (school_id = get_user_school_id() AND get_user_role() = 'admin');

CREATE POLICY "New users can insert their profile" ON users
    FOR INSERT WITH CHECK (id = auth.uid());

-- Academic years policies
CREATE POLICY "Users can view academic years in their school" ON academic_years
    FOR SELECT USING (school_id = get_user_school_id());

CREATE POLICY "School admins can manage academic years" ON academic_years
    FOR ALL USING (school_id = get_user_school_id() AND get_user_role() = 'admin');

-- Classes policies
CREATE POLICY "Users can view classes in their school" ON classes
    FOR SELECT USING (school_id = get_user_school_id());

CREATE POLICY "School admins can manage classes" ON classes
    FOR ALL USING (school_id = get_user_school_id() AND get_user_role() = 'admin');

-- Subjects policies
CREATE POLICY "Users can view subjects in their school" ON subjects
    FOR SELECT USING (school_id = get_user_school_id());

CREATE POLICY "School admins can manage subjects" ON subjects
    FOR ALL USING (school_id = get_user_school_id() AND get_user_role() = 'admin');

-- Students policies
CREATE POLICY "Users can view students in their school" ON students
    FOR SELECT USING (school_id = get_user_school_id());

CREATE POLICY "Parents can view their own children" ON students
    FOR SELECT USING (
        get_user_role() = 'parent' AND 
        id IN (SELECT student_id FROM parent_student_relationships WHERE parent_id = auth.uid())
    );

CREATE POLICY "Students can view their own record" ON students
    FOR SELECT USING (user_id = auth.uid());

CREATE POLICY "School admins and teachers can manage students" ON students
    FOR ALL USING (
        school_id = get_user_school_id() AND 
        get_user_role() IN ('admin', 'teacher')
    );

-- Teachers policies
CREATE POLICY "Users can view teachers in their school" ON teachers
    FOR SELECT USING (school_id = get_user_school_id());

CREATE POLICY "Teachers can view their own record" ON teachers
    FOR SELECT USING (user_id = auth.uid());

CREATE POLICY "School admins can manage teachers" ON teachers
    FOR ALL USING (school_id = get_user_school_id() AND get_user_role() = 'admin');

-- Parent-student relationships policies
CREATE POLICY "Parents can view their relationships" ON parent_student_relationships
    FOR SELECT USING (parent_id = auth.uid());

CREATE POLICY "School admins can manage parent-student relationships" ON parent_student_relationships
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM students s 
            WHERE s.id = student_id AND s.school_id = get_user_school_id()
        ) AND get_user_role() = 'admin'
    );

-- Class-subjects policies
CREATE POLICY "Users can view class subjects in their school" ON class_subjects
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM classes c 
            WHERE c.id = class_id AND c.school_id = get_user_school_id()
        )
    );

CREATE POLICY "School admins can manage class subjects" ON class_subjects
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM classes c 
            WHERE c.id = class_id AND c.school_id = get_user_school_id()
        ) AND get_user_role() = 'admin'
    );

-- Timetables policies
CREATE POLICY "Users can view timetables in their school" ON timetables
    FOR SELECT USING (school_id = get_user_school_id());

CREATE POLICY "School admins and teachers can manage timetables" ON timetables
    FOR ALL USING (
        school_id = get_user_school_id() AND 
        get_user_role() IN ('admin', 'teacher')
    );

-- Attendance policies
CREATE POLICY "Users can view attendance in their school" ON attendance
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM students s 
            WHERE s.id = student_id AND s.school_id = get_user_school_id()
        )
    );

CREATE POLICY "Parents can view their children's attendance" ON attendance
    FOR SELECT USING (
        get_user_role() = 'parent' AND 
        student_id IN (SELECT student_id FROM parent_student_relationships WHERE parent_id = auth.uid())
    );

CREATE POLICY "Students can view their own attendance" ON attendance
    FOR SELECT USING (
        get_user_role() = 'student' AND 
        student_id IN (SELECT id FROM students WHERE user_id = auth.uid())
    );

CREATE POLICY "Teachers can manage attendance" ON attendance
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM students s 
            WHERE s.id = student_id AND s.school_id = get_user_school_id()
        ) AND get_user_role() IN ('admin', 'teacher')
    );

-- Grades policies
CREATE POLICY "Users can view grades in their school" ON grades
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM students s 
            WHERE s.id = student_id AND s.school_id = get_user_school_id()
        )
    );

CREATE POLICY "Parents can view their children's grades" ON grades
    FOR SELECT USING (
        get_user_role() = 'parent' AND 
        student_id IN (SELECT student_id FROM parent_student_relationships WHERE parent_id = auth.uid())
    );

CREATE POLICY "Students can view their own grades" ON grades
    FOR SELECT USING (
        get_user_role() = 'student' AND 
        student_id IN (SELECT id FROM students WHERE user_id = auth.uid())
    );

CREATE POLICY "Teachers can manage grades" ON grades
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM students s 
            WHERE s.id = student_id AND s.school_id = get_user_school_id()
        ) AND get_user_role() IN ('admin', 'teacher')
    );

-- Invoices policies
CREATE POLICY "Users can view invoices in their school" ON invoices
    FOR SELECT USING (school_id = get_user_school_id());

CREATE POLICY "Parents can view their children's invoices" ON invoices
    FOR SELECT USING (
        get_user_role() = 'parent' AND 
        student_id IN (SELECT student_id FROM parent_student_relationships WHERE parent_id = auth.uid())
    );

CREATE POLICY "School admins can manage invoices" ON invoices
    FOR ALL USING (school_id = get_user_school_id() AND get_user_role() = 'admin');

-- Documents policies
CREATE POLICY "Users can view documents in their school" ON documents
    FOR SELECT USING (school_id = get_user_school_id());

CREATE POLICY "Parents can view their children's documents" ON documents
    FOR SELECT USING (
        get_user_role() = 'parent' AND 
        student_id IN (SELECT student_id FROM parent_student_relationships WHERE parent_id = auth.uid())
    );

CREATE POLICY "Students can view their own documents" ON documents
    FOR SELECT USING (
        get_user_role() = 'student' AND 
        student_id IN (SELECT id FROM students WHERE user_id = auth.uid())
    );

CREATE POLICY "School admins and teachers can manage documents" ON documents
    FOR ALL USING (
        school_id = get_user_school_id() AND 
        get_user_role() IN ('admin', 'teacher')
    );

-- Announcements policies
CREATE POLICY "Users can view announcements in their school" ON announcements
    FOR SELECT USING (
        school_id = get_user_school_id() AND 
        is_published = true AND 
        (expires_at IS NULL OR expires_at > NOW()) AND
        (target_audience = 'all' OR target_audience = get_user_role())
    );

CREATE POLICY "School admins and teachers can manage announcements" ON announcements
    FOR ALL USING (
        school_id = get_user_school_id() AND 
        get_user_role() IN ('admin', 'teacher')
    );

-- Messages policies
CREATE POLICY "Users can view their own messages" ON messages
    FOR SELECT USING (
        school_id = get_user_school_id() AND 
        (sender_id = auth.uid() OR recipient_id = auth.uid())
    );

CREATE POLICY "Users can send messages within their school" ON messages
    FOR INSERT WITH CHECK (
        school_id = get_user_school_id() AND 
        sender_id = auth.uid() AND
        EXISTS (SELECT 1 FROM users WHERE id = recipient_id AND school_id = get_user_school_id())
    );

CREATE POLICY "Users can update their own sent messages" ON messages
    FOR UPDATE USING (
        school_id = get_user_school_id() AND 
        sender_id = auth.uid()
    );

-- Grant necessary permissions to authenticated users
GRANT USAGE ON SCHEMA public TO authenticated;
GRANT ALL ON ALL TABLES IN SCHEMA public TO authenticated;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO authenticated;

