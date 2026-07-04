from pathlib import Path

path = Path('lib/main.dart')
if not path.exists():
    raise SystemExit('Run this script from the Flutter project root. lib/main.dart was not found.')

text = path.read_text(encoding='utf-8-sig')
original = text

# Remove visible formula note widgets from Add/Edit/View evaluation modals.
patterns = [
    """                const SizedBox(height: 16),
                evaluationFormulaNote(),""",
    """            const SizedBox(height: 14),
            evaluationFormulaNote(),""",
    """                const SizedBox(height: 16),
                evaluationFormulaNote(),""".replace('                ', '              '),
]

for pattern in patterns:
    text = text.replace(pattern, '')

# Remove the helper function itself if it is now unused.
while 'Widget evaluationFormulaNote() =>' in text:
    start = text.find('Widget evaluationFormulaNote() =>')
    # The helper ends just before evaluationRatingBox in the generated Evaluation block.
    end = text.find('Widget evaluationRatingBox(', start)
    if end < 0:
        break
    text = text[:start] + text[end:]

path.write_text(text, encoding='utf-8')
if text == original:
    print('No changes applied. Formula note may already be removed.')
else:
    print('Removed Evaluation formula note from modals/views.')
