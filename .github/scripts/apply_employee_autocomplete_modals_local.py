from pathlib import Path

path = Path('lib/main.dart')
if not path.exists():
    raise SystemExit('Run this script from the Flutter project root. lib/main.dart was not found.')

text = path.read_text(encoding='utf-8')
original = text

helper = r'''
Widget employeeAutocompleteField({
  required List<EditOption> employees,
  required String? employeeId,
  required ValueChanged<String?> onEmployeeChanged,
  double width = 354,
}) =>
    SizedBox(
      width: width,
      child: Autocomplete<EditOption>(
        displayStringForOption: (option) => option.label,
        optionsBuilder: (textEditingValue) {
          final sortedEmployees = uniqueOptions(employees).toList()
            ..sort((a, b) =>
                a.label.toLowerCase().compareTo(b.label.toLowerCase()));
          final query = textEditingValue.text.trim().toLowerCase();
          if (query.isEmpty) return sortedEmployees;
          final normalizedQuery = normalizeName(query);
          return sortedEmployees.where((option) {
            final label = option.label.toLowerCase();
            final normalizedLabel = normalizeName(option.label);
            return label.contains(query) ||
                normalizedLabel.contains(normalizedQuery);
          });
        },
        onSelected: (option) => onEmployeeChanged(option.value),
        fieldViewBuilder:
            (context, textController, focusNode, onFieldSubmitted) =>
                TextFormField(
          controller: textController,
          focusNode: focusNode,
          decoration: const InputDecoration(
            labelText: 'Employee Name',
            hintText: 'Select or type employee name',
            suffixIcon: Icon(Icons.search_rounded),
          ),
          validator: (_) => employeeId == null || employeeId.isEmpty
              ? 'Please select employee from the list'
              : null,
          onChanged: (value) {
            final typed = value.trim().toLowerCase();
            final exact = uniqueOptions(employees)
                .where((option) => option.label.toLowerCase() == typed)
                .toList();
            if (exact.isNotEmpty) {
              onEmployeeChanged(exact.first.value);
            } else {
              onEmployeeChanged(null);
            }
          },
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
    );

'''

if 'Widget employeeAutocompleteField({' not in text:
    marker = 'class DialogSectionTitle extends StatelessWidget {'
    if marker not in text:
        raise SystemExit('Could not find DialogSectionTitle marker.')
    text = text.replace(marker, helper + marker, 1)

old_generic = r'''    if (f.kind == FieldKind.dropdown) {
      final opts = uniqueOptions(f.options);
      widgets.add(SizedBox(
        width: width,
        child: DropdownButtonFormField<String>(
          value: optionValueOrFirst(selected[f.key], opts, f.required),
          isExpanded: true,
          decoration: InputDecoration(labelText: f.label),
          items: opts
              .map((o) => DropdownMenuItem<String>(
                  value: o.value,
                  child: Text(o.label, overflow: TextOverflow.ellipsis)))
              .toList(),
          validator: (v) =>
              f.required && (v == null || v.isEmpty) ? 'Required' : null,
          onChanged: (v) => setDialogState(() => selected[f.key] = v),
        ),
      ));
      continue;
    }
'''
new_generic = r'''    if (f.kind == FieldKind.dropdown) {
      if (f.key == 'employee_id') {
        widgets.add(employeeAutocompleteField(
          employees: f.options,
          employeeId: selected[f.key],
          width: width,
          onEmployeeChanged: (value) =>
              setDialogState(() => selected[f.key] = value),
        ));
        continue;
      }
      final opts = uniqueOptions(f.options);
      widgets.add(SizedBox(
        width: width,
        child: DropdownButtonFormField<String>(
          value: optionValueOrFirst(selected[f.key], opts, f.required),
          isExpanded: true,
          decoration: InputDecoration(labelText: f.label),
          items: opts
              .map((o) => DropdownMenuItem<String>(
                  value: o.value,
                  child: Text(o.label, overflow: TextOverflow.ellipsis)))
              .toList(),
          validator: (v) =>
              f.required && (v == null || v.isEmpty) ? 'Required' : null,
          onChanged: (v) => setDialogState(() => selected[f.key] = v),
        ),
      ));
      continue;
    }
'''
if old_generic in text:
    text = text.replace(old_generic, new_generic, 1)

old_dropdown = r'''                    SizedBox(
                      width: 430,
                      child: DropdownButtonFormField<String>(
                        value: employeeId,
                        isExpanded: true,
                        hint: const Text('Select Employee'),
                        decoration:
                            const InputDecoration(labelText: 'Employee Name'),
                        items: uniqueOptions(employees)
                            .map((o) => DropdownMenuItem<String>(
                                value: o.value,
                                child: Text(o.label,
                                    overflow: TextOverflow.ellipsis)))
                            .toList(),
                        validator: (v) => v == null || v.isEmpty
                            ? 'Please select employee'
                            : null,
                        onChanged: (v) => setDialogState(() => employeeId = v),
                      ),
                    ),
'''
new_dropdown = r'''                    employeeAutocompleteField(
                      employees: employees,
                      employeeId: employeeId,
                      width: 430,
                      onEmployeeChanged: (value) =>
                          setDialogState(() => employeeId = value),
                    ),
'''
text = text.replace(old_dropdown, new_dropdown)

if text == original:
    print('No changes applied. Employee autocomplete may already be applied.')
else:
    path.write_text(text, encoding='utf-8')
    print('Applied ranking-style employee autocomplete to add modals.')
