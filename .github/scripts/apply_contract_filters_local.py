from pathlib import Path

path = Path('lib/main.dart')
if not path.exists():
    raise SystemExit('Run this script from the Flutter project root. lib/main.dart was not found.')

text = path.read_text(encoding='utf-8')
start = text.find('class ContractsPage extends')
end = text.find('class CredentialsPage extends', start)
if start < 0 or end < 0:
    raise SystemExit('Could not find ContractsPage block to replace.')

replacement = r'''
class ContractsPage extends StatefulWidget {
  const ContractsPage({super.key});

  @override
  State<ContractsPage> createState() => _ContractsPageState();
}

class _ContractsPageState extends State<ContractsPage> {
  String contractTypeFilter = 'All';
  String statusFilter = 'All';

  static const contractTypeFilters = <String>[
    'All',
    'Full-time',
    'Full-time-Probationary',
    'Part-time',
    'Probationary',
    'Compliance',
  ];

  static const statusFilters = <String>[
    'All',
    'On-going',
    'For Renewal',
    'Expired',
    'Resigned',
    'Unspecified',
  ];

  String _clean(Object? value) => formatValue(value).trim();

  String _statusKey(Object? value) {
    final raw = _clean(value);
    final lower = raw.toLowerCase();
    if (lower.isEmpty || raw == '-') return 'Unspecified';
    if (lower.contains('resign')) return 'Resigned';
    if (lower.contains('renew')) return 'For Renewal';
    if (lower.contains('expired')) return 'Expired';
    if (lower.contains('ongoing') || lower.contains('on-going')) return 'On-going';
    if (lower.contains('active')) return 'On-going';
    return raw;
  }

  bool _matchesType(Map<String, dynamic> row) {
    if (contractTypeFilter == 'All') return true;
    return _clean(row['contract_type']).toLowerCase() ==
        contractTypeFilter.toLowerCase();
  }

  bool _matchesStatus(Map<String, dynamic> row) {
    if (statusFilter == 'All') return true;
    return _statusKey(row['status']).toLowerCase() == statusFilter.toLowerCase();
  }

  Future<List<dynamic>> _loadContracts() async {
    final rows = statusFilter == 'Resigned'
        ? await loadContracts(limit: 5000)
        : await activeOnlyRows(loadContracts(limit: 5000));
    final filtered = <Map<String, dynamic>>[];
    for (final item in rows) {
      final row = normalizeRow(Map<String, dynamic>.from(item as Map));
      if (!_matchesType(row)) continue;
      if (!_matchesStatus(row)) continue;
      filtered.add(row);
    }
    return filtered;
  }

  String _reportTitle() {
    final parts = <String>['Contract Report'];
    if (contractTypeFilter != 'All') parts.add(contractTypeFilter);
    if (statusFilter != 'All') parts.add(statusFilter);
    return parts.join(' - ');
  }

  @override
  Widget build(BuildContext context) => PageFrame(
        title: 'Contracts',
        subtitle: 'Manage contract records with dynamic total days left.',
        child: Column(children: [
          Card(
            child: Padding(
              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
              child: Row(children: [
                const Text('Filter:',
                    style: TextStyle(fontWeight: FontWeight.w900, color: _ink)),
                const SizedBox(width: 10),
                SizedBox(
                  width: 280,
                  child: DropdownButtonFormField<String>(
                    value: contractTypeFilter,
                    isExpanded: true,
                    decoration: const InputDecoration(labelText: 'Contract Type'),
                    items: const [
                      DropdownMenuItem(value: 'All', child: Text('All Contract Types')),
                      DropdownMenuItem(value: 'Full-time', child: Text('Full-time')),
                      DropdownMenuItem(value: 'Full-time-Probationary', child: Text('Full-time-Probationary')),
                      DropdownMenuItem(value: 'Part-time', child: Text('Part-time')),
                      DropdownMenuItem(value: 'Probationary', child: Text('Probationary')),
                      DropdownMenuItem(value: 'Compliance', child: Text('Compliance')),
                    ],
                    onChanged: (value) =>
                        setState(() => contractTypeFilter = value ?? 'All'),
                  ),
                ),
                const SizedBox(width: 10),
                SizedBox(
                  width: 230,
                  child: DropdownButtonFormField<String>(
                    value: statusFilter,
                    isExpanded: true,
                    decoration: const InputDecoration(labelText: 'Status'),
                    items: const [
                      DropdownMenuItem(value: 'All', child: Text('All Statuses')),
                      DropdownMenuItem(value: 'On-going', child: Text('On-going')),
                      DropdownMenuItem(value: 'For Renewal', child: Text('For Renewal')),
                      DropdownMenuItem(value: 'Expired', child: Text('Expired')),
                      DropdownMenuItem(value: 'Resigned', child: Text('Resigned')),
                      DropdownMenuItem(value: 'Unspecified', child: Text('Unspecified')),
                    ],
                    onChanged: (value) => setState(() => statusFilter = value ?? 'All'),
                  ),
                ),
                const SizedBox(width: 12),
                const Expanded(
                  child: Text(
                    'The table and Print button will follow the selected contract type and status filters.',
                    style: TextStyle(color: _muted, fontWeight: FontWeight.w600),
                  ),
                ),
              ]),
            ),
          ),
          const SizedBox(height: 8),
          Expanded(
            child: CrudTable(
              key: ValueKey('contracts-$contractTypeFilter-$statusFilter'),
              load: () => _loadContracts(),
              searchHint: 'Search employee, contract type, date, or status',
              addLabel: 'Add Contract',
              reportTitle: _reportTitle(),
              columns: const [
                GridCol('employee_name', 'Employee Name', flex: 3, primary: true),
                GridCol('contract_type', 'Contract Type', flex: 2),
                GridCol('status', 'Status', isStatus: true),
                GridCol('contract_start_date', 'Start'),
                GridCol('duration_months', 'Months', isNumber: true),
                GridCol('contract_end_date', 'End'),
                GridCol('days_left', 'Days Left', isNumber: true),
              ],
              onAdd: (ctx, refresh) => editContract(ctx, null, refresh),
              onEdit: editContract,
              onDelete: (row) =>
                  db.from('employee_contracts').delete().eq('id', row['id']),
            ),
          ),
        ]),
      );
}

'''

text = text[:start] + replacement + text[end:]
path.write_text(text, encoding='utf-8')
print('Applied Contract Type and Status filters to the Contracts module.')
