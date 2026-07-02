from pathlib import Path
import re

MAIN_DART = Path('lib/main.dart')
if not MAIN_DART.exists():
    raise SystemExit('Run this from the Flutter project root. lib/main.dart was not found.')

text = MAIN_DART.read_text(encoding='utf-8')
original = text

load_eval_pattern = re.compile(r"Future<List<dynamic>> loadEvaluations\(\{int limit = 1500\}\) => db\.from\('evaluation_records'\)\.select\([^\n]+?\)\.order\('academic_year'\)[^\n]*?\.limit\(limit\);")
load_eval_replacement = "Future<List<dynamic>> loadEvaluations({int limit = 1500}) => db.from('evaluation_records').select('id, employee_id, academic_year, semester, superior_rating, superior_description, peer_rating, peer_description, self_rating, self_description, student_rating, student_description, total_rating, total_description, employees(full_name)').order('academic_year', ascending: false).order('semester', ascending: false).limit(limit);"
text, load_count = load_eval_pattern.subn(load_eval_replacement, text, count=1)
if load_count == 0 and 'superior_description' not in text[text.find("Future<List<dynamic>> loadEvaluations"):text.find("Future<List<dynamic>> loadRankings")]:
    raise SystemExit('Could not update loadEvaluations select list.')

page_start = text.find('class EvaluationsPage extends')
page_end = text.find('class AppointmentPage extends', page_start)
if page_start == -1 or page_end == -1:
    raise SystemExit('Could not find EvaluationsPage block boundaries.')

evaluation_page_replacement = r'''class EvaluationsPage extends StatefulWidget {
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
        subtitle: 'Faculty and staff evaluation record styled after the LIST Excel evaluation sheet.',
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
            final titleParts = <String>[
              if (academicYearFilter != 'All') 'A.Y. $academicYearFilter' else 'All Academic Years',
              if (semesterFilter != 'All') semesterFilter else 'All Semesters',
            ];

            return Column(children: [
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
                child: EvaluationExcelTable(
                  rows: rows,
                  reportTitle: titleParts.join(' - '),
                  onEdit: (row) => editEvaluation(context, row, refreshEvaluations),
                  onDelete: (row) async {
                    await db.from('evaluation_records').delete().eq('id', row['id']);
                    refreshEvaluations();
                  },
                ),
              ),
            ]);
          },
        ),
      );
}

class EvaluationExcelTable extends StatelessWidget {
  final List<Map<String, dynamic>> rows;
  final String reportTitle;
  final void Function(Map<String, dynamic> row) onEdit;
  final Future<void> Function(Map<String, dynamic> row) onDelete;

  const EvaluationExcelTable({super.key, required this.rows, required this.reportTitle, required this.onEdit, required this.onDelete});

  static const double noWidth = 54;
  static const double nameWidth = 310;
  static const double ratingWidth = 96;
  static const double descriptionWidth = 170;
  static const double actionWidth = 104;
  static const double tableWidth = noWidth + nameWidth + ((ratingWidth + descriptionWidth) * 4) + actionWidth;

  Widget _cell(
    Widget child,
    double width, {
    double height = 34,
    Color color = Colors.white,
    Alignment alignment = Alignment.center,
    EdgeInsets padding = const EdgeInsets.symmetric(horizontal: 6),
    Border? border,
  }) => Container(
        width: width,
        height: height,
        alignment: alignment,
        padding: padding,
        decoration: BoxDecoration(
          color: color,
          border: border ?? Border.all(color: Colors.black.withOpacity(0.68), width: 0.6),
        ),
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

  String _evaluationDescription(Map<String, dynamic> row, String descriptionKey, String ratingKey, String type) {
    final existing = formatValueRaw(row[descriptionKey]).trim();
    if (existing.isNotEmpty && existing != '-') return existing.toUpperCase();
    final rating = num.tryParse('${row[ratingKey] ?? ''}');
    if (rating == null) return type == 'student' ? 'FAILED' : type == 'self' ? 'UNSATISFACTORY' : 'UNACCEPTABLE';
    if (type == 'self') {
      if (rating >= 4.5) return 'OUTSTANDING';
      if (rating >= 4.0) return 'VERY SATISFACTORY';
      if (rating >= 3.0) return 'SATISFACTORY';
      return 'UNSATISFACTORY';
    }
    if (type == 'student') {
      if (rating >= 4.2) return 'EXCELLENT';
      if (rating >= 3.4) return 'GOOD';
      if (rating >= 2.6) return 'FAIR';
      return 'FAILED';
    }
    if (rating >= 85) return 'EXCEEDS EXPECTATION';
    if (rating >= 75) return 'MEETS EXPECTATION';
    return 'UNACCEPTABLE';
  }

  Color _ratingColor(Object? value, String type) {
    final rating = num.tryParse('${value ?? ''}');
    if (rating == null) return Colors.white;
    if (type == 'superior') {
      if (rating >= 90) return const Color(0xFF84CC6A);
      if (rating >= 85) return const Color(0xFFA6D96A);
      if (rating >= 75) return const Color(0xFFC5E384);
      return const Color(0xFFF4CCCC);
    }
    if (type == 'peer') {
      if (rating >= 95) return const Color(0xFF63BE7B);
      if (rating >= 85) return const Color(0xFF92D050);
      if (rating >= 75) return const Color(0xFFC5E384);
      return const Color(0xFFF4CCCC);
    }
    return Colors.white;
  }

  Widget _headerGroup(String title, double width) => _cell(
        Text(title, textAlign: TextAlign.center, style: const TextStyle(fontSize: 11, fontWeight: FontWeight.w900, color: Colors.black)),
        width,
        height: 30,
        color: const Color(0xFF94A3B8),
      );

  Widget _subHeader(String title, double width) => _cell(
        Text(title, textAlign: TextAlign.center, style: const TextStyle(fontSize: 10.5, fontWeight: FontWeight.w900, color: Colors.black)),
        width,
        height: 28,
        color: const Color(0xFFB7C3D0),
      );

  Widget _dataRow(Map<String, dynamic> row, int index) => Row(children: [
        _textCell('${index + 1}', noWidth, height: 28),
        _cell(Text(formatValue(row['employee_name']), maxLines: 1, overflow: TextOverflow.ellipsis, style: const TextStyle(fontSize: 11, fontWeight: FontWeight.w700)), nameWidth, height: 28, alignment: Alignment.centerLeft),
        _textCell(_ratingText(row['superior_rating']), ratingWidth, height: 28, color: _ratingColor(row['superior_rating'], 'superior')),
        _textCell(_evaluationDescription(row, 'superior_description', 'superior_rating', 'superior'), descriptionWidth, height: 28),
        _textCell(_ratingText(row['peer_rating']), ratingWidth, height: 28, color: _ratingColor(row['peer_rating'], 'peer')),
        _textCell(_evaluationDescription(row, 'peer_description', 'peer_rating', 'peer'), descriptionWidth, height: 28),
        _textCell(_ratingText(row['self_rating']), ratingWidth, height: 28),
        _textCell(_evaluationDescription(row, 'self_description', 'self_rating', 'self'), descriptionWidth, height: 28),
        _textCell(_ratingText(row['student_rating']), ratingWidth, height: 28),
        _textCell(_evaluationDescription(row, 'student_description', 'student_rating', 'student'), descriptionWidth, height: 28),
        _cell(Row(mainAxisAlignment: MainAxisAlignment.center, children: [
          IconButton(icon: const Icon(Icons.edit_rounded, size: 17), tooltip: 'Edit', padding: EdgeInsets.zero, constraints: const BoxConstraints.tightFor(width: 34, height: 28), onPressed: () => onEdit(row)),
          IconButton(
            icon: const Icon(Icons.delete_outline_rounded, size: 17, color: _danger),
            tooltip: 'Delete',
            padding: EdgeInsets.zero,
            constraints: const BoxConstraints.tightFor(width: 34, height: 28),
            onPressed: () async => onDelete(row),
          ),
        ]), actionWidth, height: 28),
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
                Container(width: tableWidth, height: 22, color: const Color(0xFFFFD966), alignment: Alignment.center, child: Text(reportTitle, style: const TextStyle(color: Colors.black, fontSize: 12, fontWeight: FontWeight.w900))),
                Row(children: [
                  _headerGroup('NO.', noWidth),
                  _headerGroup('Name', nameWidth),
                  _headerGroup('Superior Evaluation', ratingWidth + descriptionWidth),
                  _headerGroup('PEER-TO-PEER EVALUATION', ratingWidth + descriptionWidth),
                  _headerGroup('SELF EVALUATION', ratingWidth + descriptionWidth),
                  _headerGroup('Student Evaluation', ratingWidth + descriptionWidth),
                  _headerGroup('Actions', actionWidth),
                ]),
                Row(children: [
                  _subHeader('', noWidth),
                  _subHeader('', nameWidth),
                  _subHeader('RATING', ratingWidth),
                  _subHeader('Description', descriptionWidth),
                  _subHeader('RATING', ratingWidth),
                  _subHeader('Description', descriptionWidth),
                  _subHeader('RATING', ratingWidth),
                  _subHeader('Description', descriptionWidth),
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

text = text[:page_start] + evaluation_page_replacement + text[page_end:]

old_eval_fields = """      const EditField('superior_rating', 'Superior Rating', kind: FieldKind.number),\n      const EditField('peer_rating', 'Peer Rating', kind: FieldKind.number),\n      const EditField('self_rating', 'Self Rating', kind: FieldKind.number),\n      const EditField('student_rating', 'Student Rating', kind: FieldKind.number),\n      const EditField('total_rating', 'Total Rating', kind: FieldKind.number),\n      const EditField('total_description', 'Description'),"""
new_eval_fields = """      const EditField('superior_rating', 'Superior Rating', kind: FieldKind.number),\n      const EditField('superior_description', 'Superior Description'),\n      const EditField('peer_rating', 'Peer Rating', kind: FieldKind.number),\n      const EditField('peer_description', 'Peer Description'),\n      const EditField('self_rating', 'Self Rating', kind: FieldKind.number),\n      const EditField('self_description', 'Self Description'),\n      const EditField('student_rating', 'Student Rating', kind: FieldKind.number),\n      const EditField('student_description', 'Student Description'),\n      const EditField('total_rating', 'Total Rating', kind: FieldKind.number),\n      const EditField('total_description', 'Overall Description'),"""
if old_eval_fields in text:
    text = text.replace(old_eval_fields, new_eval_fields, 1)

if text != original:
    MAIN_DART.write_text(text, encoding='utf-8')
    print('Applied Excel-style evaluation table update to lib/main.dart.')
else:
    print('No changes needed.')
