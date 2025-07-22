-- EduControl Storage Rules
-- Storage bucket policies for secure file uploads and access

-- Create storage buckets
INSERT INTO storage.buckets (id, name, public) VALUES 
    ('school-logos', 'school-logos', true),
    ('user-avatars', 'user-avatars', true),
    ('documents', 'documents', false),
    ('certificates', 'certificates', false);

-- Helper function to get user's school_id for storage
CREATE OR REPLACE FUNCTION get_user_school_id_storage()
RETURNS UUID AS $$
BEGIN
    RETURN (SELECT school_id FROM public.users WHERE id = auth.uid());
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Helper function to get user's role for storage
CREATE OR REPLACE FUNCTION get_user_role_storage()
RETURNS TEXT AS $$
BEGIN
    RETURN (SELECT role FROM public.users WHERE id = auth.uid());
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- School logos bucket policies
CREATE POLICY "School logos are publicly viewable" ON storage.objects
    FOR SELECT USING (bucket_id = 'school-logos');

CREATE POLICY "School admins can upload school logos" ON storage.objects
    FOR INSERT WITH CHECK (
        bucket_id = 'school-logos' AND 
        get_user_role_storage() = 'admin' AND
        (storage.foldername(name))[1] = get_user_school_id_storage()::text
    );

CREATE POLICY "School admins can update their school logos" ON storage.objects
    FOR UPDATE USING (
        bucket_id = 'school-logos' AND 
        get_user_role_storage() = 'admin' AND
        (storage.foldername(name))[1] = get_user_school_id_storage()::text
    );

CREATE POLICY "School admins can delete their school logos" ON storage.objects
    FOR DELETE USING (
        bucket_id = 'school-logos' AND 
        get_user_role_storage() = 'admin' AND
        (storage.foldername(name))[1] = get_user_school_id_storage()::text
    );

-- User avatars bucket policies
CREATE POLICY "User avatars are publicly viewable" ON storage.objects
    FOR SELECT USING (bucket_id = 'user-avatars');

CREATE POLICY "Users can upload their own avatars" ON storage.objects
    FOR INSERT WITH CHECK (
        bucket_id = 'user-avatars' AND 
        (storage.foldername(name))[1] = get_user_school_id_storage()::text AND
        (storage.foldername(name))[2] = auth.uid()::text
    );

CREATE POLICY "Users can update their own avatars" ON storage.objects
    FOR UPDATE USING (
        bucket_id = 'user-avatars' AND 
        (storage.foldername(name))[1] = get_user_school_id_storage()::text AND
        (storage.foldername(name))[2] = auth.uid()::text
    );

CREATE POLICY "Users can delete their own avatars" ON storage.objects
    FOR DELETE USING (
        bucket_id = 'user-avatars' AND 
        (storage.foldername(name))[1] = get_user_school_id_storage()::text AND
        (storage.foldername(name))[2] = auth.uid()::text
    );

-- Documents bucket policies
CREATE POLICY "Users can view documents in their school" ON storage.objects
    FOR SELECT USING (
        bucket_id = 'documents' AND 
        (storage.foldername(name))[1] = get_user_school_id_storage()::text
    );

CREATE POLICY "Parents can view their children's documents" ON storage.objects
    FOR SELECT USING (
        bucket_id = 'documents' AND 
        (storage.foldername(name))[1] = get_user_school_id_storage()::text AND
        get_user_role_storage() = 'parent' AND
        (storage.foldername(name))[2] IN (
            SELECT s.id::text FROM public.students s
            JOIN public.parent_student_relationships psr ON s.id = psr.student_id
            WHERE psr.parent_id = auth.uid()
        )
    );

CREATE POLICY "Students can view their own documents" ON storage.objects
    FOR SELECT USING (
        bucket_id = 'documents' AND 
        (storage.foldername(name))[1] = get_user_school_id_storage()::text AND
        get_user_role_storage() = 'student' AND
        (storage.foldername(name))[2] IN (
            SELECT s.id::text FROM public.students s
            WHERE s.user_id = auth.uid()
        )
    );

CREATE POLICY "School admins and teachers can upload documents" ON storage.objects
    FOR INSERT WITH CHECK (
        bucket_id = 'documents' AND 
        (storage.foldername(name))[1] = get_user_school_id_storage()::text AND
        get_user_role_storage() IN ('admin', 'teacher')
    );

CREATE POLICY "School admins and teachers can update documents" ON storage.objects
    FOR UPDATE USING (
        bucket_id = 'documents' AND 
        (storage.foldername(name))[1] = get_user_school_id_storage()::text AND
        get_user_role_storage() IN ('admin', 'teacher')
    );

CREATE POLICY "School admins and teachers can delete documents" ON storage.objects
    FOR DELETE USING (
        bucket_id = 'documents' AND 
        (storage.foldername(name))[1] = get_user_school_id_storage()::text AND
        get_user_role_storage() IN ('admin', 'teacher')
    );

-- Certificates bucket policies
CREATE POLICY "Users can view certificates in their school" ON storage.objects
    FOR SELECT USING (
        bucket_id = 'certificates' AND 
        (storage.foldername(name))[1] = get_user_school_id_storage()::text
    );

CREATE POLICY "Parents can view their children's certificates" ON storage.objects
    FOR SELECT USING (
        bucket_id = 'certificates' AND 
        (storage.foldername(name))[1] = get_user_school_id_storage()::text AND
        get_user_role_storage() = 'parent' AND
        (storage.foldername(name))[2] IN (
            SELECT s.id::text FROM public.students s
            JOIN public.parent_student_relationships psr ON s.id = psr.student_id
            WHERE psr.parent_id = auth.uid()
        )
    );

CREATE POLICY "Students can view their own certificates" ON storage.objects
    FOR SELECT USING (
        bucket_id = 'certificates' AND 
        (storage.foldername(name))[1] = get_user_school_id_storage()::text AND
        get_user_role_storage() = 'student' AND
        (storage.foldername(name))[2] IN (
            SELECT s.id::text FROM public.students s
            WHERE s.user_id = auth.uid()
        )
    );

CREATE POLICY "School admins and teachers can upload certificates" ON storage.objects
    FOR INSERT WITH CHECK (
        bucket_id = 'certificates' AND 
        (storage.foldername(name))[1] = get_user_school_id_storage()::text AND
        get_user_role_storage() IN ('admin', 'teacher')
    );

CREATE POLICY "School admins and teachers can update certificates" ON storage.objects
    FOR UPDATE USING (
        bucket_id = 'certificates' AND 
        (storage.foldername(name))[1] = get_user_school_id_storage()::text AND
        get_user_role_storage() IN ('admin', 'teacher')
    );

CREATE POLICY "School admins and teachers can delete certificates" ON storage.objects
    FOR DELETE USING (
        bucket_id = 'certificates' AND 
        (storage.foldername(name))[1] = get_user_school_id_storage()::text AND
        get_user_role_storage() IN ('admin', 'teacher')
    );

-- File size and type restrictions (to be implemented in application logic)
-- Maximum file sizes:
-- - School logos: 5MB
-- - User avatars: 2MB  
-- - Documents: 50MB
-- - Certificates: 10MB

-- Allowed file types:
-- - School logos: image/jpeg, image/png, image/webp
-- - User avatars: image/jpeg, image/png, image/webp
-- - Documents: application/pdf, image/jpeg, image/png, application/msword, application/vnd.openxmlformats-officedocument.wordprocessingml.document
-- - Certificates: application/pdf, image/jpeg, image/png

