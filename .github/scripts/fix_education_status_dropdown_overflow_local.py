from pathlib import Path
import re

path = Path('lib/main.dart')
if not path.exists():
    raise SystemExit('Run this script from the Flutter project root. lib/main.dart was not found.')

text = path.read_text(encoding='utf-8-sig')
original = text

# Limit changes to the education background card widget.
start = text.find('Widget educationBackgroundInputCard(')
end = text.find('class AddEmployeeFullResult', start)
if start < 0 or end < 0:
    raise SystemExit('Could not locate educationBackgroundInputCard block.')

block = text[start:end]

# Make the second-row fields fit cleanly inside the card.
# 342 + 140 + 190 + 20 spacing = 692, below the inner card width.
block = block.replace(
    """          SizedBox(
            width: 164,
            child: TextFormField(
              controller: entry.yearGraduated,""",
    """          SizedBox(
            width: 140,
            child: TextFormField(
              controller: entry.yearGraduated,""",
    1,
)
block = block.replace(
    """          SizedBox(
            width: 164,
            child: DropdownButtonFormField<String>(""",
    """          SizedBox(
            width: 190,
            child: DropdownButtonFormField<String>(""",
    1,
)

# DropdownButtonFormField can still overflow when text + arrow compete for space.
# isExpanded lets the selected value use the available width correctly.
status_idx = block.find('child: DropdownButtonFormField<String>(')
if status_idx >= 0:
    value_idx = block.find('value:', status_idx)
    if value_idx >= 0 and 'isExpanded: true,' not in block[status_idx:value_idx]:
        insert_at = value_idx
        block = block[:insert_at] + '              isExpanded: true,\n' + block[insert_at:]

# Reduce the selected item font a little so longer statuses such as
# Undergraduate stay inside the field.
items_old = """                  .map((status) => DropdownMenuItem<String>(
                        value: status,
                        child: Text(status),
                      ))"""
items_new = """                  .map((status) => DropdownMenuItem<String>(
                        value: status,
                        child: Text(status,
                            overflow: TextOverflow.ellipsis,
                            style: const TextStyle(fontSize: 13)),
                      ))"""
block = block.replace(items_old, items_new, 1)

text = text[:start] + block + text[end:]
path.write_text(text, encoding='utf-8')

if text == original:
    print('No changes applied. Education status dropdown overflow may already be fixed.')
else:
    print('Fixed education status dropdown overflow.')
