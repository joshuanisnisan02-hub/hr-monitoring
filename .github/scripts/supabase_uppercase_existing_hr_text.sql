-- Optional one-time cleanup: convert existing HR text data to CAPITAL LETTERS.
-- This intentionally skips IDs, dates, email fields, and attachment URLs.

update public.employees set
  full_name = upper(full_name),
  name_key = upper(name_key),
  employee_code = upper(employee_code),
  bio_number = upper(bio_number),
  gender = upper(gender),
  education_level = upper(education_level),
  employment_status = upper(employment_status),
  designation = upper(designation),
  employee_type = upper(employee_type),
  civil_status = upper(civil_status),
  teaching_status = upper(teaching_status),
  license_summary = upper(license_summary),
  address = upper(address),
  contact_number = upper(contact_number),
  guardian_name = upper(guardian_name),
  guardian_relationship = upper(guardian_relationship),
  guardian_contact = upper(guardian_contact),
  guardian_address = upper(guardian_address),
  school_graduated = upper(school_graduated),
  degree_course = upper(degree_course),
  notes = upper(notes)
where true;

update public.employee_contracts set
  contract_type = upper(contract_type),
  status = upper(status)
where true;

update public.employee_licenses set
  license_name = upper(license_name),
  license_number = upper(license_number),
  status = upper(status)
where true;

update public.employee_certificates set
  certificate_type = upper(certificate_type),
  certificate_name = upper(certificate_name),
  certificate_number = upper(certificate_number),
  status = upper(status)
where true;

update public.employee_safety_officers set
  safety_officer_name = upper(safety_officer_name),
  certificate_number = upper(certificate_number),
  status = upper(status)
where true;

update public.evaluation_records set
  academic_year = upper(academic_year),
  semester = upper(semester),
  superior_description = upper(superior_description),
  peer_description = upper(peer_description),
  self_description = upper(self_description),
  student_description = upper(student_description),
  total_description = upper(total_description)
where true;

update public.employee_appointments set
  category = upper(category),
  appointment_title = upper(appointment_title)
where true;

update public.ranking_applications set
  appointment = upper(appointment),
  previous_rank_text = upper(previous_rank_text),
  applied_rank_text = upper(applied_rank_text),
  approved_rank_text = upper(approved_rank_text)
where true;

update public.employee_educational_backgrounds set
  education_level = upper(education_level),
  school_graduated = upper(school_graduated),
  degree_course = upper(degree_course),
  year_graduated = upper(year_graduated),
  status = upper(status)
where to_regclass('public.employee_educational_backgrounds') is not null;

select pg_notify('pgrst', 'reload schema');
