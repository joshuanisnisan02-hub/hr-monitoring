from pathlib import Path
import re

path = Path('lib/main.dart')
text = path.read_text(encoding='utf-8')

new_reports_getter = r'''  List<ReportConfig> get reports => [
        ReportConfig('Gender Summary Report', () => loadHrGenderSummaryReport(), const [
          GridCol('item', 'Gender', flex: 4, primary: true),
          GridCol('total', 'Total', isNumber: true),
        ]),
        ReportConfig('Ranks Summary Report', () => loadRankSummaryReport(), const [
          GridCol('item', 'Rank', flex: 4, primary: true),
          GridCol('total', 'Total', isNumber: true),
        ]),
        ReportConfig('Type of License Summary Report', () => loadLicenseTypeSummaryReport(), const [
          GridCol('item', 'Type of License', flex: 4, primary: true),
          GridCol('total', 'Total', isNumber: true),
        ]),
        ReportConfig('NC/TM Summary Report', () => loadNcTmSummaryReport(), const [
          GridCol('item', 'NC/TM', flex: 4, primary: true),
          GridCol('total', 'Total', isNumber: true),
        ]),
      ];
'''

text, count = re.subn(r"  List<ReportConfig> get reports => \[.*?\n      \];", new_reports_getter, text, count=1, flags=re.S)
if count == 0:
    raise SystemExit('Could not replace reports getter.')

text = text.replace("Select one category, then print only that category. Use Complete HR Summary Report only when you need all totals together.", "Select one category, then print that category as a simple two-column table.")
text = text.replace("subtitle: 'Print each summary category separately.',", "subtitle: 'Print each summary category separately in two-column table format.',")

path.write_text(text, encoding='utf-8')
print('Summary reports are now formatted as two-column category tables.')
