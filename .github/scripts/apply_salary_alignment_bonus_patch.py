from pathlib import Path

path = Path("lib/main.dart")
text = path.read_text(encoding="utf-8")


def replace_once(old: str, new: str) -> None:
    global text
    if old not in text:
        raise SystemExit(f"Required pattern not found:\n{old[:500]}")
    text = text.replace(old, new, 1)


def replace_all(old: str, new: str) -> None:
    global text
    if old not in text:
        raise SystemExit(f"Required pattern not found:\n{old[:500]}")
    text = text.replace(old, new)


if "const _salaryAlignmentBonusSurnames" in text:
    print("Salary alignment bonus patch is already applied.")
    raise SystemExit(0)

replace_once(
"""  String? employeeId = isAdd ? null : initial?['employee_id']?.toString();
  String? cycleId = optionValueOrFirst(initial?['cycle_id']?.toString(), cycles, true);
""",
"""  String? employeeId = isAdd ? null : initial?['employee_id']?.toString();
  String selectedEmployeeName = isAdd ? '' : linkedEmployeeName(initial);
  String? cycleId = optionValueOrFirst(initial?['cycle_id']?.toString(), cycles, true);
""",
)

replace_once(
"""                      onSelected: (option) => setDialogState(() {
                        employeeId = option.value;
                        appointment.text = appointmentByEmployee[option.value] ?? '';
                      }),
""",
"""                      onSelected: (option) => setDialogState(() {
                        employeeId = option.value;
                        selectedEmployeeName = option.label;
                        appointment.text = appointmentByEmployee[option.value] ?? '';
                        applyRankSalaryForEmployee(previousRank, previousSalary, ranks, selectedEmployeeName);
                        applyRankSalaryForEmployee(appliedRank, appliedSalary, ranks, selectedEmployeeName);
                      }),
""",
)

replace_once(
"""                          if (exact.isNotEmpty) {
                            employeeId = exact.first.value;
                            appointment.text = appointmentByEmployee[exact.first.value] ?? '';
                          } else {
                            employeeId = null;
                            appointment.text = '';
                          }
""",
"""                          if (exact.isNotEmpty) {
                            employeeId = exact.first.value;
                            selectedEmployeeName = exact.first.label;
                            appointment.text = appointmentByEmployee[exact.first.value] ?? '';
                            applyRankSalaryForEmployee(previousRank, previousSalary, ranks, selectedEmployeeName);
                            applyRankSalaryForEmployee(appliedRank, appliedSalary, ranks, selectedEmployeeName);
                          } else {
                            employeeId = null;
                            selectedEmployeeName = '';
                            appointment.text = '';
                          }
""",
)

replace_all(
"""rankAutocompleteBox('Previous Rank', previousRank, previousSalary, ranks)""",
"""rankAutocompleteBox('Previous Rank', previousRank, previousSalary, ranks, selectedEmployeeName)""",
)

replace_all(
"""rankAutocompleteBox('Applied Rank', appliedRank, appliedSalary, ranks)""",
"""rankAutocompleteBox('Applied Rank', appliedRank, appliedSalary, ranks, selectedEmployeeName)""",
)

replace_once(
"""Widget rankAutocompleteBox(String label, TextEditingController controller, TextEditingController salaryController, List<EditOption> ranks) => SizedBox(
""",
"""Widget rankAutocompleteBox(String label, TextEditingController controller, TextEditingController salaryController, List<EditOption> ranks, String employeeName) => SizedBox(
""",
)

replace_all(
"""if (option.salary != null) salaryController.text = formatMoney(option.salary);""",
"""if (option.salary != null) salaryController.text = formatMoney(adjustedRankSalary(option.salary!, employeeName));""",
)

replace_all(
"""if (exact.isNotEmpty && exact.first.salary != null) salaryController.text = formatMoney(exact.first.salary);""",
"""if (exact.isNotEmpty && exact.first.salary != null) salaryController.text = formatMoney(adjustedRankSalary(exact.first.salary!, employeeName));""",
)

replace_once(
"""Future<void> saveRow(BuildContext context, String table, Object? id, Map<String, dynamic> data, VoidCallback refresh) async {
""",
"""const _salaryAlignmentBonusSurnames = <String>{'saulong', 'epil', 'roderos', 'flores', 'saligumba'};

bool hasSalaryAlignmentBonus(Object? employeeName) {
  final normalized = normalizeName('${employeeName ?? ''}'.replaceAll(RegExp(r'[^A-Za-z0-9 ]+'), ' '));
  if (normalized.isEmpty) return false;
  final parts = normalized.split(RegExp(r'\\s+'));
  return parts.any(_salaryAlignmentBonusSurnames.contains);
}

num adjustedRankSalary(num salary, Object? employeeName) => salary + (hasSalaryAlignmentBonus(employeeName) ? 1000 : 0);

EditOption? matchedRankOption(List<EditOption> ranks, String rankText) {
  final key = normalizeRankKey(rankText);
  if (key.isEmpty) return null;
  for (final option in uniqueOptions(ranks)) {
    if (normalizeRankKey(option.value) == key) return option;
  }
  return null;
}

void applyRankSalaryForEmployee(TextEditingController rankController, TextEditingController salaryController, List<EditOption> ranks, Object? employeeName) {
  final option = matchedRankOption(ranks, rankController.text);
  if (option?.salary == null) return;
  salaryController.text = formatMoney(adjustedRankSalary(option!.salary!, employeeName));
}

Future<void> saveRow(BuildContext context, String table, Object? id, Map<String, dynamic> data, VoidCallback refresh) async {
""",
)

path.write_text(text, encoding="utf-8")
print("Salary alignment bonus patch applied to lib/main.dart")
