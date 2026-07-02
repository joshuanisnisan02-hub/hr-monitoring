from pathlib import Path
import re

MAIN_DART = Path('lib/main.dart')
if not MAIN_DART.exists():
    raise SystemExit('Run this from the Flutter project root. lib/main.dart was not found.')

text = MAIN_DART.read_text(encoding='utf-8')
original = text

# Make sure evaluation loading includes all rating and description columns used by the tabs.
load_eval_pattern = re.compile(
    r"Future<List<dynamic>> loadEvaluations\(\{int limit = 1500\}\) => db\.from\('evaluation_records'\)\.select\([^\n]+?\)\.order\('academic_year'[^\n]*?\.limit\(limit\);"
)
load_eval_replacement = "Future<List<dynamic>> loadEvaluations({int limit = 1500}) => db.from('evaluation_records').select('id, employee_id, academic_year, semester, superior_rating, superior_description, peer_rating, peer_description, self_rating, self_description, student_rating, student_description, total_rating, total_description, employees(full_name)').order('academic_year', ascending: false).order('semester', ascending: false).limit(limit);"
text, load_count = load_eval_pattern.subn(load_eval_replacement, text, count=1)
if load_count == 0:
    start = text.find("Future<List<dynamic>> loadEvaluations")
    end = text.find("Future<List<dynamic>> loadRankings", start)
    existing = text[start:end] if start != -1 and end != -1 else ''
    if 'superior_description' not in existing or 'student_description' not in existing:
        raise SystemExit('Could not update loadEvaluations select list.')

# Replace the current Evaluations page implementation with tabbed evaluation tables.
page_start = text.find('class EvaluationsPage extends')
page_end = text.find('class AppointmentPage extends', page_start)
if page_start == -1 or page_end == -1:
    raise SystemExit('Could not find EvaluationsPage block boundaries.')

evaluation_tabs_block = r'''class EvaluationsPage extends StatefulWidget {
  const EvaluationsPage({super.key});

  @override
  State<EvaluationsPage> createState() => _EvaluationsPageState();
}

class _EvaluationsPageState extends State<EvaluationsPage> {
  int refreshToken = 0;
  String search = '';
  String academicYearFilter = 'All';
  String semesterFilter = 'All';

  void refreshEvaluations() => setState(() => refreshToken++);

  List<Map<String, dynamic>> _normalizedRows(List<dynamic> rows) => rows.map((item) => normalizeRow(Map<String, dynamic>.from(item as Map))).toList();

  List<String> _filterOptions(List<Map<String, dynamic>> rows, String key) {
    final values = rows.map((r) => formatValueRaw(r[key]).trim()).where((v) => v.isNotEmpty && v != '-').toSet().toList()..sort((a, b) => b.compareTo(a));
    return ['All', ...values];
  }

  List<Map<String, dynamic>> _filteredRows(List<Map<String, dynamic>> rows) {
    final query = search.trim().toLowerCase();
    return rows.where((row) {
      final ayOk = academicYearFilter == 'All' || formatValueRaw(row['academic_year']) == academicYearFilter;
      final semOk = semesterFilter == 'All' || formatValueRaw(row['semester']) == semesterFilter;
      final searchOk = query.isEmpty || searchableText(row).contains(query);
      return ayOk && semOk && searchOk;
    }).toList();
  }

  @override
  Widget build(BuildContext context) => PageFrame(
        title: 'Evaluations',
        subtitle: 'Manage faculty evaluation records by evaluation type.',
        child: FutureBuilder<List<dynamic>>(
          key: ValueKey(refreshToken),
          future: loadEvaluations(limit: 5000),
          builder: (_, snap) {
            if (snap.connectionState != ConnectionState.done) return const Center(child: CircularProgressIndicator());
            if (snap.hasError) return ErrorBox('${snap.error}');
            final allRows = _normalizedRows(snap.data ?? const []);
            final academicYearOptions = _filterOptions(allRows, 'academic_year');
            final semesterOptions = _filterOptions(allRows, 'semester');
            if (!academicYearOptions.contains(academicYearFilter)) academicYearFilter = 'All';
            if (!semesterOptions.contains(semesterFilter)) semesterFilter = 'All';
            final rows = _filteredRows(allRows);
            final reportPeriod = [
              if (academicYearFilter != 'All') 'A.Y. $academicYearFilter' else 'All Academic Years',
              if (semesterFilter != 'All') semesterFilter else 'All Semesters',
            ].join(' - ');

            return DefaultTabController(
              length: 4,
              child: Column(children: [
                const Align(
                  alignment: Alignment.centerLeft,
                  child: SizedBox(
                    width: 760,
                    child: TabBar(
                      isScrollable: true,
                      tabs: [
                        Tab(text: 'Superior Evaluation'),
                        Tab(text: 'Peer-to-peer Evaluation'),
                        Tab(text: 'Self Evaluation'),
                        Tab(text: 'Student Evaluation'),
                      ],
                    ),
                  ),
                ),
                const SizedBox(height: 14),
                Card(
                  child: Padding(
                    padding: const EdgeInsets.all(12),
                    child: Row(children: [
                      SizedBox(
                        width: 280,
                        child: TextField(
                          decoration: const InputDecoration(labelText: 'Search', hintText: 'Search employee or rating', prefixIcon: Icon(Icons.search_rounded)),
                          onChanged: (value) => setState(() => search = value),
                        ),
                      ),
                      const SizedBox(width: 12),
                      SizedBox(
                        width: 210,
                        child: DropdownButtonFormField<String>(
                          value: academicYearFilter,
                          isExpanded: true,
                          decoration: const InputDecoration(labelText: 'Academic Year'),
                          items: academicYearOptions.map((v) => DropdownMenuItem(value: v, child: Text(v, overflow: TextOverflow.ellipsis))).toList(),
                          onChanged: (value) => setState(() => academicYearFilter = value ?? 'All'),
                        ),
                      ),
                      const SizedBox(width: 12),
                      SizedBox(
                        width: 210,
                        child: DropdownButtonFormField<String>(
                          value: semesterFilter,
                          isExpanded: true,
                          decoration: const InputDecoration(labelText: 'Semester'),
                          items: semesterOptions.map((v) => DropdownMenuItem(value: v, child: Text(v, overflow: TextOverflow.ellipsis))).toList(),
                          onChanged: (value) => setState(() => semesterFilter = value ?? 'All'),
                        ),
                      ),
                      const Spacer(),
                      FilledButton.icon(
                        onPressed: () => editEvaluation(context, null, refreshEvaluations),
                        icon: const Icon(Icons.add_rounded),
                        label: const Text('Add Evaluation'),
                      ),
                    ]),
                  ),
                ),
                const SizedBox(height: 14),
                Expanded(
                  child: TabBarView(children: [
                    EvaluationTypeTable(
                      rows: rows,
                      title: 'Superior Evaluation',
                      reportPeriod: reportPeriod,
                      ratingKey: 'superior_rating',
                      descriptionKey: 'superior_description',
                      type: EvaluationType.superior,
                      onEdit: (row) => editEvaluation(context, row, refreshEvaluations),
                      onDelete: (row) async {
                        await db.from('evaluation_records').delete().eq('id', row['id']);
                        refreshEvaluations();
                      },
                    ),
                    EvaluationTypeTable(
                      rows: rows,
                      title: 'Peer-to-peer Evaluation',
                      reportPeriod: reportPeriod,
                      ratingKey: 'peer_rating',
                      descriptionKey: 'peer_description',
                      type: EvaluationType.peer,
                      onEdit: (row) => editEvaluation(context, row, refreshEvaluations),
                      onDelete: (row) async {
                        await db.from('evaluation_records').delete().eq('id', row['id']);
                        refreshEvaluations();
                      },
                    ),
                    EvaluationTypeTable(
                      rows: rows,
                      title: 'Self Evaluation',
                      reportPeriod: reportPeriod,
                      ratingKey: 'self_rating',
                      descriptionKey: 'self_description',
                      type: EvaluationType.self,
                      onEdit: (row) => editEvaluation(context, row, refreshEvaluations),
                      onDelete: (row) async {
                        await db.from('evaluation_records').delete().eq('id', row['id']);
                        refreshEvaluations();
                      },
                    ),
                    EvaluationTypeTable(
                      rows: rows,
                      title: 'Student Evaluation',
                      reportPeriod: reportPeriod,
                      ratingKey: 'student_rating',
                      descriptionKey: 'student_description',
                      type: EvaluationType.student,
                      onEdit: (row) => editEvaluation(context, row, refreshEvaluations),
                      onDelete: (row) async {
                        await db.from('evaluation_records').delete().eq('id', row['id']);
                        refreshEvaluations();
                      },
                    ),
                  ]),
                ),
              ]),
            );
          },
        ),
      );
}

enum EvaluationType { superior, peer, self, student }

class EvaluationTypeTable extends StatelessWidget {
  final List<Map<String, dynamic>> rows;
  final String title;
  final String reportPeriod;
  final String ratingKey;
  final String descriptionKey;
  final EvaluationType type;
  final void Function(Map<String, dynamic> row) onEdit;
  final Future<void> Function(Map<String, dynamic> row) onDelete;

  const EvaluationTypeTable({
    super.key,
    required this.rows,
    required this.title,
    required this.reportPeriod,
    required this.ratingKey,
    required this.descriptionKey,
    required this.type,
    required this.onEdit,
    required this.onDelete,
  });

  static const double noWidth = 54;
  static const double nameWidth = 390;
  static const double ratingWidth = 130;
  static const double descriptionWidth = 250;
  static const double actionWidth = 112;
  static const double tableWidth = noWidth + nameWidth + ratingWidth + descriptionWidth + actionWidth;

  Widget _cell(
    Widget child,
    double width, {
    double height = 34,
    Color color = Colors.white,
    Alignment alignment = Alignment.center,
    EdgeInsets padding = const EdgeInsets.symmetric(horizontal: 6),
  }) => Container(
        width: width,
        height: height,
        alignment: alignment,
        padding: padding,
        decoration: BoxDecoration(color: color, border: Border.all(color: Colors.black.withOpacity(0.68), width: 0.6)),
        child: child,
      );

  Widget _textCell(String value, double width, {double height = 34, Color color = Colors.white, bool bold = false, Alignment alignment = Alignment.center}) => _cell(
        Text(value, maxLines: 2, overflow: TextOverflow.ellipsis, textAlign: TextAlign.center, style: TextStyle(fontSize: 11, fontWeight: bold ? FontWeight.w800 : FontWeight.w600, color: Colors.black)),
        width,
        height: height,
        color: color,
        alignment: alignment,
      );

  String _ratingText(Object? value) {
    final n = num.tryParse('${value ?? ''}'.replaceAll(',', '').trim());
    if (n == null) return '';
    return n % 1 == 0 ? n.toInt().toString() : n.toStringAsFixed(2).replaceFirst(RegExp(r'0$'), '').replaceFirst(RegExp(r'\.$'), '');
  }

  String _description(Map<String, dynamic> row) {
    final existing = formatValueRaw(row[descriptionKey]).trim();
    if (existing.isNotEmpty && existing != '-') return existing.toUpperCase();
    final rating = num.tryParse('${row[ratingKey] ?? ''}');
    if (rating == null) {
      if (type == EvaluationType.student) return 'FAILED';
      if (type == EvaluationType.self) return 'UNSATISFACTORY';
      return 'UNACCEPTABLE';
    }
    switch (type) {
      case EvaluationType.self:
        if (rating >= 4.5) return 'OUTSTANDING';
        if (rating >= 4.0) return 'VERY SATISFACTORY';
        if (rating >= 3.0) return 'SATISFACTORY';
        return 'UNSATISFACTORY';
      case EvaluationType.student:
        if (rating >= 4.2) return 'EXCELLENT';
        if (rating >= 3.4) return 'GOOD';
        if (rating >= 2.6) return 'FAIR';
        return 'FAILED';
      case EvaluationType.superior:
      case EvaluationType.peer:
        if (rating >= 85) return 'EXCEEDS EXPECTATION';
        if (rating >= 75) return 'MEETS EXPECTATION';
        return 'UNACCEPTABLE';
    }
  }

  Color _ratingColor(Object? value) {
    final rating = num.tryParse('${value ?? ''}');
    if (rating == null) return Colors.white;
    if (type == EvaluationType.superior) {
      if (rating >= 90) return const Color(0xFF84CC6A);
      if (rating >= 85) return const Color(0xFFA6D96A);
      if (rating >= 75) return const Color(0xFFC5E384);
      return const Color(0xFFF4CCCC);
    }
    if (type == EvaluationType.peer) {
      if (rating >= 95) return const Color(0xFF63BE7B);
      if (rating >= 85) return const Color(0xFF92D050);
      if (rating >= 75) return const Color(0xFFC5E384);
      return const Color(0xFFF4CCCC);
    }
    return Colors.white;
  }

  Widget _header(String text, double width, {double height = 30}) => _cell(
        Text(text, textAlign: TextAlign.center, style: const TextStyle(fontSize: 11, fontWeight: FontWeight.w900, color: Colors.black)),
        width,
        height: height,
        color: const Color(0xFF94A3B8),
      );

  Widget _subHeader(String text, double width) => _cell(
        Text(text, textAlign: TextAlign.center, style: const TextStyle(fontSize: 10.5, fontWeight: FontWeight.w900, color: Colors.black)),
        width,
        height: 28,
        color: const Color(0xFFB7C3D0),
      );

  Widget _dataRow(Map<String, dynamic> row, int index) => Row(children: [
        _textCell('${index + 1}', noWidth, height: 30),
        _cell(Text(formatValue(row['employee_name']), maxLines: 1, overflow: TextOverflow.ellipsis, style: const TextStyle(fontSize: 11, fontWeight: FontWeight.w700)), nameWidth, height: 30, alignment: Alignment.centerLeft),
        _textCell(_ratingText(row[ratingKey]), ratingWidth, height: 30, color: _ratingColor(row[ratingKey])),
        _textCell(_description(row), descriptionWidth, height: 30),
        _cell(Row(mainAxisAlignment: MainAxisAlignment.center, children: [
          IconButton(icon: const Icon(Icons.edit_rounded, size: 18), tooltip: 'Edit', padding: EdgeInsets.zero, constraints: const BoxConstraints.tightFor(width: 36, height: 30), onPressed: () => onEdit(row)),
          IconButton(
            icon: const Icon(Icons.delete_outline_rounded, size: 18, color: _danger),
            tooltip: 'Delete',
            padding: EdgeInsets.zero,
            constraints: const BoxConstraints.tightFor(width: 36, height: 30),
            onPressed: () async => onDelete(row),
          ),
        ]), actionWidth, height: 30),
      ]);

  @override
  Widget build(BuildContext context) {
    if (rows.isEmpty) return const EmptyBox();
    return Card(
      child: ClipRRect(
        borderRadius: BorderRadius.circular(22),
        child: Scrollbar(
          thumbVisibility: true,
          child: SingleChildScrollView(
            scrollDirection: Axis.horizontal,
            child: SizedBox(
              width: tableWidth,
              child: Column(children: [
                Container(width: tableWidth, height: 30, color: const Color(0xFFFF0000), alignment: Alignment.center, child: const Text('Cronasia Foundation College, Inc.', style: TextStyle(color: Colors.white, fontSize: 12, fontWeight: FontWeight.w900))),
                Container(width: tableWidth, height: 22, color: const Color(0xFFFFD966), alignment: Alignment.center, child: Text('$title  |  $reportPeriod', style: const TextStyle(color: Colors.black, fontSize: 12, fontWeight: FontWeight.w900))),
                Row(children: [
                  _header('NO.', noWidth),
                  _header('Name', nameWidth),
                  _header(title, ratingWidth + descriptionWidth),
                  _header('Actions', actionWidth),
                ]),
                Row(children: [
                  _subHeader('', noWidth),
                  _subHeader('', nameWidth),
                  _subHeader('RATING', ratingWidth),
                  _subHeader('Description', descriptionWidth),
                  _subHeader('', actionWidth),
                ]),
                Expanded(
                  child: SingleChildScrollView(
                    child: Column(children: [
                      for (var i = 0; i < rows.length; i++) _dataRow(rows[i], i),
                    ]),
                  ),
                ),
              ]),
            ),
          ),
        ),
      ),
    );
  }
}

'''

text = text[:page_start] + evaluation_tabs_block + text[page_end:]

# Add description fields to the add/edit evaluation dialog if the old field list is still present.
old_eval_fields = """      const EditField('superior_rating', 'Superior Rating', kind: FieldKind.number),\n      const EditField('peer_rating', 'Peer Rating', kind: FieldKind.number),\n      const EditField('self_rating', 'Self Rating', kind: FieldKind.number),\n      const EditField('student_rating', 'Student Rating', kind: FieldKind.number),\n      const EditField('total_rating', 'Total Rating', kind: FieldKind.number),\n      const EditField('total_description', 'Description'),"""
new_eval_fields = """      const EditField('superior_rating', 'Superior Rating', kind: FieldKind.number),\n      const EditField('superior_description', 'Superior Description'),\n      const EditField('peer_rating', 'Peer Rating', kind: FieldKind.number),\n      const EditField('peer_description', 'Peer Description'),\n      const EditField('self_rating', 'Self Rating', kind: FieldKind.number),\n      const EditField('self_description', 'Self Description'),\n      const EditField('student_rating', 'Student Rating', kind: FieldKind.number),\n      const EditField('student_description', 'Student Description'),\n      const EditField('total_rating', 'Total Rating', kind: FieldKind.number),\n      const EditField('total_description', 'Overall Description'),"""
if old_eval_fields in text:
    text = text.replace(old_eval_fields, new_eval_fields, 1)

if text != original:
    MAIN_DART.write_text(text, encoding='utf-8')
    print('Applied tabbed evaluation table update to lib/main.dart.')
else:
    print('No changes needed.')
