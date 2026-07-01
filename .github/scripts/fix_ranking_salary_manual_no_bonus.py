from pathlib import Path

path = Path('lib/main.dart')
text = path.read_text(encoding='utf-8')

replacements = {
    "textBox('Previous Salary', previousSalary, kind: FieldKind.number, readOnly: true)": "textBox('Previous Salary', previousSalary, kind: FieldKind.number)",
    "formatMoney(adjustedRankSalary(option.salary!, employeeName))": "formatMoney(option.salary)",
    "formatMoney(adjustedRankSalary(exact.first.salary!, employeeName))": "formatMoney(exact.first.salary)",
    "formatMoney(adjustedRankSalary(option!.salary!, employeeName))": "formatMoney(option!.salary)",
    "num adjustedRankSalary(num salary, Object? employeeName) => salary + (hasSalaryAlignmentBonus(employeeName) ? 1000 : 0);": "num adjustedRankSalary(num salary, Object? employeeName) => salary;",
    "Select Employee, then pick the Previous Rank to auto-fill Previous Salary. Applied rank and points can be updated later using Edit.": "Select Employee, then pick the Previous Rank to auto-fill Previous Salary. You can still manually edit the Previous Salary before saving. Applied rank and points can be updated later using Edit.",
}

changed = False
for old, new in replacements.items():
    if old in text:
        text = text.replace(old, new)
        changed = True

if "adjustedRankSalary(option.salary!" in text or "adjustedRankSalary(exact.first.salary!" in text or "hasSalaryAlignmentBonus(employeeName) ? 1000" in text:
    raise SystemExit('Could not remove all salary bonus usages. Please inspect lib/main.dart manually.')

if changed:
    path.write_text(text, encoding='utf-8')
    print('Ranking salary manual/no-bonus fix applied to lib/main.dart')
else:
    print('Ranking salary manual/no-bonus fix is already applied.')
