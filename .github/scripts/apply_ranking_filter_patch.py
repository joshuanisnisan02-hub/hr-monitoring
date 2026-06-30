from pathlib import Path

path = Path("lib/main.dart")
text = path.read_text(encoding="utf-8")


def replace_once(old: str, new: str) -> None:
    global text
    if old not in text:
        raise SystemExit(f"Required pattern not found:\n{old[:400]}")
    text = text.replace(old, new, 1)


replace_once(
"""class _RankingPageState extends State<RankingPage> {
  String filter = 'All';

  bool _matchesRankingFilter(Map<String, dynamic> row, String selected) {
""",
"""class _RankingPageState extends State<RankingPage> {
  String filter = 'All';
  String rankFilter = 'All';
  late Future<List<EditOption>> rankFilterOptionsFuture;

  @override
  void initState() {
    super.initState();
    rankFilterOptionsFuture = rankOptions();
  }

  bool _matchesRankingFilter(Map<String, dynamic> row, String selected) {
""",
)

replace_once(
"""  bool _matchesRankingFilter(Map<String, dynamic> row, String selected) {
    final text = '${row['appointment'] ?? ''}'.toLowerCase().replaceAll('_', ' ').replaceAll('-', ' ');
    final isFullTime = text.contains('full') && text.contains('time');
    final isProbationary = text.contains('probationary');
    if (selected == 'Full-time') return isFullTime;
    if (selected == 'Probationary') return isProbationary;
    return isFullTime || isProbationary;
  }
""",
"""  bool _matchesRankingFilter(Map<String, dynamic> row, String selected) {
    final text = '${row['appointment'] ?? ''}'.toLowerCase().replaceAll('_', ' ').replaceAll('-', ' ');
    final isFullTime = text.contains('full') && text.contains('time');
    final isProbationary = text.contains('probationary');
    if (selected == 'Full-time') return isFullTime;
    if (selected == 'Probationary') return isProbationary;
    return isFullTime || isProbationary;
  }

  Iterable<String> _rankValues(Map<String, dynamic> row) sync* {
    for (final key in const ['previous_rank_text', 'applied_rank_text', 'approved_rank_text']) {
      final value = '${row[key] ?? ''}'.trim();
      if (value.isNotEmpty && value != '-') yield value;
    }
  }

  bool _matchesRankFilter(Map<String, dynamic> row) {
    if (rankFilter == 'All') return true;
    final selected = normalizeRankKey(rankFilter);
    return _rankValues(row).any((value) => normalizeRankKey(value) == selected);
  }

  String _rankingReportTitle() {
    final appointmentLabel = filter == 'All' ? 'Full-time and Probationary' : filter;
    final rankLabel = rankFilter == 'All' ? 'All Ranks' : rankFilter;
    return 'Ranking Report - $appointmentLabel - $rankLabel';
  }
""",
)

replace_once(
"""  Future<List<dynamic>> _loadRankings() async {
    final rows = await loadRankings(limit: 5000);
    return rows.where((item) => _matchesRankingFilter(normalizeRow(Map<String, dynamic>.from(item as Map)), filter)).toList();
  }
""",
"""  Future<List<dynamic>> _loadRankings() async {
    final rows = await loadRankings(limit: 5000);
    return rows
        .map((item) => normalizeRow(Map<String, dynamic>.from(item as Map)))
        .where((row) => _matchesRankingFilter(row, filter) && _matchesRankFilter(row))
        .toList();
  }
""",
)

replace_once(
"""          Card(
            child: Padding(
              padding: const EdgeInsets.all(12),
              child: Row(children: [
                const Text('Filter:', style: TextStyle(fontWeight: FontWeight.w900, color: _ink)),
                const SizedBox(width: 12),
                for (final item in const ['All', 'Full-time', 'Probationary']) ...[
                  ChoiceChip(
                    label: Text(item == 'All' ? 'All (Full-time + Probationary)' : item),
                    selected: filter == item,
                    onSelected: (_) => setState(() => filter = item),
                  ),
                  const SizedBox(width: 8),
                ],
              ]),
            ),
          ),
""",
"""          Card(
            child: Padding(
              padding: const EdgeInsets.all(12),
              child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                Row(children: [
                  const Text('Filter:', style: TextStyle(fontWeight: FontWeight.w900, color: _ink)),
                  const SizedBox(width: 12),
                  for (final item in const ['All', 'Full-time', 'Probationary']) ...[
                    ChoiceChip(
                      label: Text(item == 'All' ? 'All (Full-time + Probationary)' : item),
                      selected: filter == item,
                      onSelected: (_) => setState(() {
                        filter = item;
                        rankFilter = 'All';
                      }),
                    ),
                    const SizedBox(width: 8),
                  ],
                ]),
                const SizedBox(height: 12),
                FutureBuilder<List<EditOption>>(
                  future: rankFilterOptionsFuture,
                  builder: (context, snap) {
                    final ranks = snap.data ?? const <EditOption>[];
                    final options = <EditOption>[
                      const EditOption('All', 'All Ranks'),
                      ...uniqueOptions(ranks).map((option) => EditOption(option.value, option.value)),
                    ];
                    final selectedRank = options.any((option) => option.value == rankFilter) ? rankFilter : 'All';
                    return SizedBox(
                      width: 360,
                      child: DropdownButtonFormField<String>(
                        value: selectedRank,
                        isExpanded: true,
                        decoration: const InputDecoration(labelText: 'Filter by Ranking'),
                        items: options.map((option) => DropdownMenuItem<String>(value: option.value, child: Text(option.label, overflow: TextOverflow.ellipsis))).toList(),
                        onChanged: (value) => setState(() => rankFilter = value ?? 'All'),
                      ),
                    );
                  },
                ),
              ]),
            ),
          ),
""",
)

replace_once("""key: ValueKey(filter),""", """key: ValueKey('$filter|$rankFilter'),""")
replace_once(
"""reportTitle: 'Ranking Report - ${filter == 'All' ? 'Full-time and Probationary' : filter}',""",
"""reportTitle: _rankingReportTitle(),""",
)

replace_once(
"""                if (isAdd)
                  rankTextBox('Previous Rank', previousRank, () => pickRank(previousRank, previousSalary))
                else
                  textBox('Previous Rank', previousRank, readOnly: true),
""",
"""                if (isAdd)
                  rankAutocompleteBox('Previous Rank', previousRank, previousSalary, ranks)
                else
                  textBox('Previous Rank', previousRank, readOnly: true),
""",
)

replace_once(
"""                  rankTextBox('Applied Rank', appliedRank, () => pickRank(appliedRank, appliedSalary)),
""",
"""                  rankAutocompleteBox('Applied Rank', appliedRank, appliedSalary, ranks),
""",
)

replace_once(
"""Widget rankTextBox(String label, TextEditingController controller, VoidCallback onPick) => SizedBox(
      width: 354,
      child: Row(children: [
        Expanded(child: TextFormField(controller: controller, decoration: InputDecoration(labelText: label))),
        const SizedBox(width: 8),
        OutlinedButton(onPressed: onPick, child: const Text('Pick')),
      ]),
    );
""",
"""Widget rankTextBox(String label, TextEditingController controller, VoidCallback onPick) => SizedBox(
      width: 354,
      child: Row(children: [
        Expanded(child: TextFormField(controller: controller, decoration: InputDecoration(labelText: label))),
        const SizedBox(width: 8),
        OutlinedButton(onPressed: onPick, child: const Text('Pick')),
      ]),
    );

Widget rankAutocompleteBox(String label, TextEditingController controller, TextEditingController salaryController, List<EditOption> ranks) => SizedBox(
      width: 354,
      child: Autocomplete<EditOption>(
        initialValue: TextEditingValue(text: controller.text),
        displayStringForOption: (option) => option.value,
        optionsBuilder: (textEditingValue) {
          final options = uniqueOptions(ranks).toList()..sort((a, b) => a.value.toLowerCase().compareTo(b.value.toLowerCase()));
          final query = textEditingValue.text.trim().toLowerCase();
          if (query.isEmpty) return options;
          final normalizedQuery = normalizeRankKey(query);
          return options.where((option) {
            final value = option.value.toLowerCase();
            final labelText = option.label.toLowerCase();
            final normalizedValue = normalizeRankKey(option.value);
            return value.contains(query) || labelText.contains(query) || normalizedValue.contains(normalizedQuery);
          });
        },
        onSelected: (option) {
          controller.text = option.value;
          if (option.salary != null) salaryController.text = formatMoney(option.salary);
        },
        fieldViewBuilder: (context, textController, focusNode, onFieldSubmitted) => TextFormField(
          controller: textController,
          focusNode: focusNode,
          decoration: InputDecoration(labelText: label, hintText: 'Select or type rank', suffixIcon: const Icon(Icons.search_rounded)),
          onChanged: (value) {
            controller.text = value;
            final selectedKey = normalizeRankKey(value);
            final exact = uniqueOptions(ranks).where((option) => normalizeRankKey(option.value) == selectedKey).toList();
            if (exact.isNotEmpty && exact.first.salary != null) salaryController.text = formatMoney(exact.first.salary);
          },
        ),
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
                    title: Text(option.value, overflow: TextOverflow.ellipsis),
                    subtitle: option.salary == null ? null : Text(formatMoney(option.salary)),
                    onTap: () => onSelected(option),
                  );
                },
              ),
            ),
          ),
        ),
      ),
    );
""",
)

path.write_text(text, encoding="utf-8")
print("Ranking filter patch applied to lib/main.dart")
