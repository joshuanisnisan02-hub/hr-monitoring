from pathlib import Path

path = Path('lib/main.dart')
if not path.exists():
    raise SystemExit('Run this script from the Flutter project root. lib/main.dart was not found.')

text = path.read_text(encoding='utf-8-sig')
original = text

# Keep the Display Names selector in the same left-side position.
# Only fix the clipped/cut floating label by removing the forced 44px height
# and giving the form field enough vertical padding.
marker = "const InputDecoration(labelText: 'Display Names')"
marker_index = text.find(marker)
if marker_index < 0:
    raise SystemExit('Could not find the Display Names dropdown. It may have already been changed.')

start = text.rfind("            if (widget.pageSizeOptions.length > 1) ...[", 0, marker_index)
end = text.find("            const SizedBox(height:", marker_index)
if start < 0 or end < 0:
    raise SystemExit('Could not safely locate the full Display Names block.')
end_line = text.find('\n', end)
if end_line < 0:
    end_line = end

new_block = """            if (widget.pageSizeOptions.length > 1) ...[
              const SizedBox(height: 4),
              Align(
                alignment: Alignment.centerLeft,
                child: SizedBox(
                  width: 220,
                  child: DropdownButtonFormField<int>(
                    value: pageSize,
                    isExpanded: true,
                    isDense: false,
                    itemHeight: 48,
                    decoration: InputDecoration(
                      labelText: 'Display Names',
                      floatingLabelBehavior: FloatingLabelBehavior.always,
                      contentPadding:
                          const EdgeInsets.fromLTRB(16, 18, 12, 12),
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(20),
                      ),
                      enabledBorder: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(20),
                        borderSide: const BorderSide(color: _line),
                      ),
                      focusedBorder: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(20),
                        borderSide: const BorderSide(color: _primary, width: 1.6),
                      ),
                    ),
                    items: widget.pageSizeOptions
                        .map((value) => DropdownMenuItem<int>(
                              value: value,
                              child: Text('$value per page'),
                            ))
                        .toList(),
                    onChanged: (value) => setState(() {
                      pageSize = value ?? pageSize;
                      page = 0;
                      WidgetsBinding.instance
                          .addPostFrameCallback((_) => scrollBothToTop());
                    }),
                  ),
                ),
              ),
            ],
            const SizedBox(height: 14),
"""

text = text[:start] + new_block + text[end_line + 1:]
path.write_text(text, encoding='utf-8')

if text == original:
    print('No changes applied. Display Names selector may already be fixed.')
else:
    print('Fixed Display Names clipped label while keeping the selector in the same position.')
