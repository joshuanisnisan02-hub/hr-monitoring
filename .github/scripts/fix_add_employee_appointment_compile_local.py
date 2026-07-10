from pathlib import Path

path = Path('lib/main.dart')
if not path.exists():
    raise SystemExit('Run this script from the Flutter project root. lib/main.dart was not found.')

text = path.read_text(encoding='utf-8-sig')
original = text

start = text.find('Future<AddEmployeeFullResult?> showAddEmployeeFullDialog')
end = text.find('Future<void> addEmployeeFull', start)
if start < 0 or end < 0:
    raise SystemExit('Could not locate showAddEmployeeFullDialog block.')

block = text[start:end]

# The previous Add Employee appointment section patch inserted UI/dispose items,
# but on some local code shapes it did not insert the controllers/state.
if 'final employeeAppointmentCategory = TextEditingController' not in block:
    insert_after = "  final contractStatus = TextEditingController(text: '');\n"
    declarations = """  final employeeAppointmentCategory = TextEditingController();
  final employeeAppointmentTitle = TextEditingController();
  final employeeAppointmentOtherDuties = TextEditingController();
  final employeeAppointmentType = TextEditingController();
  String employeeAppointmentAttachmentUrl = '';
  String employeeAppointmentAttachmentFileName = '';
  bool uploadingEmployeeAppointmentAttachment = false;
"""
    if insert_after in block:
        block = block.replace(insert_after, insert_after + declarations, 1)
    else:
        fallback = "  final contractEnd = TextEditingController(text: '');\n"
        if fallback in block:
            block = block.replace(fallback, fallback + declarations, 1)
        else:
            raise SystemExit('Could not find insertion point for appointment controllers.')

# Make sure appointmentRecord is created in the same scope as the
# AddEmployeeFullResult constructor call.
result_idx = block.find('AddEmployeeFullResult(')
if result_idx < 0:
    raise SystemExit('Could not find AddEmployeeFullResult constructor call.')
window_start = max(0, result_idx - 2500)
if 'final appointmentRecord = <String, dynamic>{' not in block[window_start:result_idx]:
    nav_idx = block.rfind('Navigator.pop', 0, result_idx)
    if nav_idx < 0:
        raise SystemExit('Could not find Navigator.pop before AddEmployeeFullResult.')
    line_start = block.rfind('\n', 0, nav_idx) + 1
    indent = block[line_start:nav_idx]
    appointment_record = (
        f"{indent}final appointmentRecord = <String, dynamic>{{\n"
        f"{indent}  'category': employeeAppointmentCategory.text.trim(),\n"
        f"{indent}  'appointment_title': employeeAppointmentTitle.text.trim(),\n"
        f"{indent}  'other_duties': employeeAppointmentOtherDuties.text.trim(),\n"
        f"{indent}  'appointment_type': employeeAppointmentType.text.trim(),\n"
        f"{indent}  'attachment_url': employeeAppointmentAttachmentUrl.trim(),\n"
        f"{indent}}}..removeWhere((_, value) =>\n"
        f"{indent}    value == null || value.toString().trim().isEmpty);\n"
    )
    block = block[:nav_idx] + appointment_record + block[nav_idx:]

# If appointment argument was not inserted, add it after educationBackgrounds.
if 'appointment: appointmentRecord' not in block:
    block = block.replace(
        'educationBackgrounds: educationRecords,',
        'educationBackgrounds: educationRecords,\n                    appointment: appointmentRecord,',
        1,
    )

# Make sure the AddEmployeeFullResult data class has appointment field/required arg.
class_start = text.find('class AddEmployeeFullResult {')
class_end = text.find('Future<AddEmployeeFullResult?> showAddEmployeeFullDialog', class_start)
class_block = text[class_start:class_end] if class_start >= 0 and class_end > class_start else ''
if class_block and 'final Map<String, dynamic> appointment;' not in class_block:
    class_block = class_block.replace(
        '  final List<Map<String, dynamic>> educationBackgrounds;\n',
        '  final List<Map<String, dynamic>> educationBackgrounds;\n  final Map<String, dynamic> appointment;\n',
        1,
    )
    class_block = class_block.replace(
        '    required this.educationBackgrounds,\n  });',
        '    required this.educationBackgrounds,\n    required this.appointment,\n  });',
        1,
    )
    text = text[:class_start] + class_block + text[class_end:]
    # Recompute locations after class edit.
    start = text.find('Future<AddEmployeeFullResult?> showAddEmployeeFullDialog')
    end = text.find('Future<void> addEmployeeFull', start)

text = text[:start] + block + text[end:]

path.write_text(text, encoding='utf-8')
if text == original:
    print('No changes applied. Add Employee appointment compile issue may already be fixed.')
else:
    print('Fixed Add Employee appointment controllers and appointmentRecord scope.')
