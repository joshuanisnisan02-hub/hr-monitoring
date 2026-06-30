alter table public.employees
  add column if not exists birth_date date,
  add column if not exists address text,
  add column if not exists contact_number text,
  add column if not exists email text,
  add column if not exists guardian_name text,
  add column if not exists guardian_relationship text,
  add column if not exists guardian_contact text,
  add column if not exists guardian_address text,
  add column if not exists school_graduated text,
  add column if not exists degree_course text,
  add column if not exists date_hired date;

update public.employees
set date_hired = coalesce(date_hired, starting_date)
where date_hired is null and starting_date is not null;
