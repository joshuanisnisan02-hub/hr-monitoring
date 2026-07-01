from pathlib import Path

path = Path('lib/main.dart')
text = path.read_text(encoding='utf-8')

changed = False

old_pages = """      const EvaluationsPage(),
      const AppointmentPage(),
      const RankingPage(),
    ];
"""
new_pages = """      const EvaluationsPage(),
      const AppointmentPage(),
      const RankingPage(),
      const ReportsPage(),
    ];
"""
if old_pages in text:
    text = text.replace(old_pages, new_pages, 1)
    changed = True
elif "const ReportsPage()," in text:
    pass
else:
    raise SystemExit('Pages list insertion point was not found.')

old_nav = """      NavItem('Appointment', Icons.work_outline_rounded),
      NavItem('Ranking', Icons.leaderboard_rounded),
    ];
"""
new_nav = """      NavItem('Appointment', Icons.work_outline_rounded),
      NavItem('Ranking', Icons.leaderboard_rounded),
      NavItem('Reports', Icons.summarize_rounded),
    ];
"""
if old_nav in text:
    text = text.replace(old_nav, new_nav, 1)
    changed = True
elif "NavItem('Reports'," in text:
    pass
else:
    raise SystemExit('Sidebar nav insertion point was not found.')

if changed:
    path.write_text(text, encoding='utf-8')
    print('Reports navigation patch applied to lib/main.dart')
else:
    print('Reports navigation is already present.')
