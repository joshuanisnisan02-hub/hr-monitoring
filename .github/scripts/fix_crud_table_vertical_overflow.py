from pathlib import Path

path = Path('lib/main.dart')
text = path.read_text(encoding='utf-8')

if 'minCrudTableScrollableHeight' not in text:
    marker = 'class CrudTable extends StatefulWidget {'
    if marker not in text:
        raise SystemExit('CrudTable class was not found.')
    text = text.replace(marker, "const double minCrudTableScrollableHeight = 520;\n\n" + marker, 1)

start = text.find('class _CrudTableState')
if start == -1:
    raise SystemExit('_CrudTableState was not found.')
block_start = text.find('          return Column(children: [', start)
if block_start == -1:
    if 'final tableContent = Column(children: [' in text:
        print('CRUD table overflow fix already applied.')
        path.write_text(text, encoding='utf-8')
        raise SystemExit(0)
    raise SystemExit('CrudTable return Column block was not found.')

block_end_marker = '''            PaginationFooter(
              page: safePage,
              pageCount: pageCount,
              start: sorted.isEmpty ? 0 : startIndex + 1,
              end: endIndex,
              total: sorted.length,
              onPrevious: safePage > 0 ? () => setState(() => page = safePage - 1) : null,
              onNext: safePage < pageCount - 1 ? () => setState(() => page = safePage + 1) : null,
            ),
          ]);'''
block_end = text.find(block_end_marker, block_start)
if block_end == -1:
    raise SystemExit('CrudTable footer block was not found.')
block_end += len(block_end_marker)
old_block = text[block_start:block_end]
new_block = old_block.replace('          return Column(children: [', '          final tableContent = Column(children: [', 1)
new_block += r'''
          return LayoutBuilder(
            builder: (context, constraints) {
              if (constraints.maxHeight < 320) {
                return SingleChildScrollView(
                  child: SizedBox(
                    height: minCrudTableScrollableHeight,
                    child: tableContent,
                  ),
                );
              }
              return tableContent;
            },
          );'''
text = text[:block_start] + new_block + text[block_end:]

path.write_text(text, encoding='utf-8')
print('CRUD table vertical overflow fix applied to lib/main.dart')
