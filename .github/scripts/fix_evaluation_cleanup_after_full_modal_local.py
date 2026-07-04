from pathlib import Path

path = Path('lib/main.dart')
if not path.exists():
    raise SystemExit('Run this script from the Flutter project root. lib/main.dart was not found.')

text = path.read_text(encoding='utf-8-sig')
original = text


def find_function_end(source: str, start: int) -> int:
    brace = source.find('{', start)
    if brace < 0:
        raise SystemExit('Could not find opening brace for function.')
    depth = 0
    in_single = False
    in_double = False
    escape = False
    i = brace
    while i < len(source):
        ch = source[i]
        if in_single:
            if escape:
                escape = False
            elif ch == '\\':
                escape = True
            elif ch == "'":
                in_single = False
            i += 1
            continue
        if in_double:
            if escape:
                escape = False
            elif ch == '\\':
                escape = True
            elif ch == '"':
                in_double = False
            i += 1
            continue
        if ch == "'":
            in_single = True
        elif ch == '"':
            in_double = True
        elif ch == '{':
            depth += 1
        elif ch == '}':
            depth -= 1
            if depth == 0:
                end = i + 1
                while end < len(source) and source[end] in ' \t\r\n':
                    end += 1
                return end
        i += 1
    raise SystemExit('Could not find closing brace for function.')

# The previous full-evaluation patch can leave partial old evaluation helper code
# after editCertificate and before approveRanking. Remove that whole leftover area.
edit_cert_sig = 'Future<void> editCertificate(BuildContext context, Map<String, dynamic>? row,'
approve_sig = 'Future<void> approveRanking('
edit_start = text.find(edit_cert_sig)
approve_start = text.find(approve_sig, edit_start)
if edit_start >= 0 and approve_start > edit_start:
    edit_end = find_function_end(text, edit_start)
    if edit_end < approve_start:
        text = text[:edit_end] + '\n' + text[approve_start:]
        print('Removed stale evaluation helper/editEvaluation leftovers after editCertificate.')

# Ensure the per-tab table has no Add button and uses the whole edit modal only.
text = text.replace("""        addLabel: 'Add Evaluation',
        reportTitle: '$title Report',""", """        addLabel: 'Add Evaluation',
        allowAdd: false,
        reportTitle: '$title Report',""")
text = text.replace(
    """        onAdd: (ctx, refresh) => editEvaluation(ctx, null, refresh),
        onEdit: editEvaluation,""",
    """        onView: viewEvaluation,
        onEdit: editFullEvaluation,""",
)
text = text.replace(
    """        onAdd: (ctx, refresh) => editEvaluationForKind(ctx, null, refresh, kind),
        onView: viewEvaluation,
        onEdit: (ctx, row, refresh) => editEvaluationForKind(ctx, row, refresh, kind),""",
    """        onView: viewEvaluation,
        onEdit: editFullEvaluation,""",
)

# Remove any isolated broken fragment from an expression-bodied evaluationRatingLabel
# function if one still exists in the stale area.
broken = """;
;
;
;
Rating (out of ${evaluationMaxScore(kind).toStringAsFixed(0)})';
"""
text = text.replace(broken, '')

path.write_text(text, encoding='utf-8')
if text == original:
    print('No changes applied. The evaluation cleanup may already be fixed.')
else:
    print('Cleaned evaluation full modal patch leftovers.')
