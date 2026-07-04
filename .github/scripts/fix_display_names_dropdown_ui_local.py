from pathlib import Path

path = Path('lib/main.dart')
if not path.exists():
    raise SystemExit('Run this script from the Flutter project root. lib/main.dart was not found.')

text = path.read_text(encoding='utf-8-sig')
original = text

old = """            if (widget.pageSizeOptions.length > 1) ...[
              const SizedBox(height: 4),
              Align(
                alignment: Alignment.centerLeft,
                child: SizedBox(
                  width: 220,
                  height: 44,
                  child: DropdownButtonFormField<int>(
                    value: pageSize,
                    isExpanded: true,
                    decoration:
                        const InputDecoration(labelText: 'Display Names'),
                    items: widget.pageSizeOptions
                        .map((value) => DropdownMenuItem<int>(
                            value: value, child: Text('$value per page')))
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

new = """            if (widget.pageSizeOptions.length > 1) ...[
              const SizedBox(height: 10),
              Align(
                alignment: Alignment.centerRight,
                child: Container(
                  height: 42,
                  padding: const EdgeInsets.symmetric(horizontal: 14),
                  decoration: BoxDecoration(
                    color: _surface,
                    borderRadius: BorderRadius.circular(999),
                    border: Border.all(color: _line),
                  ),
                  child: Row(mainAxisSize: MainAxisSize.min, children: [
                    const Icon(Icons.format_list_numbered_rounded,
                        size: 18, color: _accent),
                    const SizedBox(width: 8),
                    const Text('Display',
                        style: TextStyle(
                            color: _muted,
                            fontSize: 12.5,
                            fontWeight: FontWeight.w800)),
                    const SizedBox(width: 10),
                    DropdownButtonHideUnderline(
                      child: DropdownButton<int>(
                        value: pageSize,
                        borderRadius: BorderRadius.circular(16),
                        isDense: true,
                        icon: const Icon(Icons.keyboard_arrow_down_rounded,
                            size: 20),
                        style: const TextStyle(
                            color: _ink,
                            fontSize: 13,
                            fontWeight: FontWeight.w800),
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
                  ]),
                ),
              ),
            ],
            const SizedBox(height: 12),
"""

if old not in text:
    # More tolerant fallback: locate the Display Names dropdown block and replace it.
    marker = "const InputDecoration(labelText: 'Display Names')"
    marker_index = text.find(marker)
    if marker_index < 0:
        print('No changes applied. Display Names dropdown block was not found or may already be fixed.')
    else:
        start = text.rfind("            if (widget.pageSizeOptions.length > 1) ...[", 0, marker_index)
        end = text.find("            const SizedBox(height:", marker_index)
        if start < 0 or end < 0:
            raise SystemExit('Could not safely locate full Display Names block.')
        end_line = text.find('\n', end)
        old_block = text[start:end_line + 1]
        text = text[:start] + new + text[end_line + 1:]
else:
    text = text.replace(old, new, 1)

path.write_text(text, encoding='utf-8')
if text == original:
    print('No changes applied. Display Names dropdown may already be fixed.')
else:
    print('Fixed Display Names UI: compact pill selector aligned to the right, no floating form field.')
