from pathlib import Path

path = Path('lib/main.dart')
text = path.read_text(encoding='utf-8')

old = "subtitle: 'Print detailed reports and summary totals per HR module.'\n      child: Column(children: ["
new = "subtitle: 'Print detailed reports and summary totals per HR module.',\n      child: Column(children: ["

if old in text:
    text = text.replace(old, new, 1)
    path.write_text(text, encoding='utf-8')
    print('Summary reports missing comma fixed in lib/main.dart')
elif "subtitle: 'Print detailed reports and summary totals per HR module.'," in text:
    print('Summary reports missing comma is already fixed.')
else:
    raise SystemExit('Expected Reports subtitle pattern was not found.')
