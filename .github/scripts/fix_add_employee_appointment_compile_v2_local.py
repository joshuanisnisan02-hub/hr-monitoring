from pathlib import Path

p = Path('lib/main.dart')
if not p.exists():
    raise SystemExit('Run from project root')
s = p.read_text(encoding='utf-8-sig')
o = s

start = s.find('Future<AddEmployeeFullResult?> showAddEmployeeFullDialog')
end = s.find('Future<void> addEmployeeFull', start)
if start < 0 or end < 0:
    raise SystemExit('Could not locate showAddEmployeeFullDialog block')
block = s[start:end]

if 'final employeeAppointmentCategory =' not in block:
    insert_text = """  final employeeAppointmentCategory = TextEditingController();
  final employeeAppointmentTitle = TextEditingController();
  final employeeAppointmentOtherDuties = TextEditingController();
  final employeeAppointmentType = TextEditingController();
  String employeeAppointmentAttachmentUrl = '';
  String employeeAppointmentAttachmentFileName = '';
  bool uploadingEmployeeAppointmentAttachment = false;
"""
    anchors = [
        "  final contractStatus = TextEditingController(text: '');",
        "  final contractStatus = TextEditingController",
        "  final selectedLicenses",
    ]
    done = False
    for a in anchors:
        idx = block.find(a)
        if idx >= 0:
            if a == "  final selectedLicenses":
                block = block[:idx] + insert_text + block[idx:]
            else:
                line_end = block.find('\n', idx)
                block = block[:line_end + 1] + insert_text + block[line_end + 1:]
            done = True
            break
    if not done:
        raise SystemExit('Could not insert appointment controllers')

if 'final appointmentRecord = <String, dynamic>{' not in block:
    call_idx = block.find('AddEmployeeFullResult(')
    if call_idx < 0:
        raise SystemExit('Could not find AddEmployeeFullResult call')
    nav_idx = block.rfind('Navigator.pop', 0, call_idx)
    insert_at = nav_idx if nav_idx >= 0 else call_idx
    snippet = r'''              final appointmentRecord = <String, dynamic>{
                'category': employeeAppointmentCategory.text.trim(),
                'appointment_title': employeeAppointmentTitle.text.trim(),
                'other_duties': employeeAppointmentOtherDuties.text.trim(),
                'appointment_type': employeeAppointmentType.text.trim(),
                'attachment_url': employeeAppointmentAttachmentUrl.trim(),
              }..removeWhere((_, value) =>
                  value == null || value.toString().trim().isEmpty);
'''
    block = block[:insert_at] + snippet + block[insert_at:]

call_idx = block.find('AddEmployeeFullResult(')
if call_idx >= 0:
    close_idx = block.find('));', call_idx)
    if close_idx < 0:
        close_idx = block.find('),', call_idx)
    if close_idx > call_idx:
        call = block[call_idx:close_idx]
        if 'appointment:' not in call:
            needle = 'educationBackgrounds: educationRecords,'
            pos = block.find(needle, call_idx, close_idx)
            if pos >= 0:
                pos += len(needle)
                block = block[:pos] + '\n                    appointment: appointmentRecord,' + block[pos:]

s = s[:start] + block + s[end:]
p.write_text(s, encoding='utf-8')
if s == o:
    print('No changes applied. Appointment compile fix may already be present.')
else:
    print('Fixed Add Employee appointment compile errors.')
