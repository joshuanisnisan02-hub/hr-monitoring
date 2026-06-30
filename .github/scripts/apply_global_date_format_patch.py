from pathlib import Path

p = Path('lib/main.dart')
s = p.read_text()

# Use long readable date hints in general dialogs.
s = s.replace("""decoration: InputDecoration(labelText: f.label, hintText: f.kind == FieldKind.date ? 'YYYY-MM-DD' : null),""", """decoration: InputDecoration(labelText: f.label, hintText: f.kind == FieldKind.date ? 'January 02, 2026' : null),""", 1)

# License/certificate multi-select date hints and validation.
s = s.replace("""decoration: const InputDecoration(labelText: 'Expiry Date', hintText: 'YYYY-MM-DD'),""", """decoration: const InputDecoration(labelText: 'Expiry Date', hintText: 'January 02, 2026'),""")
s = s.replace("""if (DateTime.tryParse(v.trim()) == null) return 'Use YYYY-MM-DD';""", """if (parseFlexibleDate(v.trim()) == null) return 'Use January 02, 2026';""")

# Save normalized ISO date values from multi-select dialogs even when user types January 02, 2026.
s = s.replace("""                  'expiry_date': entry.expiry.text.trim(),
                  'attachment_url': entry.attachmentUrl.trim().isEmpty ? null : entry.attachmentUrl.trim(),""", """                  'expiry_date': toIsoDateInput(entry.expiry.text),
                  'attachment_url': entry.attachmentUrl.trim().isEmpty ? null : entry.attachmentUrl.trim(),""")

# parseFieldValue should parse date fields into ISO date for Supabase.
s = s.replace(
    """Object? parseFieldValue(String text, FieldKind kind) {
  final value = text.trim();
  if (value.isEmpty) return null;
  if (kind == FieldKind.number) return num.tryParse(value);
  if (kind == FieldKind.integer) return int.tryParse(value);
  return value;
}""",
    """Object? parseFieldValue(String text, FieldKind kind) {
  final value = text.trim();
  if (value.isEmpty) return null;
  if (kind == FieldKind.number) return num.tryParse(value.replaceAll(RegExp(r'[^0-9.\\-]'), ''));
  if (kind == FieldKind.integer) return int.tryParse(value.replaceAll(RegExp(r'[^0-9\\-]'), ''));
  if (kind == FieldKind.date) return toIsoDateInput(value);
  return value;
}""",
    1,
)

# Replace formatValue block with date-aware formatting helpers.
s = s.replace(
    """String formatValue(Object? value) {
  if (value == null) return '-';
  final text = value.toString();
  if (text.trim().isEmpty) return '-';
  if (RegExp(r'^\\d{4}-\\d{2}-\\d{2}').hasMatch(text)) return text.substring(0, 10);
  return text;
}

String formatEditValue(Object? value) => value == null ? '' : formatValue(value) == '-' ? '' : formatValue(value);
""",
    """bool looksLikeDateText(String text) => RegExp(r'^\\d{4}-\\d{2}-\\d{2}').hasMatch(text.trim()) || RegExp(r'^[A-Za-z]+\\s+\\d{1,2},\\s*\\d{4}$').hasMatch(text.trim()) || RegExp(r'^\\d{1,2}[-/]\\d{1,2}[-/]\\d{4}$').hasMatch(text.trim());

DateTime? parseFlexibleDate(Object? value) {
  if (value == null) return null;
  final text = value.toString().trim();
  if (text.isEmpty || text == '-') return null;
  final iso = RegExp(r'^(\\d{4})-(\\d{2})-(\\d{2})').firstMatch(text);
  if (iso != null) return DateTime.tryParse('${iso.group(1)}-${iso.group(2)}-${iso.group(3)}');
  for (final pattern in const ['MMMM dd, yyyy', 'MMMM d, yyyy', 'MMM dd, yyyy', 'MMM d, yyyy', 'MM-dd-yyyy', 'M-d-yyyy', 'MM/dd/yyyy', 'M/d/yyyy']) {
    try {
      return DateFormat(pattern).parseStrict(text);
    } catch (_) {}
  }
  return null;
}

String formatDateLong(Object? value) {
  final parsed = parseFlexibleDate(value);
  if (parsed == null) return formatValueRaw(value);
  return DateFormat('MMMM dd, yyyy').format(parsed);
}

String? toIsoDateInput(Object? value) {
  final parsed = parseFlexibleDate(value);
  if (parsed == null) return value == null || value.toString().trim().isEmpty ? null : value.toString().trim();
  return DateFormat('yyyy-MM-dd').format(parsed);
}

String formatValueRaw(Object? value) {
  if (value == null) return '-';
  final text = value.toString();
  if (text.trim().isEmpty) return '-';
  return text;
}

String formatValue(Object? value) {
  if (value == null) return '-';
  final text = value.toString();
  if (text.trim().isEmpty) return '-';
  if (looksLikeDateText(text)) return formatDateLong(text);
  return text;
}

String formatEditValue(Object? value) {
  if (value == null) return '';
  final raw = formatValueRaw(value);
  if (raw == '-') return '';
  return looksLikeDateText(raw) ? formatDateLong(raw) : raw;
}
""",
    1,
)

# Detail values should render any date-ish field with the long format.
s = s.replace(
    """String formatDetailValue(Object? value, String key) {
  if (key.contains('salary')) return formatMoney(value);
  return formatValue(value);
}""",
    """String formatDetailValue(Object? value, String key) {
  if (key.contains('salary')) return formatMoney(value);
  if (key.contains('date')) return formatDateLong(value);
  return formatValue(value);
}""",
    1,
)

# daysLeft and status helpers should support the new typed format.
s = s.replace("""  final parsed = DateTime.tryParse(date.toString());""", """  final parsed = parseFlexibleDate(date);""", 1)
s = s.replace("""  final parsed = DateTime.tryParse(value);""", """  final parsed = parseFlexibleDate(value);""", 1)

# Search/print/report preview date display is already routed via formatValue/formatDetailValue.
p.write_text(s)
