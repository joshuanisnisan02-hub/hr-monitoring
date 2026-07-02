from pathlib import Path

path = Path('lib/main.dart')
text = path.read_text(encoding='utf-8')

# A previous broad replacement repaired Align: by changing every "Align:" to "Align(",
# which also damaged named parameters like textAlign: and mainAxisAlignment:.
# Restore the common named parameters back to colon syntax.
for name in [
    'textAlign',
    'alignment',
    'mainAxisAlignment',
    'crossAxisAlignment',
    'verticalDirection',
    'textDirection',
    'clipBehavior',
]:
    text = text.replace(f'{name}(', f'{name}:')

# Keep the intended repair for the broken widget token.
text = text.replace('Align:\n', 'Align(\n')
text = text.replace('              Align:\n', '              Align(\n')

# Clean possible accidental spacing variants from the logs.
text = text.replace('textAlign( TextAlign.', 'textAlign: TextAlign.')
text = text.replace('mainAxisAlignment( MainAxisAlignment.', 'mainAxisAlignment: MainAxisAlignment.')
text = text.replace('crossAxisAlignment( CrossAxisAlignment.', 'crossAxisAlignment: CrossAxisAlignment.')
text = text.replace('alignment( Alignment.', 'alignment: Alignment.')

path.write_text(text, encoding='utf-8')
print('Repaired named-parameter colon damage caused by Align repair.')
