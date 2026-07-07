from pathlib import Path
import re

path = Path('lib/main.dart')
if not path.exists():
    raise SystemExit('Run this script from the Flutter project root. lib/main.dart was not found.')

text = path.read_text(encoding='utf-8-sig')
original = text

# The previous constructor fixer accidentally inserted a local variable into the
# AddEmployeeFullResult class body. Replace the entire class block with the
# correct data class.
start = text.find('class AddEmployeeFullResult {')
end = text.find('Future<AddEmployeeFullResult?> showAddEmployeeFullDialog', start)
if start < 0 or end < 0:
    raise SystemExit('Could not locate AddEmployeeFullResult class block.')

correct_class = '''class AddEmployeeFullResult {
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
text = text[:start] + correct_class + text[end:]

# Repair AddEmployeeFullResult constructor calls in showAddEmployeeFullDialog.
# If the call already has educationBackgrounds, this leaves it unchanged.
show_start = text.find('Future<AddEmployeeFullResult?> showAddEmployeeFullDialog')
show_end = text.find('Future<void> addEmployeeFull', show_start)
if show_start < 0 or show_end < 0:
    path.write_text(text, encoding='utf-8')
    raise SystemExit('Class block fixed, but showAddEmployeeFullDialog was not found.')

block = text[show_start:show_end]

# Add educationRecords before every AddEmployeeFullResult call if that call area
# does not already have the variable.
if 'educationRecords' not in block:
    cert_idx = block.rfind('final certificates = selectedCertificates.values')
    if cert_idx >= 0:
        end_list = block.find('.toList();', cert_idx)
        if end_list >= 0:
            end_list += len('.toList();')
            insertion = '''
              final educationRecords = educationBackgrounds
                  .where((entry) => entry.hasInput)
                  .map((entry) => entry.toMap())
                  .where((record) => record.isNotEmpty)
                  .toList();'''
            block = block[:end_list] + insertion + block[end_list:]

# Add missing educationBackgrounds parameter in constructor calls.
block = re.sub(
    r'(certificates:\s*certificates,\s*)(\n\s*\)\s*\)?\s*;?)',
    r'\1\n                    educationBackgrounds: educationRecords,\2',
    block,
)
block = block.replace(
    'educationBackgrounds: educationRecords,\n                    educationBackgrounds: educationRecords,',
    'educationBackgrounds: educationRecords,',
)
block = block.replace(
    'educationBackgrounds: educationRecords,\n          educationBackgrounds: educationRecords,',
    'educationBackgrounds: educationRecords,',
)

text = text[:show_start] + block + text[show_end:]

path.write_text(text, encoding='utf-8')
if text == original:
    print('No changes applied. AddEmployeeFullResult class may already be fixed.')
else:
    print('Fixed AddEmployeeFullResult class block and educationBackgrounds constructor parameter.')
