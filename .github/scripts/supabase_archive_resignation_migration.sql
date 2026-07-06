-- HR Monitoring archive and resignation migration
-- Run this once in Supabase SQL Editor before testing the archive/date-resigned features.

alter table if exists public.employees
  add column if not exists date_resigned date;

create table if not exists public.archived_records (
  id bigserial primary key,
  module_name text not null,
  table_name text not null,
  original_id text,
  employee_id text,
  employee_name text,
  archive_type text not null default 'deleted',
  record_data jsonb not null default '{}'::jsonb,
  archived_at timestamptz not null default now(),
  is_restored boolean not null default false,
  restored_at timestamptz
);

create index if not exists archived_records_archive_type_idx
  on public.archived_records (archive_type);

create index if not exists archived_records_table_name_idx
  on public.archived_records (table_name);

create index if not exists archived_records_employee_name_idx
  on public.archived_records (employee_name);

create index if not exists archived_records_archived_at_idx
  on public.archived_records (archived_at desc);

-- Keep RLS disabled for this internal HR app table unless you already manage custom policies.
alter table public.archived_records disable row level security;
