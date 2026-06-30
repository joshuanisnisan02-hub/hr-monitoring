from pathlib import Path

p = Path('lib/main.dart')
s = p.read_text()

# Include approved_date in the Ranking select list.
s = s.replace(
    """select('id, employee_id, cycle_id, appointment, previous_rank_text, previous_salary, applied_rank_text, applied_salary, points_earned, approved_rank_text, approved_salary, employees(full_name), ranking_cycles(name)')""",
    """select('id, employee_id, cycle_id, appointment, previous_rank_text, previous_salary, applied_rank_text, applied_salary, points_earned, approved_rank_text, approved_salary, approved_date, employees(full_name), ranking_cycles(name)')""",
    1,
)

# Add Approved Date after Approved Rank, before actions. Appointment remains after Employee Name.
s = s.replace(
    """                GridCol('points_earned', 'Points Earned', isNumber: true),
                GridCol('approved_rank_text', 'Approved Rank', flex: 2),
              ],""",
    """                GridCol('points_earned', 'Points Earned', isNumber: true),
                GridCol('approved_rank_text', 'Approved Rank', flex: 2),
                GridCol('approved_date', 'Approved Date'),
              ],""",
    1,
)

# View dialog should include approved date.
s = s.replace(
    """                  'Approved Rank': 'approved_rank_text',
                  'Salary Rate': 'approved_salary',""",
    """                  'Approved Rank': 'approved_rank_text',
                  'Approved Date': 'approved_date',
                  'Salary Rate': 'approved_salary',""",
    1,
)

# Approve action should stamp the date.
s = s.replace(
    """      'approved_rank_text': row['applied_rank_text'],
      'approved_salary': row['applied_salary'],
      'updated_at': DateTime.now().toIso8601String(),""",
    """      'approved_rank_text': row['applied_rank_text'],
      'approved_salary': row['applied_salary'],
      'approved_date': DateFormat('yyyy-MM-dd').format(DateTime.now()),
      'updated_at': DateTime.now().toIso8601String(),""",
    1,
)

# Legacy report config, if present.
s = s.replace(
    """          GridCol('approved_rank_text', 'Approved Rank', flex: 2),
          GridCol('appointment_title', 'Appointment', flex: 3),""",
    """          GridCol('approved_rank_text', 'Approved Rank', flex: 2),
          GridCol('approved_date', 'Approved Date'),
          GridCol('appointment_title', 'Appointment', flex: 3),""",
    1,
)

p.write_text(s)
