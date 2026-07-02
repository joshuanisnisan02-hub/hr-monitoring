from pathlib import Path
p = Path('lib/main.dart')
s = p.read_text()
old = """                textBox('Duration In Months', durationMonths, kind: FieldKind.integer),
"""
new = """                SizedBox(
                  width: 354,
                  child: TextFormField(
                    controller: durationMonths,
                    keyboardType: TextInputType.number,
                    decoration: const InputDecoration(labelText: 'Duration In Months'),
                    validator: (v) {
                      final text = (v ?? '').trim();
                      if (text.isEmpty) return null;
                      return int.tryParse(text.replaceAll(RegExp(r'[^0-9-]'), '')) == null ? 'Enter a valid month count' : null;
                    },
                  ),
                ),
"""
if old in s:
    s = s.replace(old, new, 1)
elif new not in s:
    raise SystemExit('duration field line not found')
p.write_text(s)
