from pathlib import Path

p = Path('lib/main.dart')
s = p.read_text()

# Ensure employee options are sorted A-Z by display label.
s = s.replace(
    """Future<List<EditOption>> employeeOptions() async {
  final rows = await db.from('employees').select('id, full_name').order('full_name').limit(3000);
  return rows.map<EditOption>((r) => EditOption(r['id'].toString(), formatValue(r['full_name']))).toList();
}""",
    """Future<List<EditOption>> employeeOptions() async {
  final rows = await db.from('employees').select('id, full_name').order('full_name').limit(3000);
  final out = rows.map<EditOption>((r) => EditOption(r['id'].toString(), formatValue(r['full_name']))).toList();
  out.sort((a, b) => a.label.toLowerCase().compareTo(b.label.toLowerCase()));
  return out;
}""",
    1,
)

old_block = """                if (isAdd)
                  SizedBox(
                    width: 354,
                    child: DropdownButtonFormField<String>(
                      value: employeeId,
                      isExpanded: true,
                      hint: const Text('Select Employee'),
                      decoration: const InputDecoration(labelText: 'Employee Name'),
                      items: uniqueOptions(employees).map((o) => DropdownMenuItem<String>(value: o.value, child: Text(o.label, overflow: TextOverflow.ellipsis))).toList(),
                      validator: (v) => v == null || v.isEmpty ? 'Please select employee' : null,
                      onChanged: (v) => setDialogState(() {
                        employeeId = v;
                        appointment.text = v == null ? '' : (appointmentByEmployee[v] ?? '');
                      }),
                    ),
                  )
                else"""

new_block = """                if (isAdd)
                  SizedBox(
                    width: 354,
                    child: Autocomplete<EditOption>(
                      displayStringForOption: (option) => option.label,
                      optionsBuilder: (textEditingValue) {
                        final sortedEmployees = uniqueOptions(employees).toList()
                          ..sort((a, b) => a.label.toLowerCase().compareTo(b.label.toLowerCase()));
                        final query = textEditingValue.text.trim().toLowerCase();
                        if (query.isEmpty) return sortedEmployees;
                        final normalizedQuery = normalizeName(query);
                        return sortedEmployees.where((option) {
                          final label = option.label.toLowerCase();
                          final normalizedLabel = normalizeName(option.label);
                          return label.contains(query) || normalizedLabel.contains(normalizedQuery);
                        });
                      },
                      onSelected: (option) => setDialogState(() {
                        employeeId = option.value;
                        appointment.text = appointmentByEmployee[option.value] ?? '';
                      }),
                      fieldViewBuilder: (context, textController, focusNode, onFieldSubmitted) => TextFormField(
                        controller: textController,
                        focusNode: focusNode,
                        decoration: const InputDecoration(
                          labelText: 'Employee Name',
                          hintText: 'Select or type employee name',
                          suffixIcon: Icon(Icons.search_rounded),
                        ),
                        validator: (_) => employeeId == null || employeeId!.isEmpty ? 'Please select employee from the list' : null,
                        onChanged: (value) => setDialogState(() {
                          final typed = value.trim().toLowerCase();
                          final exact = uniqueOptions(employees).where((option) => option.label.toLowerCase() == typed).toList();
                          if (exact.isNotEmpty) {
                            employeeId = exact.first.value;
                            appointment.text = appointmentByEmployee[exact.first.value] ?? '';
                          } else {
                            employeeId = null;
                            appointment.text = '';
                          }
                        }),
                      ),
                      optionsViewBuilder: (context, onSelected, options) => Align(
                        alignment: Alignment.topLeft,
                        child: Material(
                          elevation: 6,
                          borderRadius: BorderRadius.circular(14),
                          child: ConstrainedBox(
                            constraints: const BoxConstraints(maxWidth: 520, maxHeight: 320),
                            child: ListView.separated(
                              padding: EdgeInsets.zero,
                              shrinkWrap: true,
                              itemCount: options.length,
                              separatorBuilder: (_, __) => const Divider(height: 1),
                              itemBuilder: (context, index) {
                                final option = options.elementAt(index);
                                return ListTile(
                                  dense: true,
                                  title: Text(option.label, overflow: TextOverflow.ellipsis),
                                  onTap: () => onSelected(option),
                                );
                              },
                            ),
                          ),
                        ),
                      ),
                    ),
                  )
                else"""

if old_block not in s and new_block not in s:
    raise SystemExit('Add Ranking employee dropdown block not found')
s = s.replace(old_block, new_block, 1)

p.write_text(s)
