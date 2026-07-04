from pathlib import Path

path = Path('lib/main.dart')
if not path.exists():
    raise SystemExit('Run this script from the Flutter project root. lib/main.dart was not found.')

text = path.read_text(encoding='utf-8-sig')
original = text

# Restore the Display Names selector to the same left-side form-field style,
# then only fix the clipped label by removing the too-small fixed height.
block_start_marker = "            if (widget.pageSizeOptions.length > 1) ...["
marker_index = text.find(block_start_marker)
if marker_index < 0:
    raise SystemExit('Could not find Display Names page-size block.')

# Prefer the block that contains pageSizeOptions/items or the Display label.
search_from = 0
block_start = -1
while True:
    candidate = text.find(block_start_marker, search_from)
    if candidate < 0:
        break
    candidate_end = text.find("            Expanded(", candidate)
    if candidate_end < 0:
        candidate_end = text.find("            const SizedBox(height:", candidate)
    snippet = text[candidate:candidate_end if candidate_end > 0 else candidate + 2500]
    if 'pageSizeOptions' in snippet or 'Display Names' in snippet:
        block_start = candidate
        break
    search_from = candidate + 1

if block_start < 0:
    raise SystemExit('Could not safely identify the Display Names selector block.')

# Replace everything from the Display Names conditional block to before the table Expanded.
block_end = text.find("            Expanded(", block_start)
if block_end < 0:
    raise SystemExit('Could not find table Expanded after Display Names selector.')

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

text = text[:block_start] + new_block + text[block_end:]
path.write_text(text, encoding='utf-8')

if text == original:
    print('No changes applied. Display Names selector may already match the requested style.')
else:
    print('Restored Display Names to the left-side form-field style and fixed the clipped label.')
