-- HR Monitoring safety officer credentials migration
-- Run once in Supabase SQL Editor if the table is not created yet.

create table if not exists public.employee_safety_officers (
  id bigserial primary key,
  employee_id uuid references public.employees(id) on delete cascade,
  safety_officer_name text not null,
  certificate_number text,
  issued_date date,
  expiry_date date,
  status text,
  attachment_url text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create index if not exists employee_safety_officers_employee_id_idx
  on public.employee_safety_officers (employee_id);

create index if not exists employee_safety_officers_expiry_date_idx
  on public.employee_safety_officers (expiry_date);

alter table public.employee_safety_officers disable row level security;

select pg_notify('pgrst', 'reload schema');
