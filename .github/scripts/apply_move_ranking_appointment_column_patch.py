from pathlib import Path

p = Path('lib/main.dart')
s = p.read_text()

old = """                GridCol('employee_name', 'Employee Name', flex: 3, primary: true),
                GridCol('previous_rank_text', 'Previous Rank', flex: 2),
                GridCol('previous_salary', 'Basic Salary', isMoney: true),
                GridCol('applied_rank_text', 'Rank Applied', flex: 2),
                GridCol('applied_salary', 'Basic Salary Adjustment', flex: 2, isMoney: true),
                GridCol('points_earned', 'Points Earned', isNumber: true),
                GridCol('approved_rank_text', 'Approved Rank', flex: 2),
                GridCol('appointment_title', 'Appointment', flex: 3),"""

new = """                GridCol('employee_name', 'Employee Name', flex: 3, primary: true),
                GridCol('appointment_title', 'Appointment', flex: 3),
                GridCol('previous_rank_text', 'Previous Rank', flex: 2),
                GridCol('previous_salary', 'Basic Salary', isMoney: true),
                GridCol('applied_rank_text', 'Rank Applied', flex: 2),
                GridCol('applied_salary', 'Basic Salary Adjustment', flex: 2, isMoney: true),
                GridCol('points_earned', 'Points Earned', isNumber: true),
                GridCol('approved_rank_text', 'Approved Rank', flex: 2),"""

if old not in s and new not in s:
    raise SystemExit('Ranking columns block not found')
s = s.replace(old, new, 1)

p.write_text(s)
