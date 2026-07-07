from pathlib import Path

path = Path('lib/main.dart')
if not path.exists():
    raise SystemExit('Run this script from the Flutter project root. lib/main.dart was not found.')

text = path.read_text(encoding='utf-8-sig')
original = text

# Fix AddEmployeeFullResult constructor calls that were created before the
# educationBackgrounds parameter existed.
text = text.replace(
    """                    certificates: certificates,
                  ));""",
    """                    certificates: certificates,
                    educationBackgrounds: educationRecords,
                  ));""",
)
text = text.replace(
    """          certificates: certificates,
        ));""",
    """          certificates: certificates,
          educationBackgrounds: educationRecords,
        ));""",
)
text = text.replace(
    """          certificates: certificates,
        ));""",
    """          certificates: certificates,
          educationBackgrounds: educationRecords,
        ));""",
)

# Some formatted versions place the constructor in a slightly different shape.
text = text.replace(
    """          certificates: certificates,
        ),""",
    """          certificates: certificates,
          educationBackgrounds: educationRecords,
        ),""",
)
text = text.replace(
    """                    certificates: certificates,
                  ),""",
    """                    certificates: certificates,
                    educationBackgrounds: educationRecords,
                  ),""",
)

# Ensure educationRecords exists before every AddEmployeeFullResult creation.
needle = """final educationRecords = educationBackgrounds
                  .where((entry) => entry.hasInput)
                  .map((entry) => entry.toMap())
                  .where((record) => record.isNotEmpty)
                  .toList();"""
alt_needle = """final educationRecords = educationBackgrounds
        .where((entry) => entry.hasInput)
        .map((entry) => entry.toMap())
        .where((record) => record.isNotEmpty)
        .toList();"""

positions = []
start = 0
while True:
    idx = text.find('AddEmployeeFullResult(', start)
    if idx < 0:
        break
    positions.append(idx)
    start = idx + 1

insertions = []
for idx in positions:
    window_start = max(0, idx - 2500)
    before = text[window_start:idx]
    if 'educationRecords' not in before:
        # Insert immediately before the Navigator.pop that wraps the constructor.
        nav = text.rfind('Navigator.pop', window_start, idx)
        insert_at = nav if nav >= 0 else idx
        indent = text[text.rfind('\n', 0, insert_at) + 1:insert_at]
        snippet = (
            f"{indent}final educationRecords = educationBackgrounds\n"
            f"{indent}    .where((entry) => entry.hasInput)\n"
            f"{indent}    .map((entry) => entry.toMap())\n"
            f"{indent}    .where((record) => record.isNotEmpty)\n"
            f"{indent}    .toList();\n"
        )
        insertions.append((insert_at, snippet))

for insert_at, snippet in reversed(insertions):
    text = text[:insert_at] + snippet + text[insert_at:]

path.write_text(text, encoding='utf-8')
if text == original:
    print('No changes applied. AddEmployeeFullResult constructor may already be fixed.')
else:
    print('Fixed AddEmployeeFullResult constructor calls for educationBackgrounds.')
