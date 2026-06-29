-- HR Monitoring security hardening
-- Run this in Supabase Dashboard > SQL Editor after creating the two Auth users:
-- admin@hr-monitoring.local
-- hr@hr-monitoring.local

-- 1) Enable RLS on all app tables.
alter table public.employees enable row level security;
alter table public.employee_contracts enable row level security;
alter table public.employee_licenses enable row level security;
alter table public.employee_certificates enable row level security;
alter table public.evaluation_records enable row level security;
alter table public.ranking_applications enable row level security;
alter table public.ranking_cycles enable row level security;
alter table public.ranks enable row level security;
alter table public.hr_reference_options enable row level security;

-- 2) Remove old policies if rerunning this file.
drop policy if exists employees_admin_hr_only on public.employees;
drop policy if exists employee_contracts_admin_hr_only on public.employee_contracts;
drop policy if exists employee_licenses_admin_hr_only on public.employee_licenses;
drop policy if exists employee_certificates_admin_hr_only on public.employee_certificates;
drop policy if exists evaluation_records_admin_hr_only on public.evaluation_records;
drop policy if exists ranking_applications_admin_hr_only on public.ranking_applications;
drop policy if exists ranking_cycles_admin_hr_only on public.ranking_cycles;
drop policy if exists ranks_admin_hr_only on public.ranks;
drop policy if exists hr_reference_options_admin_hr_only on public.hr_reference_options;

-- 3) Allow access only for the two signed-in Auth users.
create policy employees_admin_hr_only
on public.employees
for all
to authenticated
using ((auth.jwt() ->> 'email') in ('admin@hr-monitoring.local', 'hr@hr-monitoring.local'))
with check ((auth.jwt() ->> 'email') in ('admin@hr-monitoring.local', 'hr@hr-monitoring.local'));

create policy employee_contracts_admin_hr_only
on public.employee_contracts
for all
to authenticated
using ((auth.jwt() ->> 'email') in ('admin@hr-monitoring.local', 'hr@hr-monitoring.local'))
with check ((auth.jwt() ->> 'email') in ('admin@hr-monitoring.local', 'hr@hr-monitoring.local'));

create policy employee_licenses_admin_hr_only
on public.employee_licenses
for all
to authenticated
using ((auth.jwt() ->> 'email') in ('admin@hr-monitoring.local', 'hr@hr-monitoring.local'))
with check ((auth.jwt() ->> 'email') in ('admin@hr-monitoring.local', 'hr@hr-monitoring.local'));

create policy employee_certificates_admin_hr_only
on public.employee_certificates
for all
to authenticated
using ((auth.jwt() ->> 'email') in ('admin@hr-monitoring.local', 'hr@hr-monitoring.local'))
with check ((auth.jwt() ->> 'email') in ('admin@hr-monitoring.local', 'hr@hr-monitoring.local'));

create policy evaluation_records_admin_hr_only
on public.evaluation_records
for all
to authenticated
using ((auth.jwt() ->> 'email') in ('admin@hr-monitoring.local', 'hr@hr-monitoring.local'))
with check ((auth.jwt() ->> 'email') in ('admin@hr-monitoring.local', 'hr@hr-monitoring.local'));

create policy ranking_applications_admin_hr_only
on public.ranking_applications
for all
to authenticated
using ((auth.jwt() ->> 'email') in ('admin@hr-monitoring.local', 'hr@hr-monitoring.local'))
with check ((auth.jwt() ->> 'email') in ('admin@hr-monitoring.local', 'hr@hr-monitoring.local'));

create policy ranking_cycles_admin_hr_only
on public.ranking_cycles
for all
to authenticated
using ((auth.jwt() ->> 'email') in ('admin@hr-monitoring.local', 'hr@hr-monitoring.local'))
with check ((auth.jwt() ->> 'email') in ('admin@hr-monitoring.local', 'hr@hr-monitoring.local'));

create policy ranks_admin_hr_only
on public.ranks
for all
to authenticated
using ((auth.jwt() ->> 'email') in ('admin@hr-monitoring.local', 'hr@hr-monitoring.local'))
with check ((auth.jwt() ->> 'email') in ('admin@hr-monitoring.local', 'hr@hr-monitoring.local'));

create policy hr_reference_options_admin_hr_only
on public.hr_reference_options
for all
to authenticated
using ((auth.jwt() ->> 'email') in ('admin@hr-monitoring.local', 'hr@hr-monitoring.local'))
with check ((auth.jwt() ->> 'email') in ('admin@hr-monitoring.local', 'hr@hr-monitoring.local'));

-- 4) Protect views by making them run as the logged-in user, not as the owner.
alter view if exists public.hr_dashboard_counts set (security_invoker = true);
alter view if exists public.hr_contract_monitoring set (security_invoker = true);
alter view if exists public.hr_license_monitoring set (security_invoker = true);
alter view if exists public.hr_certificate_monitoring set (security_invoker = true);
alter view if exists public.hr_evaluation_summary set (security_invoker = true);
alter view if exists public.hr_faculty_ranking_summary set (security_invoker = true);

-- 5) Remove anonymous table grants and keep access for authenticated users only.
revoke all on public.employees from anon;
revoke all on public.employee_contracts from anon;
revoke all on public.employee_licenses from anon;
revoke all on public.employee_certificates from anon;
revoke all on public.evaluation_records from anon;
revoke all on public.ranking_applications from anon;
revoke all on public.ranking_cycles from anon;
revoke all on public.ranks from anon;
revoke all on public.hr_reference_options from anon;

revoke all on public.hr_dashboard_counts from anon;
revoke all on public.hr_contract_monitoring from anon;
revoke all on public.hr_license_monitoring from anon;
revoke all on public.hr_certificate_monitoring from anon;
revoke all on public.hr_evaluation_summary from anon;
revoke all on public.hr_faculty_ranking_summary from anon;

grant select, insert, update, delete on public.employees to authenticated;
grant select, insert, update, delete on public.employee_contracts to authenticated;
grant select, insert, update, delete on public.employee_licenses to authenticated;
grant select, insert, update, delete on public.employee_certificates to authenticated;
grant select, insert, update, delete on public.evaluation_records to authenticated;
grant select, insert, update, delete on public.ranking_applications to authenticated;
grant select, insert, update, delete on public.ranking_cycles to authenticated;
grant select, insert, update, delete on public.ranks to authenticated;
grant select, insert, update, delete on public.hr_reference_options to authenticated;

grant select on public.hr_dashboard_counts to authenticated;
grant select on public.hr_contract_monitoring to authenticated;
grant select on public.hr_license_monitoring to authenticated;
grant select on public.hr_certificate_monitoring to authenticated;
grant select on public.hr_evaluation_summary to authenticated;
grant select on public.hr_faculty_ranking_summary to authenticated;
