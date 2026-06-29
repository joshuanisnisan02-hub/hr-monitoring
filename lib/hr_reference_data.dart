import 'package:supabase_flutter/supabase_flutter.dart';

class HrReferenceOption {
  final String value;
  final String label;
  final num? salary;

  const HrReferenceOption({required this.value, required this.label, this.salary});
}

Future<List<HrReferenceOption>> loadHrReferenceOptions(String category) async {
  final rows = await Supabase.instance.client
      .from('hr_reference_options')
      .select('label, value, salary')
      .eq('category', category)
      .eq('is_active', true)
      .order('sort_order')
      .order('label');

  return rows.map<HrReferenceOption>((row) {
    final label = (row['label'] ?? '').toString();
    final value = (row['value'] ?? label).toString();
    final salary = num.tryParse('${row['salary'] ?? ''}');
    return HrReferenceOption(value: value, label: label, salary: salary);
  }).toList();
}
