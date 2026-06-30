from pathlib import Path

p = Path('lib/main.dart')
s = p.read_text()

# Need bytes for browser PDF upload.
if "import 'dart:typed_data';" not in s:
    s = s.replace("import 'dart:html' as html;\n", "import 'dart:html' as html;\nimport 'dart:typed_data';\n", 1)

# Replace attachment text controller with uploaded file metadata.
s = s.replace(
    """  final TextEditingController attachment = TextEditingController();
  String status = '';""",
    """  String attachmentUrl = '';
  String attachmentFileName = '';
  bool uploadingAttachment = false;
  String status = '';""",
    1,
)
s = s.replace("""    attachment.dispose();\n""", "", 1)

# Add PDF picker/uploader helper after license status helper.
if 'Future<void> pickAndUploadLicensePdf(' not in s:
    s = s.replace(
        """String licenseStatusFromExpiry(String text) {
  final value = text.trim();
  if (value.isEmpty) return '';
  final parsed = DateTime.tryParse(value);
  if (parsed == null) return '';
  final todayNow = DateTime.now();
  final today = DateTime(todayNow.year, todayNow.month, todayNow.day);
  final expiry = DateTime(parsed.year, parsed.month, parsed.day);
  if (expiry.isBefore(today)) return 'Expired';
  if (expiry.difference(today).inDays <= 90) return 'For Renewal';
  return 'Active';
}
""",
        """String licenseStatusFromExpiry(String text) {
  final value = text.trim();
  if (value.isEmpty) return '';
  final parsed = DateTime.tryParse(value);
  if (parsed == null) return '';
  final todayNow = DateTime.now();
  final today = DateTime(todayNow.year, todayNow.month, todayNow.day);
  final expiry = DateTime(parsed.year, parsed.month, parsed.day);
  if (expiry.isBefore(today)) return 'Expired';
  if (expiry.difference(today).inDays <= 90) return 'For Renewal';
  return 'Active';
}

Future<void> pickAndUploadLicensePdf(BuildContext context, SelectedLicenseInput entry, StateSetter setDialogState) async {
  final input = html.FileUploadInputElement()
    ..accept = 'application/pdf,.pdf'
    ..multiple = false;
  input.click();
  await input.onChange.first;
  final file = input.files?.isNotEmpty == true ? input.files!.first : null;
  if (file == null) return;
  final lowerName = file.name.toLowerCase();
  if (!lowerName.endsWith('.pdf') && file.type != 'application/pdf') {
    showSnack(context, 'Only PDF files are allowed.');
    return;
  }
  setDialogState(() => entry.uploadingAttachment = true);
  try {
    final reader = html.FileReader();
    reader.readAsArrayBuffer(file);
    await reader.onLoad.first;
    final result = reader.result;
    late final Uint8List bytes;
    if (result is ByteBuffer) {
      bytes = Uint8List.view(result);
    } else if (result is Uint8List) {
      bytes = result;
    } else {
      throw Exception('Unable to read selected PDF file.');
    }
    final safeName = file.name.replaceAll(RegExp(r'[^A-Za-z0-9._-]+'), '_');
    final path = 'licenses/${DateTime.now().millisecondsSinceEpoch}_$safeName';
    await db.storage.from('hr-attachments').uploadBinary(path, bytes, fileOptions: const FileOptions(contentType: 'application/pdf', upsert: true));
    final url = db.storage.from('hr-attachments').getPublicUrl(path);
    setDialogState(() {
      entry.attachmentUrl = url;
      entry.attachmentFileName = file.name;
      entry.uploadingAttachment = false;
    });
  } catch (e) {
    setDialogState(() => entry.uploadingAttachment = false);
    showSnack(context, 'PDF upload failed: $e');
  }
}
""",
        1,
    )

# Replace Attachment (PDF) text input with a real PDF upload button.
s = s.replace(
    """                            Expanded(
                              flex: 2,
                              child: TextFormField(
                                controller: entry.attachment,
                                decoration: const InputDecoration(labelText: 'Attachment (PDF)', hintText: 'PDF URL'),
                              ),
                            ),""",
    """                            Expanded(
                              flex: 2,
                              child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                                OutlinedButton.icon(
                                  onPressed: entry.uploadingAttachment ? null : () => pickAndUploadLicensePdf(context, entry, setDialogState),
                                  icon: entry.uploadingAttachment
                                      ? const SizedBox(width: 16, height: 16, child: CircularProgressIndicator(strokeWidth: 2))
                                      : const Icon(Icons.picture_as_pdf_rounded),
                                  label: Text(entry.uploadingAttachment ? 'Uploading...' : (entry.attachmentFileName.isEmpty ? 'Attach PDF' : 'Change PDF')),
                                ),
                                const SizedBox(height: 6),
                                Text(
                                  entry.attachmentFileName.isEmpty ? 'No PDF attached' : entry.attachmentFileName,
                                  maxLines: 2,
                                  overflow: TextOverflow.ellipsis,
                                  style: TextStyle(fontSize: 12, color: entry.attachmentFileName.isEmpty ? _muted : _ink, fontWeight: FontWeight.w700),
                                ),
                              ]),
                            ),""",
    1,
)

# Require uploaded PDF before saving.
s = s.replace(
    """              final now = DateTime.now().toIso8601String();
              Navigator.pop(context, selected.values.map((entry) {""",
    """              final missingPdf = selected.values.where((entry) => entry.attachmentUrl.trim().isEmpty).toList();
              if (missingPdf.isNotEmpty) {
                showSnack(context, 'Please attach a PDF file for every selected license.');
                return;
              }
              final now = DateTime.now().toIso8601String();
              Navigator.pop(context, selected.values.map((entry) {""",
    1,
)

# Save uploaded URL, not typed text.
s = s.replace(
    """                  'attachment_url': entry.attachment.text.trim().isEmpty ? null : entry.attachment.text.trim(),""",
    """                  'attachment_url': entry.attachmentUrl.trim().isEmpty ? null : entry.attachmentUrl.trim(),""",
    1,
)

p.write_text(s)
