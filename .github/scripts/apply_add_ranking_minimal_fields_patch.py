from pathlib import Path

p = Path('lib/main.dart')
s = p.read_text()

old_fields = """                textBox('Appointment', appointment, readOnly: true),
                textBox('Points Earned', points, kind: FieldKind.number),
                textBox('Previous Rank', previousRank, readOnly: true),
                textBox('Previous Salary', previousSalary, kind: FieldKind.number, readOnly: true),
                rankTextBox('Applied Rank', appliedRank, () => pickRank(appliedRank, appliedSalary)),
                textBox('Applied Salary', appliedSalary, kind: FieldKind.number),
                SizedBox(width: 728, child: Container(padding: const EdgeInsets.all(12), decoration: BoxDecoration(color: const Color(0xFFEFF6FF), borderRadius: BorderRadius.circular(16)), child: Text(isAdd ? 'Select Employee first. The Appointment field will be filled automatically when an existing appointment is found for the selected employee.' : 'Employee name is locked here. Use the table Approve button to approve the applied rank.', style: const TextStyle(color: Color(0xFF1E3A8A), fontWeight: FontWeight.w600)))),"""

new_fields = """                textBox('Appointment', appointment, readOnly: true),
                if (isAdd)
                  rankTextBox('Previous Rank', previousRank, () => pickRank(previousRank, previousSalary))
                else
                  textBox('Previous Rank', previousRank, readOnly: true),
                textBox('Previous Salary', previousSalary, kind: FieldKind.number, readOnly: true),
                if (!isAdd) ...[
                  textBox('Points Earned', points, kind: FieldKind.number),
                  rankTextBox('Applied Rank', appliedRank, () => pickRank(appliedRank, appliedSalary)),
                  textBox('Applied Salary', appliedSalary, kind: FieldKind.number),
                ],
                SizedBox(width: 728, child: Container(padding: const EdgeInsets.all(12), decoration: BoxDecoration(color: const Color(0xFFEFF6FF), borderRadius: BorderRadius.circular(16)), child: Text(isAdd ? 'Select Employee, then pick the Previous Rank to auto-fill Previous Salary. Applied rank and points can be updated later using Edit.' : 'Employee name is locked here. Use the table Approve button to approve the applied rank.', style: const TextStyle(color: Color(0xFF1E3A8A), fontWeight: FontWeight.w600)))),"""

if old_fields not in s:
    raise SystemExit('Ranking dialog field block not found')
s = s.replace(old_fields, new_fields, 1)

old_pop = """              Navigator.of(context, rootNavigator: true).pop({
                'employee_id': isAdd ? emptyToNull(employeeId) : initial?['employee_id'],
                'cycle_id': emptyToNull(cycleId),
                'appointment': emptyToNull(appointment.text),
                'previous_rank_text': emptyToNull(previousRank.text),
                'previous_salary': parseMoneyInput(previousSalary.text),
                'applied_rank_text': emptyToNull(appliedRank.text),
                'applied_salary': parseMoneyInput(appliedSalary.text),
                'points_earned': num.tryParse(points.text.trim()),
              });"""
new_pop = """              final out = <String, dynamic>{
                'employee_id': isAdd ? emptyToNull(employeeId) : initial?['employee_id'],
                'cycle_id': emptyToNull(cycleId),
                'appointment': emptyToNull(appointment.text),
                'previous_rank_text': emptyToNull(previousRank.text),
                'previous_salary': parseMoneyInput(previousSalary.text),
              };
              if (!isAdd) {
                out.addAll({
                  'applied_rank_text': emptyToNull(appliedRank.text),
                  'applied_salary': parseMoneyInput(appliedSalary.text),
                  'points_earned': num.tryParse(points.text.trim()),
                });
              }
              Navigator.of(context, rootNavigator: true).pop(out);"""

if old_pop not in s:
    raise SystemExit('Ranking dialog save block not found')
s = s.replace(old_pop, new_pop, 1)

p.write_text(s)
