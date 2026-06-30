from pathlib import Path

p = Path('lib/main.dart')
s = p.read_text()

# Ranking table: add Appointment column after the approved-related column.
s = s.replace(
    """                GridCol('points_earned', 'Points Earned', isNumber: true),
                GridCol('approved_rank_text', 'Approved Rank', flex: 2),
              ],""",
    """                GridCol('points_earned', 'Points Earned', isNumber: true),
                GridCol('approved_rank_text', 'Approved Rank', flex: 2),
                GridCol('appointment_title', 'Appointment', flex: 3),
              ],""",
    1,
)

# Ranking search should include appointment again because it is visible in the table.
s = s.replace(
    """searchHint: 'Search employee, rank, salary, or points',""",
    """searchHint: 'Search employee, rank, salary, points, or appointment',""",
    1,
)

# Legacy report config, if still present, should include the same appointment value.
s = s.replace(
    """          GridCol('points_earned', 'Points Earned', isNumber: true),
          GridCol('approved_rank_text', 'Approved Rank', flex: 2),
        ]),""",
    """          GridCol('points_earned', 'Points Earned', isNumber: true),
          GridCol('approved_rank_text', 'Approved Rank', flex: 2),
          GridCol('appointment_title', 'Appointment', flex: 3),
        ]),""",
    1,
)

p.write_text(s)
