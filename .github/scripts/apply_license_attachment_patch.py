from pathlib import Path

p = Path('lib/main.dart')
s = p.read_text()

# Remove Issued column from Licenses table.
s = s.replace("          GridCol('issued_date', 'Issued'),\n", "", 1)

# Add attachment controller to selected license row model.
s = s.replace(
    """class SelectedLicenseInput {
  final String name;
  final TextEditingController number = TextEditingController();
  final TextEditingController expiry = TextEditingController();
  String status = '';

  SelectedLicenseInput(this.name);

  void dispose() {
    number.dispose();
    expiry.dispose();
  }
}""",
    """class SelectedLicenseInput {
  final String name;
  final TextEditingController number = TextEditingController();
  final TextEditingController expiry = TextEditingController();
  final TextEditingController attachment = TextEditingController();
  String status = '';

  SelectedLicenseInput(this.name);

  void dispose() {
    number.dispose();
    expiry.dispose();
    attachment.dispose();
  }
}""",
    1,
)

# Widen modal for the added table column.
s = s.replace("""          width: 900,""", """          width: 1040,""", 1)

# Add Attachment (PDF) header in selected license table.
s = s.replace(
    """                          Expanded(flex: 2, child: Text('Expiry Date', style: TextStyle(fontWeight: FontWeight.w900, color: _ink))),
                          SizedBox(width: 10),
                          SizedBox(width: 130, child: Text('Status', style: TextStyle(fontWeight: FontWeight.w900, color: _ink))),""",
    """                          Expanded(flex: 2, child: Text('Expiry Date', style: TextStyle(fontWeight: FontWeight.w900, color: _ink))),
                          SizedBox(width: 10),
                          Expanded(flex: 2, child: Text('Attachment (PDF)', style: TextStyle(fontWeight: FontWeight.w900, color: _ink))),
                          SizedBox(width: 10),
                          SizedBox(width: 130, child: Text('Status', style: TextStyle(fontWeight: FontWeight.w900, color: _ink))),""",
    1,
)

# Add Attachment (PDF) input after expiry date field.
s = s.replace(
    """                            const SizedBox(width: 10),
                            SizedBox(width: 130, child: Padding(padding: const EdgeInsets.only(top: 10), child: StatusChip(entry.status.isEmpty ? '-' : entry.status))),""",
    """                            const SizedBox(width: 10),
                            Expanded(
                              flex: 2,
                              child: TextFormField(
                                controller: entry.attachment,
                                decoration: const InputDecoration(labelText: 'Attachment (PDF)', hintText: 'PDF URL'),
                              ),
                            ),
                            const SizedBox(width: 10),
                            SizedBox(width: 130, child: Padding(padding: const EdgeInsets.only(top: 10), child: StatusChip(entry.status.isEmpty ? '-' : entry.status))),""",
    1,
)

# Save attachment URL per selected license.
s = s.replace(
    """                  'expiry_date': entry.expiry.text.trim(),
                  'status': status.isEmpty ? null : status,""",
    """                  'expiry_date': entry.expiry.text.trim(),
                  'attachment_url': entry.attachment.text.trim().isEmpty ? null : entry.attachment.text.trim(),
                  'status': status.isEmpty ? null : status,""",
    1,
)

p.write_text(s)
