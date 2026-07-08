from pathlib import Path
import re

path = Path('lib/main.dart')
if not path.exists():
    raise SystemExit('Run this script from the Flutter project root. lib/main.dart was not found.')

text = path.read_text(encoding='utf-8-sig')
original = text

# 1) Repair the AddEmployeeFullResult class block if a previous script inserted
# educationRecords inside the class.
start = text.find('class AddEmployeeFullResult {')
end = text.find('Future<AddEmployeeFullResult?> showAddEmployeeFullDialog', start)
if start >= 0 and end > start:
    correct = '''class AddEmployeeFullResult {
  final Map<String, dynamic> employee;
  final Map<String, dynamic> contract;
  final List<Map<String, dynamic>> licenses;
  final List<Map<String, dynamic>> certificates;
  final List<Map<String, dynamic>> educationBackgrounds;

  const AddEmployeeFullResult({
    required this.employee,
    required this.contract,
    required this.licenses,
    required this.certificates,
    required this.educationBackgrounds,
  });
}

'''
    text = text[:start] + correct + text[end:]

# 2) Convert education background status from free text into a dropdown.
if 'const educationBackgroundStatusOptions' not in text:
    marker = 'class EducationBackgroundInput {'
    text = text.replace(
        marker,
        "const educationBackgroundStatusOptions = ['Completed', 'On-going', 'Undergraduate'];\n\n" + marker,
        1,
    )

# Ensure default status value is one of the dropdown values.
text = text.replace(
    "final TextEditingController status = TextEditingController();",
    "final TextEditingController status = TextEditingController(text: 'Completed');",
    1,
)

# Replace the status TextFormField block inside educationBackgroundInputCard.
old_status_block = '''          SizedBox(
            width: 164,
            child: TextFormField(
              controller: entry.status,
              decoration: const InputDecoration(labelText: 'Status'),
            ),
          ),'''
new_status_block = '''          SizedBox(
            width: 164,
            child: DropdownButtonFormField<String>(
              value: educationBackgroundStatusOptions.contains(entry.status.text)
                  ? entry.status.text
                  : 'Completed',
              decoration: const InputDecoration(labelText: 'Status'),
              items: educationBackgroundStatusOptions
                  .map((status) => DropdownMenuItem<String>(
                        value: status,
                        child: Text(status),
                      ))
                  .toList(),
              onChanged: (value) =>
                  setDialogState(() => entry.status.text = value ?? 'Completed'),
            ),
          ),'''
text = text.replace(old_status_block, new_status_block, 1)

# If the field was formatted differently, use a targeted fallback around the label.
if old_status_block in text:
    text = text.replace(old_status_block, new_status_block, 1)

# 3) Make sure clear/remove resets dropdown back to Completed.
text = text.replace("entry.status.clear();", "entry.status.text = 'Completed';")

# 4) Make AddEmployeeFullResult constructor calls include educationBackgrounds.
show_start = text.find('Future<AddEmployeeFullResult?> showAddEmployeeFullDialog')
show_end = text.find('Future<void> addEmployeeFull', show_start)
if show_start >= 0 and show_end > show_start:
    block = text[show_start:show_end]

    if 'final educationRecords = educationBackgrounds' not in block:
        cert_pos = block.rfind('final certificates = selectedCertificates.values')
        if cert_pos >= 0:
            cert_end = block.find('.toList();', cert_pos)
            if cert_end >= 0:
                cert_end += len('.toList();')
                insertion = '''
              final educationRecords = educationBackgrounds
                  .where((entry) => entry.hasInput)
                  .map((entry) => entry.toMap())
                  .where((record) => record.isNotEmpty)
                  .toList();'''
                block = block[:cert_end] + insertion + block[cert_end:]

    # Add the named parameter only where missing.
    result_positions = [m.start() for m in re.finditer(r'AddEmployeeFullResult\(', block)]
    for pos in reversed(result_positions):
        close_search = block.find('));', pos)
        if close_search < 0:
            close_search = block.find('),', pos)
        if close_search < 0:
            continue
        call = block[pos:close_search]
        if 'educationBackgrounds:' in call:
            continue
        cert_arg = call.find('certificates: certificates,')
        if cert_arg >= 0:
            insert_at = pos + cert_arg + len('certificates: certificates,')
            block = (block[:insert_at] +
                     '\n                    educationBackgrounds: educationRecords,' +
                     block[insert_at:])

    # Remove accidental duplicates.
    block = re.sub(
        r'(educationBackgrounds:\s*educationRecords,\s*){2,}',
        'educationBackgrounds: educationRecords,\n',
        block,
    )
    text = text[:show_start] + block + text[show_end:]

path.write_text(text, encoding='utf-8')
if text == original:
    print('No changes applied. Education status dropdown and result class may already be fixed.')
else:
    print('Fixed education background result class and changed status to dropdown.')
