-- HR Monitoring multiple educational background migration
-- Run once in Supabase SQL Editor if the table is not created yet.

create table if not exists public.employee_educational_backgrounds (
  id bigserial primary key,
  employee_id uuid references public.employees(id) on delete cascade,
  education_level text,
  school_graduated text,
  degree_course text,
  year_graduated text,
  status text,
  attachment_url text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create index if not exists employee_educational_backgrounds_employee_id_idx
  on public.employee_educational_backgrounds (employee_id);

create index if not exists employee_educational_backgrounds_year_graduated_idx
  on public.employee_educational_backgrounds (year_graduated);

alter table public.employee_educational_backgrounds disable row level security;

select pg_notify('pgrst', 'reload schema');
