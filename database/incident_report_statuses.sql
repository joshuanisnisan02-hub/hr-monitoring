-- Run this once against the Supabase project used by HR Monitoring.
-- It is safe for existing Incident Report records and can be re-run.

alter table public.incident_reports
  add column if not exists response_status text;

alter table public.incident_reports
  alter column response_status set default 'Waiting for Response';

update public.incident_reports
set response_status = 'Waiting for Response'
where response_status is null or btrim(response_status) = '';

alter table public.incident_reports
  alter column response_status set not null;

alter table public.incident_reports
  alter column nod set default 'Pending';

update public.incident_reports
set nod = 'Pending'
where nod is null or btrim(nod) = '';

comment on column public.incident_reports.response_status is
  'Employee response timing status: Waiting for Response, Responded On Time, Responded Late, or Waive the Right.';

comment on column public.incident_reports.nod is
  'Incident resolution or disciplinary status maintained from the Incident Report table.';
