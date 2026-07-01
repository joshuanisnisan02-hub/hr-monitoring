from pathlib import Path

path = Path('lib/main.dart')
text = path.read_text(encoding='utf-8')

old = """                FutureBuilder<List<EditOption>>(\n                  future: rankFilterOptionsFuture,\n                  builder: (context, snap) {\n                    final ranks = snap.data ?? const <EditOption>[];\n                    final options = <EditOption>[\n                      const EditOption('All', 'All Ranks'),\n                      ...uniqueOptions(ranks).map((option) => EditOption(option.value, option.value)),\n                    ];\n                    final selectedRank = options.any((option) => option.value == rankFilter) ? rankFilter : 'All';\n                    return SizedBox(\n                      width: 360,\n                      child: DropdownButtonFormField<String>(\n                        value: selectedRank,\n                        isExpanded: true,\n                        decoration: const InputDecoration(labelText: 'Filter by Ranking'),\n                        items: options.map((option) => DropdownMenuItem<String>(value: option.value, child: Text(option.label, overflow: TextOverflow.ellipsis))).toList(),\n                        onChanged: (value) => setState(() => rankFilter = value ?? 'All'),\n                      ),\n                    );\n                  },\n                ),\n"""

new = """                FutureBuilder<List<EditOption>>(\n                  future: rankFilterOptionsFuture,\n                  builder: (context, snap) {\n                    final ranks = snap.data ?? const <EditOption>[];\n                    final options = <EditOption>[\n                      const EditOption('All', 'All Ranks'),\n                      ...uniqueOptions(ranks).map((option) => EditOption(option.value, option.value)),\n                    ];\n                    final selectedRank = options.any((option) => option.value == rankFilter) ? rankFilter : 'All';\n                    return rankFilterAutocompleteBox(\n                      selectedRank: selectedRank,\n                      options: options,\n                      onChanged: (value) => setState(() => rankFilter = value),\n                    );\n                  },\n                ),\n"""

if old not in text:
    if 'rankFilterAutocompleteBox(' in text:
        print('Rank filter autocomplete patch is already applied.')
        raise SystemExit(0)
    raise SystemExit('Required rank filter dropdown block was not found.')

text = text.replace(old, new, 1)

insert_before = """class GridCol {\n"""
widget = """
class RankFilterAutocompleteBox extends StatefulWidget {
  final String selectedRank;
  final List<EditOption> options;
  final ValueChanged<String> onChanged;

  const RankFilterAutocompleteBox({super.key, required this.selectedRank, required this.options, required this.onChanged});

  @override
  State<RankFilterAutocompleteBox> createState() => _RankFilterAutocompleteBoxState();
}

class _RankFilterAutocompleteBoxState extends State<RankFilterAutocompleteBox> {
  late TextEditingController controller;

  @override
  void initState() {
    super.initState();
    controller = TextEditingController(text: widget.selectedRank == 'All' ? 'All Ranks' : widget.selectedRank);
  }

  @override
  void didUpdateWidget(covariant RankFilterAutocompleteBox oldWidget) {
    super.didUpdateWidget(oldWidget);
    final nextText = widget.selectedRank == 'All' ? 'All Ranks' : widget.selectedRank;
    if (oldWidget.selectedRank != widget.selectedRank && controller.text != nextText) {
      controller.text = nextText;
    }
  }

  @override
  void dispose() {
    controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) => SizedBox(
        width: 360,
        child: Autocomplete<EditOption>(
          initialValue: TextEditingValue(text: controller.text),
          displayStringForOption: (option) => option.label,
          optionsBuilder: (textEditingValue) {
            final sorted = uniqueOptions(widget.options).toList()..sort((a, b) => a.label.toLowerCase().compareTo(b.label.toLowerCase()));
            final query = textEditingValue.text.trim().toLowerCase();
            if (query.isEmpty) return sorted;
            final normalizedQuery = normalizeRankKey(query);
            return sorted.where((option) {
              final value = option.value.toLowerCase();
              final label = option.label.toLowerCase();
              final normalizedValue = normalizeRankKey(option.value);
              final normalizedLabel = normalizeRankKey(option.label);
              return value.contains(query) || label.contains(query) || normalizedValue.contains(normalizedQuery) || normalizedLabel.contains(normalizedQuery);
            });
          },
          onSelected: (option) {
            controller.text = option.label;
            widget.onChanged(option.value);
          },
          fieldViewBuilder: (context, textController, focusNode, onFieldSubmitted) {
            if (textController.text != controller.text) textController.text = controller.text;
            return TextFormField(
              controller: textController,
              focusNode: focusNode,
              decoration: InputDecoration(
                labelText: 'Filter by Ranking',
                hintText: 'Search or select rank',
                suffixIcon: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    if (widget.selectedRank != 'All')
                      IconButton(
                        tooltip: 'Clear rank filter',
                        icon: const Icon(Icons.close_rounded),
                        onPressed: () {
                          textController.text = 'All Ranks';
                          controller.text = 'All Ranks';
                          widget.onChanged('All');
                        },
                      ),
                    const Icon(Icons.search_rounded),
                    const SizedBox(width: 10),
                  ],
                ),
              ),
              onTap: () {
                if (widget.selectedRank == 'All') textController.selection = TextSelection(baseOffset: 0, extentOffset: textController.text.length);
              },
              onChanged: (value) {
                controller.text = value;
                final clean = value.trim();
                if (clean.isEmpty) {
                  widget.onChanged('All');
                  return;
                }
                final exact = uniqueOptions(widget.options).where((option) => option.label.toLowerCase() == clean.toLowerCase() || option.value.toLowerCase() == clean.toLowerCase() || normalizeRankKey(option.value) == normalizeRankKey(clean)).toList();
                if (exact.isNotEmpty) widget.onChanged(exact.first.value);
              },
            );
          },
          optionsViewBuilder: (context, onSelected, options) => Align(
            alignment: Alignment.topLeft,
            child: Material(
              elevation: 6,
              borderRadius: BorderRadius.circular(14),
              child: ConstrainedBox(
                constraints: const BoxConstraints(maxWidth: 520, maxHeight: 320),
                child: ListView.separated(
                  padding: EdgeInsets.zero,
                  shrinkWrap: true,
                  itemCount: options.length,
                  separatorBuilder: (_, __) => const Divider(height: 1),
                  itemBuilder: (context, index) {
                    final option = options.elementAt(index);
                    return ListTile(
                      dense: true,
                      title: Text(option.label, overflow: TextOverflow.ellipsis),
                      onTap: () => onSelected(option),
                    );
                  },
                ),
              ),
            ),
          ),
        ),
      );
}

Widget rankFilterAutocompleteBox({required String selectedRank, required List<EditOption> options, required ValueChanged<String> onChanged}) => RankFilterAutocompleteBox(selectedRank: selectedRank, options: options, onChanged: onChanged);

"""

if 'class RankFilterAutocompleteBox extends StatefulWidget' not in text:
    if insert_before not in text:
        raise SystemExit('GridCol insertion point was not found.')
    text = text.replace(insert_before, widget + insert_before, 1)

path.write_text(text, encoding='utf-8')
print('Rank filter autocomplete patch applied to lib/main.dart')
