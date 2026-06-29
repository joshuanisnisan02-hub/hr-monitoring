import 'package:flutter/material.dart';
import 'package:supabase_flutter/supabase_flutter.dart';

import 'hr_modern_app_v2.dart';

const projectUrl = String.fromEnvironment(
  'SUPABASE_URL',
  defaultValue: 'https://iysbzkdczngvafvtwpjn.supabase.co',
);
const publicClientKey = String.fromEnvironment(
  'SUPABASE_PUBLIC_CLIENT_KEY',
  defaultValue: 'sb_publishable_QJuRm0RkkQfbgAnBPPxbYw_AtG0BK3o',
);

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await Supabase.initialize(url: projectUrl, anonKey: publicClientKey);
  runApp(const HrModernAppV2());
}
