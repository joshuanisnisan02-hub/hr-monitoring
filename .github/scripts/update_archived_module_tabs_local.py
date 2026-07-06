from pathlib import Path

path = Path('lib/main.dart')
if not path.exists():
    raise SystemExit('Run this script from the Flutter project root. lib/main.dart was not found.')

text = path.read_text(encoding='utf-8-sig')
original = text

# Update the archive loader so each tab can show only the archived records for a module.
loader_start = text.find('Future<List<dynamic>> loadArchivedRecords(')
loader_end = text.find('Map<String, dynamic> archiveRestoreData(', loader_start)
if loader_start >= 0 and loader_end > loader_start:
    new_loader = r'''Future<List<dynamic>> loadArchivedRecords({
  required bool oldContracts,
  List<String> moduleFilters = const <String>[],
}) async {
  final rows = await db
      .from('archived_records')
      .select()
      .eq('archive_type', oldContracts ? 'old_contract' : 'deleted')
      .order('archived_at', ascending: false)
      .limit(5000);

  return rows.map((item) {
    final row = Map<String, dynamic>.from(item as Map);
    row['archived_at_display'] = row['archived_at'];
    row['restore_status'] = row['is_restored'] == true ? 'Restored' : 'Archived';
    return row;
  }).where((row) {
    if (oldContracts || moduleFilters.isEmpty) return true;
    final moduleName = formatValue(row['module_name']).trim().toLowerCase();
    return moduleFilters.any((filter) => moduleName == filter.toLowerCase());
  }).toList();
}

'''
    text = text[:loader_start] + new_loader + text[loader_end:]
else:
    print('Warning: loadArchivedRecords was not found. Make sure the archive feature patch was applied first.')

# Replace Archived page with module-separated tabs.
page_start = text.find('class ArchivedPage extends StatelessWidget {')
page_end = text.find('class ReportsPage extends StatefulWidget {', page_start)
if page_start < 0 or page_end < 0:
    raise SystemExit('Could not find ArchivedPage block. Apply the archive feature patch first.')

new_page = r'''class ArchivedPage extends StatelessWidget {
  const ArchivedPage({super.key});

  @override
  Widget build(BuildContext context) => PageFrame(
        title: 'Archived',
        subtitle:
            'Preserved deleted records and old contract snapshots separated by module for easier review and retrieval.',
        child: const DefaultTabController(
          length: 8,
          child: Column(children: [
            Align(
              alignment: Alignment.centerLeft,
              child: SizedBox(
                width: 980,
                child: TabBar(
                  isScrollable: true,
                  tabs: [
                    Tab(text: 'All Deleted'),
                    Tab(text: 'Employees'),
                    Tab(text: 'Contracts'),
                    Tab(text: 'Credentials'),
                    Tab(text: 'Evaluations'),
                    Tab(text: 'Appointment'),
                    Tab(text: 'Ranking'),
                    Tab(text: 'Old Contracts'),
                  ],
                ),
              ),
            ),
            SizedBox(height: 16),
            Expanded(
              child: TabBarView(children: [
                ArchivedRecordsTab(
                  title: 'All Deleted Rows',
                  oldContracts: false,
                ),
                ArchivedRecordsTab(
                  title: 'Archived Employees',
                  oldContracts: false,
                  moduleFilters: ['Employees'],
                ),
                ArchivedRecordsTab(
                  title: 'Archived Contracts',
                  oldContracts: false,
                  moduleFilters: ['Contracts'],
                ),
                ArchivedRecordsTab(
                  title: 'Archived Credentials',
                  oldContracts: false,
                  moduleFilters: [
                    'Credentials - Licenses',
                    'Credentials - Certificates',
                    'Credentials - Safety Officer',
                  ],
                ),
                ArchivedRecordsTab(
                  title: 'Archived Evaluations',
                  oldContracts: false,
                  moduleFilters: ['Evaluations'],
                ),
                ArchivedRecordsTab(
                  title: 'Archived Appointments',
                  oldContracts: false,
                  moduleFilters: ['Appointment'],
                ),
                ArchivedRecordsTab(
                  title: 'Archived Ranking',
                  oldContracts: false,
                  moduleFilters: ['Ranking'],
                ),
                ArchivedRecordsTab(
                  title: 'Old Contracts',
                  oldContracts: true,
                ),
              ]),
            ),
          ]),
        ),
      );
}

class ArchivedRecordsTab extends StatelessWidget {
  final String title;
  final bool oldContracts;
  final List<String> moduleFilters;

  const ArchivedRecordsTab({
    super.key,
    required this.title,
    required this.oldContracts,
    this.moduleFilters = const <String>[],
  });

  @override
  Widget build(BuildContext context) => CrudTable(
        key: ValueKey('archive-$title-${oldContracts ? 'old' : 'deleted'}'),
        load: () => loadArchivedRecords(
          oldContracts: oldContracts,
          moduleFilters: moduleFilters,
        ),
        searchHint: oldContracts
            ? 'Search old contract, employee, type, date, or status'
            : 'Search $title by employee, module, table, or date',
        addLabel: oldContracts ? 'Old Contract' : 'Archived Row',
        allowAdd: false,
        reportTitle: oldContracts ? 'Archived Old Contracts Report' : '$title Report',
        columns: const [
          GridCol('module_name', 'Module', flex: 2),
          GridCol('employee_name', 'Employee Name', flex: 3, primary: true),
          GridCol('table_name', 'Table', flex: 2),
          GridCol('archived_at_display', 'Archived At', flex: 2),
          GridCol('restore_status', 'Status', isStatus: true),
        ],
        onView: viewArchivedRecord,
        extraAction: oldContracts ? null : restoreArchivedRecordAction,
        showDelete: false,
        onDelete: (row) async {},
      );
}

'''
text = text[:page_start] + new_page + text[page_end:]

path.write_text(text, encoding='utf-8')
if text == original:
    print('No changes applied. Archived module tabs may already be updated.')
else:
    print('Updated Archived module with module-separated tabs and per-tab archive filtering.')
