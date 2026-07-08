from pathlib import Path

path = Path('lib/main.dart')
if not path.exists():
    raise SystemExit('Run this script from the Flutter project root. lib/main.dart was not found.')

text = path.read_text(encoding='utf-8-sig')
original = text

# Overall tab should still keep the columns because full-time employees use
# Superior and Peer-to-Peer in the overall computation. For PART-TIME rows,
# those two values must display as blank / not applicable and must not be
# included in the total.
old = """    final normalized = rows.map((item) {
      final row = normalizeRow(Map<String, dynamic>.from(item as Map));
      final recomputed = recomputeEvaluationTotals(row);
      row['total_rating'] = recomputed['total_rating'];
      row['total_description'] = recomputed['total_description'];
      return row;
    }).toList();"""
new = """    final normalized = rows.map((item) {
      final row = normalizeRow(Map<String, dynamic>.from(item as Map));
      final recomputed = recomputeEvaluationTotals(row);
      row['total_rating'] = recomputed['total_rating'];
      row['total_description'] = recomputed['total_description'];
      if (isPartTimeEvaluationRow(recomputed)) {
        row['superior_rating'] = null;
        row['superior_description'] = null;
        row['peer_rating'] = null;
        row['peer_description'] = null;
      }
      return row;
    }).toList();"""
if old in text:
    text = text.replace(old, new, 1)

# In the overall View modal, do not show Superior and Peer-to-Peer details for
# part-time employees.
text = text.replace(
    """  final normalized = normalizeRow(row);
  final computed = recomputeEvaluationTotals(normalized);""",
    """  final normalized = normalizeRow(row);
  final computed = recomputeEvaluationTotals(normalized);
  final isPartTime = isPartTimeEvaluationRow(computed);""",
    1,
)

old_view = """              DetailTile('Superior Rating / 100',
                  evaluationScoreDisplay(normalized['superior_rating'])),
              DetailTile(
                  'Superior Description',
                  evaluationScoreDescription(
                      EvaluationKind.superior, normalized['superior_rating'])),
              DetailTile('Peer-to-Peer Rating / 100',
                  evaluationScoreDisplay(normalized['peer_rating'])),
              DetailTile(
                  'Peer-to-Peer Description',
                  evaluationScoreDescription(
                      EvaluationKind.peer, normalized['peer_rating'])),"""
new_view = """              if (!isPartTime) ...[
                DetailTile('Superior Rating / 100',
                    evaluationScoreDisplay(normalized['superior_rating'])),
                DetailTile(
                    'Superior Description',
                    evaluationScoreDescription(EvaluationKind.superior,
                        normalized['superior_rating'])),
                DetailTile('Peer-to-Peer Rating / 100',
                    evaluationScoreDisplay(normalized['peer_rating'])),
                DetailTile(
                    'Peer-to-Peer Description',
                    evaluationScoreDescription(
                        EvaluationKind.peer, normalized['peer_rating'])),
              ],"""
if old_view in text:
    text = text.replace(old_view, new_view, 1)

path.write_text(text, encoding='utf-8')
if text == original:
    print('No changes applied. Overall part-time display may already be fixed.')
else:
    print('Fixed Overall tab: PART-TIME rows no longer show Superior/Peer values.')
