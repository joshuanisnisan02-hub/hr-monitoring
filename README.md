# HR Monitoring

Flutter + Supabase system converted from the uploaded Excel workbooks.

## Excel flow preserved

The app is organized around the same process used by the spreadsheets:

1. **Faculty and Staff Master List**
   - Source sheets include `FACULTY 2026-2027`, `FACULTY AND STAFF 26-27`, `PART-TIME 2026-2027`, `Updated!`, and `Evaluation`.
   - Supabase table: `employees`.

2. **Contract Monitoring**
   - Source sheets include `CONTRACT` and `CONTRACT SUMMARY`.
   - Supabase table/view: `employee_contracts`, `hr_contract_monitoring`.
   - The system keeps contract start date, duration, ending date, days remaining, attachment URL, and status.

3. **Licenses and National Certificates**
   - Source sheets include `LICENSE`, `LICENSE SUMMARRY`, and `NATIONAL CERT`.
   - Supabase tables: `employee_licenses`, `employee_certificates`.

4. **Evaluation Records**
   - Source sheets include `A.Y 2024-2025 1st Sem EmpRating`, `A.Y 2025-2026 2st Sem EmpRating`, and `SUMMARY`.
   - Supabase table/view: `evaluation_records`, `hr_evaluation_summary`.

5. **Faculty Ranking**
   - Source sheets include `FULL TIME`, `PROBATIONARY`, and ranking `SUMMARY`.
   - Supabase table/view: `ranking_cycles`, `ranking_applications`, `hr_faculty_ranking_summary`.

## Run

```bash
flutter pub get
flutter run -d chrome \
  --dart-define=SUPABASE_URL=https://iysbzkdczngvafvtwpjn.supabase.co \
  --dart-define=SUPABASE_PUBLIC_CLIENT_KEY=PASTE_YOUR_SUPABASE_PUBLIC_KEY
```

The public client key is intentionally not committed to GitHub.

## Supabase

The database migration has been applied to project `iysbzkdczngvafvtwpjn`. A copy is also saved in `supabase/migrations/20260629_create_hr_monitoring_core.sql` for version tracking.

## Current implementation status

Implemented:

- Flutter Material 3 app shell
- Dashboard
- Faculty/staff master list with manual add
- Contract monitoring view
- License and certificate monitoring views
- Evaluation records view
- Faculty ranking summary view
- Supabase schema, views, indexes, and seed ranking data

Next recommended step:

- Import the actual Excel rows into the Supabase tables. The schema stores `source_workbook`, `source_sheet`, and `source_row` so each database record can still be traced back to the original Excel process.
