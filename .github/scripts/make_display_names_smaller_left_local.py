from pathlib import Path

path = Path('lib/main.dart')
if not path.exists():
    raise SystemExit('Run this script from the Flutter project root. lib/main.dart was not found.')

text = path.read_text(encoding='utf-8-sig')
original = text

# Make the Display Names selector smaller while keeping it under the toolbar
# on the left, using the same outlined-field design and avoiding label clipping.
block_start_marker = "            if (widget.pageSizeOptions.length > 1) ...["
search_from = 0
block_start = -1
while True:
    candidate = text.find(block_start_marker, search_from)
    if candidate < 0:
        break
    candidate_end = text.find("            Expanded(", candidate)
    snippet = text[candidate:candidate_end if candidate_end > 0 else candidate + 2500]
    if 'pageSizeOptions' in snippet or 'Display Names' in snippet:
        block_start = candidate
        break
    search_from = candidate + 1

if block_start < 0:
    raise SystemExit('Could not find the Display Names selector block.')

block_end = text.find("            Expanded(", block_start)
if block_end < 0:
    raise SystemExit('Could not find table Expanded after Display Names selector.')

new_block = """            if (widget.pageSizeOptions.length > 1) ...[
              const SizedBox(height: 2),
              Align(
                alignment: Alignment.centerLeft,
                child: SizedBox(
                  width: 198,
                  height: 42,
                  child: Stack(
                    clipBehavior: Clip.none,
                    children: [
                      Positioned.fill(
                        child: Container(
                          padding: const EdgeInsets.fromLTRB(14, 7, 8, 4),
                          decoration: BoxDecoration(
                            color: _surface,
                            borderRadius: BorderRadius.circular(18),
                            border: Border.all(color: _primary, width: 1.4),
                          ),
                          child: DropdownButtonHideUnderline(
                            child: DropdownButton<int>(
                              value: pageSize,
                              isExpanded: true,
                              isDense: true,
                              borderRadius: BorderRadius.circular(16),
                              icon: const Icon(Icons.keyboard_arrow_down_rounded,
                                  size: 20),
                              style: const TextStyle(
                                color: _ink,
                                fontSize: 13,
                                fontWeight: FontWeight.w600,
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
                                WidgetsBinding.instance.addPostFrameCallback(
                                    (_) => scrollBothToTop());
                              }),
                            ),
                          ),
                        ),
                      ),
                      Positioned(
                        left: 13,
                        top: -8,
                        child: Container(
                          padding: const EdgeInsets.symmetric(horizontal: 4),
                          color: _bg,
                          child: const Text(
                            'Display Names',
                            style: TextStyle(
                              color: _primary,
                              fontSize: 11.5,
                              fontWeight: FontWeight.w800,
                              height: 1,
                            ),
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ],
            const SizedBox(height: 10),
"""

text = text[:block_start] + new_block + text[block_end:]
path.write_text(text, encoding='utf-8')

if text == original:
    print('No changes applied. Display Names selector may already be compact.')
else:
    print('Made Display Names selector smaller while keeping the same left-side design and position.')
