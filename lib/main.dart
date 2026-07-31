// ignore: avoid_web_libraries_in_flutter
import 'dart:html' as html;
import 'dart:async';
import 'dart:typed_data';

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:intl/intl.dart';
import 'package:supabase_flutter/supabase_flutter.dart';

const projectUrl = String.fromEnvironment(
  'SUPABASE_URL',
  defaultValue: 'https://iysbzkdczngvafvtwpjn.supabase.co',
);
const publicClientKey = String.fromEnvironment(
  'SUPABASE_PUBLIC_CLIENT_KEY',
  defaultValue: 'sb_publishable_QJuRm0RkkQfbgAnBPPxbYw_AtG0BK3o',
);

const _primary = Color(0xFF2563EB);
const _accent = Color(0xFF4F63B6);
const _ink = Color(0xFF0F172A);
const _muted = Color(0xFF64748B);
const _bg = Color(0xFFF4F7FB);
const _line = Color(0xFFE2E8F0);
const _danger = Color(0xFFDC2626);
const _surface = Color(0xFFFFFFFF);
const _surfaceSoft = Color(0xFFF8FAFC);
const _primarySoft = Color(0xFFEFF6FF);
const _shadowSoft = Color(0x140F172A);
const _pageSize = 10;

SupabaseClient get db => Supabase.instance.client;

class DateSlashInputFormatter extends TextInputFormatter {
  @override
  TextEditingValue formatEditUpdate(
      TextEditingValue oldValue, TextEditingValue newValue) {
    var digits = newValue.text.replaceAll(RegExp(r'\D'), '');
    if (digits.length > 8) digits = digits.substring(0, 8);
    final out = StringBuffer();
    for (var i = 0; i < digits.length; i++) {
      if (i == 2 || i == 4) out.write('/');
      out.write(digits[i]);
    }
    final value = out.toString();
    return TextEditingValue(
      text: value,
      selection: TextSelection.collapsed(offset: value.length),
    );
  }
}

void safeRefresh(VoidCallback refresh) {
  WidgetsBinding.instance.addPostFrameCallback((_) => refresh());
}

bool shouldUpperCaseDataKey(String key) {
  final k = key.toLowerCase();
  if (k == 'id' || k == 'created_at' || k == 'updated_at') return false;
  if (k.endsWith('_id') || k == 'employee_id' || k == 'cycle_id') return false;
  if (k.contains('url') || k.contains('email')) return false;
  if (k.contains('date') || k == 'expiry_date' || k == 'issued_date')
    return false;
  return true;
}

dynamic upperCaseDataValue(String key, dynamic value) {
  if (value is String) {
    final clean = value.trim();
    if (clean.isEmpty) return clean;
    return shouldUpperCaseDataKey(key) ? clean.toUpperCase() : clean;
  }
  if (value is Map) {
    return upperCaseDataMap(Map<String, dynamic>.from(value));
  }
  if (value is List) {
    return value
        .map((item) => item is Map
            ? upperCaseDataMap(Map<String, dynamic>.from(item))
            : item)
        .toList();
  }
  return value;
}

Map<String, dynamic> upperCaseDataMap(Map<String, dynamic> data) {
  final out = <String, dynamic>{};
  data.forEach((key, value) {
    out[key] = upperCaseDataValue(key, value);
  });
  return out;
}

final Map<String, List<dynamic>> _crudTableDataCache =
    <String, List<dynamic>>{};

// OFFICIAL_ACTIVE_EMPLOYEE_LIST_START
const List<String> officialActiveEmployeeNames = <String>[
  'Aba, Mary Stephanie',
  'Advincula, Jesel C., LPT',
  'Agustin, Wowie D., LPT',
  'Alegato, Mark Lhister',
  'Amlato, Jeroboam C.',
  'Andang, Abdulgani T., MSCRIM, RCRIM',
  'AniÃƒÆ’Ã‚Â±on, Clotilde P., LPT',
  'Avenido, Restituto Jr., E., MBM, LPT',
  'Ballista, Beverly Joy, LPT',
  'Bangcong, Charyn P., LPT',
  'Batilaran, Quirico JR. M., RCG',
  'Beatingo, Dave Bryan J.',
  'Behiga, Charissa Mae G., MAED, LPT',
  'Belgar, Christian John',
  'Belgira, Judy Ann, LPT',
  'Belvar, Cristian Ric H., LPT',
  'Besonia, Kwin Y.',
  'Bigno, Jhon Bernand D. , LPT',
  'Bioco, Aijelon',
  'Borongan, Gibb B., MPA, LPT',
  'Borro, Enarcisa P., MAED',
  'Caballero, Annajane R., RCRIM',
  'Cabarubias, Monica B., RL',
  'Cabidog, Mary Monica, LPT',
  'Cabrera, Kristine J., MBM, LPT',
  'Cagande, Eryll John, LPT',
  'Cahilig, Christian',
  'Calle, Reycart C.',
  'Campilan, Gremar',
  'Canales, Janine Hope',
  'Caparoso, Marie Claire, LPT',
  'Carlon, Marian P., LPT',
  'Casi, Irene W., RCRIM',
  'Cauntao, Karen Grace A., LPT',
  'Celo, Lisa L., RL',
  'Centes, Cynthia B., MBM, LPT',
  'Ciudad, Mai Grape G., MAED, LPT',
  'Cocjin, Charry, RN',
  'Colipano, Tessie R., Ph.D',
  'Cuyos, Marites M., MBM',
  'Cuyos, Rosso, MBM',
  'Dalayap, Lloyd A., PHD, RPM',
  'Dalogdog, Joehmar B., MSCJ,RCRIM',
  'Dapsan, Eldie John L., LPT',
  'David, Elenito G.',
  'Dayaganon, Jenneal A.',
  'De Castro, Christopher JR., MSCJ, RCRIM',
  'De Vera, Freden S.',
  'Digan, Licona A., PhD',
  'Dionio, Rosie Shane T., RCRIM',
  'Dona, Cris, LPT',
  'Doyac, Adrian S., LPT',
  'Dumilig, Ernan C., LPT',
  'Duran, Leomil Jay B., MIT, LPT',
  'Duran, Zulaika, LPT',
  'Ebona, James Edmund, LPT',
  'Epil, Saturnino D., Jr., RSW',
  'Espinoza, Joan R., MBM,LPT, CHRA',
  'Filoteo, Alan D.',
  'Flores, Willyn L., RSW',
  'Gallardo, Justin Dave B.',
  'Gallardo, Erma, LPT',
  'Gamil, Honey Mae S., RCRIM',
  'Gania, Mark Joseph P., RCRIM',
  'Gasan, Christian Mae, LPT',
  'Germinal, Jenelyn',
  'Germinal, Juvan Roy D., CPA',
  'Gortisano, Rene D., MBM, LPT, CHRA, CHP',
  'Gruzo, Emmanuel Hope C., CPA',
  'Hassan, Almaddie',
  'Hermoso, Alberto',
  'Hitalia, Ma. Cresanta G.,MBM',
  'Hoyohoy, Ma. Lerma., LPT',
  'Hussin, Portia H., LPT',
  'Inderio, Karen Joy B.',
  'Jeronan, Yvonnie ., MAT-PE, LPT',
  'Jimenez, Joey S.',
  'Julius M. Bernardo, LPT',
  'Langgong, Charlotte K., MSSW, RSW',
  'Laroza, Cristine Lyn., LPT',
  'Linga, Jeazel S., LPT',
  'Lizada, Remart John P.',
  'Lumantas, Jonathan, LPT',
  'Luyang, Noraliza M., MBM, LPT',
  'Mahinay-Palmejar, Lovely D., LPT',
  'Mantua, Famila D.',
  'Maonio, June Ray C.',
  'Mariscal, Leane Jen C., LPT',
  'Marquez, Ariel DT., MAT-PE, LPT',
  'Medina, Nova Mae C., RPm',
  'Mentino, Rhea Christine, LPT',
  'Mina, Cathrena Jane A., LPT',
  'Mission, Erlinda., DM, CPA',
  'Momo, Marjorie G., MSCJ, RCRIM',
  'MontaÃƒÆ’Ã‚Â±o, Quencyfaith C., MBM, LPT',
  'Nacilla, Maria Fe MBA',
  'Nisnisan, Joshua',
  'Nocete,Fretch H.., PHD, MSHRM, LPT',
  'Non, Garda May G., MAED, LPT',
  'Non, Nenita, RL, MALS',
  'Ofiaza, Maria Sheena B., LPT',
  'Oreiro, Mark Dominic M., LPT',
  'Pabilona, Syrel John H., RL',
  'Palomares, Ma. Jessa A.',
  'Palon, Jovanny T., LPT',
  'Patangan, Princess Jouce B., MAED, LPT',
  'Patok JR., Sofonias P., LPT',
  'Patuar, Kenneth Joy, LPT',
  'Patuar, Nhaser, LPT',
  'Payongayong, Jeselle G., MAED, LPT',
  'Pedrigosa, Ma. Claudjean P.',
  'Pelobello, Suzaine Mae',
  'Pendon, Leonard David T.',
  'Peraman, Kimberly T., LPT',
  'Pilapil, Ariel Jhon',
  'Plarisan, Laica A., LPT',
  'Polalon, Jorita E., LPT',
  'Ponteres, Harold, LPT',
  'Prieto, Crissa Mae, LPT',
  'Pua, PCapt. Ronnie R., RCRIM',
  'Revilla, Creshyl F., LPT',
  'Roble, Arnel JR, LPT',
  'Roderos, Jobille Love, RSW',
  'Roman, Rosalia, MMREM, REA, REB, LPT',
  'Rosales, Honey Mae M., RSW',
  'Saligumba, Maria Era C., RSW',
  'Salmo, Whenah M., RCRIM',
  'Saludo, Ian Jay',
  'Santillan, Jessa Marie S., MBM,LPT',
  'Santos, Jectofer B., MAT-PE, LPT',
  'Sardalla, Allan',
  'Saulong, Ronelo A., RSW',
  'Sayson, Adams Jay, LPT',
  'Sebastian, Kristal Kae',
  'SeÃƒÆ’Ã‚Â±ires, Normie E., REB',
  'Serrano, Alvin Jay C., MAED, LPT',
  'Suhayon, Sylvester, LPT',
  'Suyao, Jethroel Hervey S., LPT',
  'Tagupa, Marychell N., LPT',
  'Tampos, Carvin Paul G.',
  'Ternora, Jhonmer F., LPT',
  'Tidalgo, Hermer B., MAED, LPT',
  'Tipawan, Frencess Jann O., LPT',
  'Titong, Salvador D., Jr., LPT',
  'Tobato, May Maeh V., MAED, LPT',
  'Tomampos, Ellah Jessa G., MBM, LPT',
  'Torcuator, Dennis Oliver G.',
  'Tres Reyes, Ronald C. MSPY',
  'Ubaldo, Ivy M., MAED',
  'Umadhay, Julius Czar., LPT',
  'Utay, Honey Babe Erica B.',
  'Valenzuela, Elvine',
  'Vazquez, Rea Joy G., MAPS, LPT',
  'Venancio, Daniel P., LPT',
  'Villamarzo, Joanne L., MAT-PE, LPT',
  'Villanueva, Rey F.',
  'Whittmer, Ira',
  'Yubal, Eugine P., LPT',
  'Zamora, Romel A., MAED, LPT',
  'Zapanta, Marivic P., MAED, LPT',
];

String officialEmployeeClean(String value) {
  var out = value
      .toLowerCase()
      .replaceAll('ÃƒÆ’Ã‚Â±', 'n')
      .replaceAll('ÃƒÆ’Ã‚Â¡', 'a')
      .replaceAll('ÃƒÆ’Ã‚Â©', 'e')
      .replaceAll('ÃƒÆ’Ã‚Â­', 'i')
      .replaceAll('ÃƒÆ’Ã‚Â³', 'o')
      .replaceAll('ÃƒÆ’Ã‚Âº', 'u')
      .replaceAll(RegExp(r'[^a-z0-9]+'), ' ')
      .replaceAll(RegExp(r'\s+'), ' ')
      .trim();

  final remove = <String>{
    'lpt',
    'maed',
    'mbm',
    'mscrim',
    'rcrim',
    'rcg',
    'rgc',
    'rl',
    'rn',
    'phd',
    'mba',
    'mit',
    'mssw',
    'rsw',
    'cpa',
    'mat',
    'pe',
    'maps',
    'map',
    'mmrem',
    'rea',
    'reb',
    'chra',
    'chp',
    'ctp',
    'mscj',
    'rpm',
    'prm',
    'mshrm',
    'dm',
    'mpa',
    'mspsy',
    'pcapt',
    'atty',
    'jr',
    'sr',
    'ii',
    'iii',
    'cepl',
    'dbm',
    'is',
    'mrm',
    'ce',
    'mrem',
    'cthm',
    'rmt',
    'mspsych'
  };

  return out
      .split(RegExp(r'\s+'))
      .where((token) => token.isNotEmpty && !remove.contains(token))
      .join(' ');
}

String officialEmployeeKey(Object? value) {
  var raw = '${value ?? ''}'.trim().toLowerCase();
  if (raw.isEmpty || raw == '-') return '';

  String lastPart;
  String restPart;

  final comma = raw.indexOf(',');
  if (comma >= 0) {
    lastPart = raw.substring(0, comma);
    restPart = raw.substring(comma + 1);
  } else {
    final cleaned = officialEmployeeClean(raw);
    final parts =
        cleaned.split(RegExp(r'\s+')).where((x) => x.isNotEmpty).toList();
    if (parts.isEmpty) return '';
    lastPart = parts.last;
    restPart =
        parts.length > 1 ? parts.sublist(0, parts.length - 1).join(' ') : '';
  }

  final last = officialEmployeeClean(lastPart);
  final rest = officialEmployeeClean(restPart);
  final tokens = rest.split(RegExp(r'\s+')).where((x) => x.isNotEmpty).toList();
  final first = tokens.isEmpty ? '' : tokens.first;

  return '$last|$first';
}

final Map<String, String> officialActiveEmployeeNameByKey = <String, String>{
  for (final name in officialActiveEmployeeNames)
    officialEmployeeKey(name): name,
};

bool isOfficialActiveEmployeeRow(Map<String, dynamic> row) {
  final possibleNames = <Object?>[
    row['full_name'],
    row['employee_name'],
    if (row['employees'] is Map) (row['employees'] as Map)['full_name'],
  ];

  for (final name in possibleNames) {
    final key = officialEmployeeKey(name);
    if (key.isNotEmpty && officialActiveEmployeeNameByKey.containsKey(key)) {
      return true;
    }
  }
  return false;
}
// OFFICIAL_ACTIVE_EMPLOYEE_LIST_END

String archiveModuleFromTitle(String? title, String fallback) {
  final raw = (title == null || title.trim().isEmpty) ? fallback : title;
  return raw.replaceAll(' Report', '').trim();
}

String archiveEmployeeNameFromRow(Map<String, dynamic> row) {
  if (row['employee_name'] != null) return formatValue(row['employee_name']);
  if (row['full_name'] != null) return formatValue(row['full_name']);
  if (row['employees'] is Map)
    return formatValue((row['employees'] as Map)['full_name']);
  return '-';
}

Object? archiveEmployeeIdFromRow(Map<String, dynamic> row) =>
    row['employee_id'] ?? row['id'];

Future<void> archiveRecordSnapshot({
  required String tableName,
  required String moduleName,
  required String archiveType,
  required Map<String, dynamic> row,
}) async {
  final normalized = normalizeRow(Map<String, dynamic>.from(row));
  await db.from('archived_records').insert({
    'module_name': moduleName,
    'table_name': tableName,
    'original_id': '${normalized['id'] ?? ''}',
    'employee_id': archiveEmployeeIdFromRow(normalized)?.toString(),
    'employee_name': archiveEmployeeNameFromRow(normalized),
    'archive_type': archiveType,
    'record_data': normalized,
    'archived_at': DateTime.now().toIso8601String(),
    'is_restored': false,
  });
}

Future<void> archiveDeletedRecord({
  required String? tableName,
  required String moduleName,
  required Map<String, dynamic> row,
}) async {
  if (tableName == null || tableName.trim().isEmpty) return;
  await archiveRecordSnapshot(
    tableName: tableName,
    moduleName: moduleName,
    archiveType: 'deleted',
    row: row,
  );
}

Future<void> archiveOldContractBeforeUpdate(String table, Object? id) async {
  if (table != 'employee_contracts' || id == null) return;
  try {
    final rows = await db
        .from('employee_contracts')
        .select(
            'id, employee_id, contract_type, contract_start_date, duration_months, contract_end_date, status, attachment_url, employees(full_name)')
        .eq('id', id)
        .limit(1);
    if (rows is List && rows.isNotEmpty) {
      await archiveRecordSnapshot(
        tableName: 'employee_contracts',
        moduleName: 'Contracts',
        archiveType: 'old_contract',
        row: normalizeRow(Map<String, dynamic>.from(rows.first as Map)),
      );
    }
  } catch (_) {}
}

Future<List<dynamic>> loadArchivedRecords({
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
    row['restore_status'] =
        row['is_restored'] == true ? 'Restored' : 'Archived';
    return row;
  }).where((row) {
    if (oldContracts || moduleFilters.isEmpty) return true;
    final moduleName = formatValue(row['module_name']).trim().toLowerCase();
    return moduleFilters.any((filter) => moduleName == filter.toLowerCase());
  }).toList();
}

Map<String, dynamic> archiveRestoreData(Map<String, dynamic> data) {
  final out = Map<String, dynamic>.from(data);
  out.remove('id');
  out.remove('employees');
  out.remove('ranking_cycles');
  out.remove('employee_name');
  out.remove('cycle_name');
  out.remove('date_hired_display');
  out.remove('date_resigned_display');
  out.remove('days_left');
  out.remove('license_ids');
  out.remove('license_records');
  out.remove('certificate_ids');
  out.remove('certificate_records');
  out.remove('safety_officer_ids');
  out.remove('safety_officer_records');
  out.removeWhere((key, value) => value == null || value.toString() == '-');
  return out;
}

Future<void> restoreArchivedRecord(BuildContext context,
    Map<String, dynamic> row, VoidCallback refresh) async {
  if (row['is_restored'] == true) {
    showSnack(context, 'This archive was already restored.');
    return;
  }
  final table = '${row['table_name'] ?? ''}'.trim();
  final dataRaw = row['record_data'];
  if (table.isEmpty || dataRaw is! Map) {
    showSnack(context, 'Archive data is incomplete.');
    return;
  }
  final ok = await showDialog<bool>(
    context: context,
    builder: (_) => AlertDialog(
      title: const Text('Restore Archived Record?'),
      content: Text(
          'This will restore ${formatValue(row['employee_name'])} back to ${formatValue(row['module_name'])} as a new active record.'),
      actions: [
        TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: const Text('Cancel')),
        FilledButton.icon(
          onPressed: () => Navigator.pop(context, true),
          icon: const Icon(Icons.restore_rounded),
          label: const Text('Restore'),
        ),
      ],
    ),
  );
  if (ok != true) return;
  try {
    final data = Map<String, dynamic>.from(dataRaw);
    if (table == 'employee_licenses' && data['license_records'] is List) {
      final records = (data['license_records'] as List)
          .whereType<Map>()
          .map((r) => archiveRestoreData(Map<String, dynamic>.from(r)))
          .toList();
      if (records.isNotEmpty) await db.from(table).insert(records);
    } else if (table == 'employee_certificates' &&
        data['certificate_records'] is List) {
      final records = (data['certificate_records'] as List)
          .whereType<Map>()
          .map((r) => archiveRestoreData(Map<String, dynamic>.from(r)))
          .toList();
      if (records.isNotEmpty) await db.from(table).insert(records);
    } else {
      await db.from(table).insert(archiveRestoreData(data));
    }
    await db.from('archived_records').update({
      'is_restored': true,
      'restored_at': DateTime.now().toIso8601String(),
    }).eq('id', row['id']);
    refresh();
    if (context.mounted) showSnack(context, 'Archived record restored.');
  } catch (e) {
    if (context.mounted) showSnack(context, 'Restore failed: $e');
  }
}

Widget? restoreArchivedRecordAction(
    BuildContext context, Map<String, dynamic> row, VoidCallback refresh) {
  if (row['is_restored'] == true) return null;
  return IconButton(
    tooltip: 'Restore',
    onPressed: () => restoreArchivedRecord(context, row, refresh),
    icon: const Icon(Icons.restore_rounded, color: Color(0xFF16A34A), size: 19),
  );
}

Future<void> viewArchivedRecord(
    BuildContext context, Map<String, dynamic> row) async {
  final data = row['record_data'] is Map
      ? Map<String, dynamic>.from(row['record_data'] as Map)
      : <String, dynamic>{};
  final cleanEntries = data.entries
      .where((entry) =>
          entry.value != null &&
          entry.value.toString().trim().isNotEmpty &&
          entry.key != 'employees' &&
          entry.key != 'ranking_cycles')
      .toList();
  await showDialog<void>(
    context: context,
    builder: (_) => AlertDialog(
      title: Text(
          '${formatValue(row['module_name'])} - ${formatValue(row['employee_name'])}'),
      content: SizedBox(
        width: 850,
        child: SingleChildScrollView(
          child:
              Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
            detailSection('Archive Information', row, const {
              'Module': 'module_name',
              'Table': 'table_name',
              'Type': 'archive_type',
              'Archived At': 'archived_at_display',
              'Status': 'restore_status',
            }),
            const SizedBox(height: 8),
            const Text('Stored Record Data',
                style: TextStyle(
                    fontSize: 16, fontWeight: FontWeight.w900, color: _ink)),
            const SizedBox(height: 8),
            Wrap(spacing: 10, runSpacing: 10, children: [
              for (final entry in cleanEntries)
                DetailTile(titleCase(entry.key),
                    formatDetailValue(entry.value, entry.key)),
            ]),
          ]),
        ),
      ),
      actions: [
        TextButton(
            onPressed: () => Navigator.pop(context), child: const Text('Close'))
      ],
    ),
  );
}

Future<void> showActionAlert(BuildContext context, String title, String message,
    {IconData icon = Icons.check_circle_rounded,
    Color iconColor = const Color(0xFF16A34A)}) async {
  if (!context.mounted) return;
  await showDialog<void>(
    context: context,
    builder: (_) => AlertDialog(
      title: Row(children: [
        Icon(icon, color: iconColor),
        const SizedBox(width: 10),
        Expanded(child: Text(title)),
      ]),
      content: Text(message),
      actions: [
        FilledButton(
          onPressed: () => Navigator.pop(context),
          child: const Text('OK'),
        ),
      ],
    ),
  );
}

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  if (publicClientKey.isNotEmpty) {
    await Supabase.initialize(url: projectUrl, anonKey: publicClientKey);
  }
  runApp(const HrApp());
}

class HrApp extends StatelessWidget {
  const HrApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'HR Monitoring',
      theme: ThemeData(
        useMaterial3: true,
        scaffoldBackgroundColor: _bg,
        colorScheme: ColorScheme.fromSeed(seedColor: _primary),
        fontFamily: 'Arial',
        visualDensity: VisualDensity.standard,
        cardTheme: CardThemeData(
          elevation: 0,
          color: _surface,
          surfaceTintColor: Colors.transparent,
          margin: EdgeInsets.zero,
          shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(24),
              side: const BorderSide(color: _line)),
        ),
        filledButtonTheme: FilledButtonThemeData(
          style: FilledButton.styleFrom(
            backgroundColor: _accent,
            foregroundColor: Colors.white,
            padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 17),
            minimumSize: const Size(44, 44),
            shape:
                RoundedRectangleBorder(borderRadius: BorderRadius.circular(18)),
          ),
        ),
        outlinedButtonTheme: OutlinedButtonThemeData(
          style: OutlinedButton.styleFrom(
            foregroundColor: _accent,
            side: const BorderSide(color: Color(0xFFCBD5E1)),
            padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 16),
            minimumSize: const Size(44, 44),
            shape:
                RoundedRectangleBorder(borderRadius: BorderRadius.circular(18)),
          ),
        ),
        dialogTheme: DialogThemeData(
          backgroundColor: _surface,
          surfaceTintColor: Colors.transparent,
          shape:
              RoundedRectangleBorder(borderRadius: BorderRadius.circular(28)),
        ),
        inputDecorationTheme: InputDecorationTheme(
          filled: true,
          fillColor: _surface,
          hintStyle: const TextStyle(color: _muted),
          labelStyle: const TextStyle(
              color: Color(0xFF1E40AF), fontWeight: FontWeight.w600),
          contentPadding:
              const EdgeInsets.symmetric(horizontal: 16, vertical: 15),
          border: OutlineInputBorder(
              borderRadius: BorderRadius.circular(18),
              borderSide: const BorderSide(color: _line)),
          enabledBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(18),
              borderSide: const BorderSide(color: _line)),
          focusedBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(18),
              borderSide: const BorderSide(color: _primary, width: 1.6)),
        ),
      ),
      home: publicClientKey.isEmpty ? const SetupPage() : const AuthGate(),
    );
  }
}

class AuthGate extends StatefulWidget {
  const AuthGate({super.key});

  @override
  State<AuthGate> createState() => _AuthGateState();
}

class _AuthGateState extends State<AuthGate> {
  Session? session;
  StreamSubscription<AuthState>? authSub;

  @override
  void initState() {
    super.initState();
    session = db.auth.currentSession;
    authSub = db.auth.onAuthStateChange.listen((data) {
      if (!mounted) return;
      setState(() => session = data.session);
    });
  }

  @override
  void dispose() {
    authSub?.cancel();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final current = session;
    if (current == null) return const LoginPage();
    if (current.user.appMetadata['must_change_password'] == true) {
      return const ForcePasswordChangePage();
    }
    return const ShellPage();
  }
}

class LoginPage extends StatefulWidget {
  const LoginPage({super.key});

  @override
  State<LoginPage> createState() => _LoginPageState();
}

class _LoginPageState extends State<LoginPage> {
  final usernameController = TextEditingController();
  final passwordController = TextEditingController();
  bool loading = false;
  bool obscurePassword = true;

  @override
  void dispose() {
    usernameController.dispose();
    passwordController.dispose();
    super.dispose();
  }

  Future<void> login() async {
    final username = usernameController.text.trim().toLowerCase();
    final password = passwordController.text;
    const accounts = <String, String>{
      'admin': 'admin@hr-monitoring.local',
      'humres': 'hr@hr-monitoring.local',
      'increp': 'ir@hr-monitoring.local',
    };
    final email = accounts[username];
    if (username.isEmpty || password.isEmpty) {
      showSnack(context, 'Please enter username and password.');
      return;
    }
    if (email == null) {
      showSnack(context, 'Login failed. Please check your credentials.');
      return;
    }
    setState(() => loading = true);
    try {
      final result =
          await db.auth.signInWithPassword(email: email, password: password);
      if (result.session == null && mounted)
        showSnack(context, 'Login failed. Please check your credentials.');
    } catch (e) {
      if (mounted)
        showSnack(context, 'Login failed. Please check your credentials.');
    } finally {
      if (mounted) setState(() => loading = false);
    }
  }

  @override
  Widget build(BuildContext context) => Scaffold(
        body: Center(
          child: SizedBox(
            width: 680,
            child: Card(
              child: Padding(
                padding: const EdgeInsets.all(32),
                child: Column(
                    mainAxisSize: MainAxisSize.min,
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      Row(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            Container(
                              width: 52,
                              height: 52,
                              decoration: BoxDecoration(
                                gradient: const LinearGradient(
                                    colors: [_primary, Color(0xFF4F46E5)]),
                                borderRadius: BorderRadius.circular(18),
                                boxShadow: const [
                                  BoxShadow(
                                      color: Color(0x332563EB),
                                      blurRadius: 18,
                                      offset: Offset(0, 8))
                                ],
                              ),
                              child: const Icon(Icons.school_rounded,
                                  color: Colors.white),
                            ),
                          ]),
                      const SizedBox(height: 18),
                      const Text('HR Monitoring',
                          textAlign: TextAlign.center,
                          style: TextStyle(
                              fontSize: 28,
                              fontWeight: FontWeight.w900,
                              color: _ink)),
                      const SizedBox(height: 6),
                      const Text('Sign in to continue',
                          textAlign: TextAlign.center,
                          style: TextStyle(
                              color: _muted, fontWeight: FontWeight.w600)),
                      const SizedBox(height: 28),
                      TextField(
                        controller: usernameController,
                        autocorrect: false,
                        enableSuggestions: false,
                        autofillHints: const [AutofillHints.username],
                        decoration: const InputDecoration(
                            labelText: 'Username',
                            prefixIcon: Icon(Icons.person_outline_rounded)),
                        onSubmitted: (_) => login(),
                      ),
                      const SizedBox(height: 14),
                      TextField(
                        controller: passwordController,
                        obscureText: obscurePassword,
                        decoration: InputDecoration(
                          labelText: 'Password',
                          prefixIcon: const Icon(Icons.lock_outline_rounded),
                          suffixIcon: IconButton(
                            onPressed: () => setState(
                                () => obscurePassword = !obscurePassword),
                            icon: Icon(obscurePassword
                                ? Icons.visibility_rounded
                                : Icons.visibility_off_rounded),
                          ),
                        ),
                        onSubmitted: (_) => login(),
                      ),
                      const SizedBox(height: 22),
                      FilledButton.icon(
                        onPressed: loading ? null : login,
                        icon: loading
                            ? const SizedBox(
                                width: 18,
                                height: 18,
                                child:
                                    CircularProgressIndicator(strokeWidth: 2))
                            : const Icon(Icons.login_rounded),
                        label: Text(loading ? 'Signing in...' : 'Login'),
                      ),
                    ]),
              ),
            ),
          ),
        ),
      );
}

class ForcePasswordChangePage extends StatefulWidget {
  const ForcePasswordChangePage({super.key});

  @override
  State<ForcePasswordChangePage> createState() =>
      _ForcePasswordChangePageState();
}

class _ForcePasswordChangePageState extends State<ForcePasswordChangePage> {
  final newPasswordController = TextEditingController();
  final confirmPasswordController = TextEditingController();
  bool loading = false;
  bool obscureNewPassword = true;
  bool obscureConfirmPassword = true;

  @override
  void dispose() {
    newPasswordController.dispose();
    confirmPasswordController.dispose();
    super.dispose();
  }

  Future<void> changePassword() async {
    final newPassword = newPasswordController.text;
    final confirmation = confirmPasswordController.text;
    if (newPassword.length < 10) {
      showSnack(context, 'Use at least 10 characters for your new password.');
      return;
    }
    if (newPassword != confirmation) {
      showSnack(context, 'The passwords do not match.');
      return;
    }

    setState(() => loading = true);
    try {
      await db.auth.updateUser(UserAttributes(password: newPassword));
      await db.auth.refreshSession();
      if (mounted) {
        showSnack(context, 'Password changed successfully.');
        setState(() {});
      }
    } catch (_) {
      if (mounted)
        showSnack(context, 'Password change failed. Please try again.');
    } finally {
      if (mounted) setState(() => loading = false);
    }
  }

  @override
  Widget build(BuildContext context) => Scaffold(
        body: Center(
          child: SizedBox(
            width: 520,
            child: Card(
              child: Padding(
                padding: const EdgeInsets.all(32),
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    const Icon(Icons.password_rounded,
                        size: 48, color: _primary),
                    const SizedBox(height: 16),
                    const Text(
                      'Change Your Password',
                      textAlign: TextAlign.center,
                      style: TextStyle(
                          fontSize: 24,
                          fontWeight: FontWeight.w900,
                          color: _ink),
                    ),
                    const SizedBox(height: 8),
                    const Text(
                      'For security, create a new password before continuing.',
                      textAlign: TextAlign.center,
                      style: TextStyle(color: _muted),
                    ),
                    const SizedBox(height: 24),
                    TextField(
                      controller: newPasswordController,
                      obscureText: obscureNewPassword,
                      enabled: !loading,
                      decoration: InputDecoration(
                        labelText: 'New Password',
                        prefixIcon: const Icon(Icons.lock_outline_rounded),
                        suffixIcon: IconButton(
                          onPressed: loading
                              ? null
                              : () => setState(() => obscureNewPassword =
                                  !obscureNewPassword),
                          icon: Icon(obscureNewPassword
                              ? Icons.visibility_rounded
                              : Icons.visibility_off_rounded),
                        ),
                      ),
                    ),
                    const SizedBox(height: 14),
                    TextField(
                      controller: confirmPasswordController,
                      obscureText: obscureConfirmPassword,
                      enabled: !loading,
                      onSubmitted: (_) => changePassword(),
                      decoration: InputDecoration(
                        labelText: 'Confirm New Password',
                        prefixIcon: const Icon(Icons.lock_reset_rounded),
                        suffixIcon: IconButton(
                          onPressed: loading
                              ? null
                              : () => setState(() => obscureConfirmPassword =
                                  !obscureConfirmPassword),
                          icon: Icon(obscureConfirmPassword
                              ? Icons.visibility_rounded
                              : Icons.visibility_off_rounded),
                        ),
                      ),
                    ),
                    const SizedBox(height: 22),
                    FilledButton.icon(
                      onPressed: loading ? null : changePassword,
                      icon: loading
                          ? const SizedBox(
                              width: 18,
                              height: 18,
                              child:
                                  CircularProgressIndicator(strokeWidth: 2))
                          : const Icon(Icons.check_circle_outline_rounded),
                      label:
                          Text(loading ? 'Changing...' : 'Change Password'),
                    ),
                    const SizedBox(height: 8),
                    TextButton(
                      onPressed: loading ? null : () => db.auth.signOut(),
                      child: const Text('Sign Out'),
                    ),
                  ],
                ),
              ),
            ),
          ),
        ),
      );
}

class SetupPage extends StatelessWidget {
  const SetupPage({super.key});

  @override
  Widget build(BuildContext context) => const Scaffold(
        body: Center(
          child: SizedBox(
              width: 720,
              child: Card(
                  child: Padding(
                      padding: EdgeInsets.all(28),
                      child: Text(
                          'Start the app with your Supabase public client key using --dart-define.')))),
        ),
      );
}

class ShellPage extends StatefulWidget {
  const ShellPage({super.key});

  @override
  State<ShellPage> createState() => _ShellPageState();
}

class _ShellPageState extends State<ShellPage> {
  int index = 0;
  final Set<int> visitedPages = {0};

  void selectPage(int nextIndex) {
    setState(() {
      index = nextIndex;
      visitedPages.add(nextIndex);
    });
  }

  @override
  Widget build(BuildContext context) {
    final pages = currentUserIsIncidentOnly
        ? <Widget>[IncidentReportPage()]
        : <Widget>[
            DashboardPage(onNavigate: selectPage),
            const EmployeesPage(),
            const ContractsPage(),
            const CredentialsPage(),
            const EvaluationsPage(),
            const AppointmentPage(),
            const RankingPage(),
            if (currentUserCanSeeIncidentReport) IncidentReportPage(),
            const ReportsPage(),
            const ResignedEmployeesPage(),
            const ArchivedPage(),
          ];
    final safeIndex = index.clamp(0, pages.length - 1).toInt();
    visitedPages.add(safeIndex);
    return Scaffold(
      body: Row(children: [
        AppSidebar(selectedIndex: safeIndex, onChanged: selectPage),
        const SizedBox.shrink(),
        Expanded(
          child: IndexedStack(
            index: safeIndex,
            children: [
              for (var i = 0; i < pages.length; i++)
                visitedPages.contains(i) ? pages[i] : const SizedBox.shrink(),
            ],
          ),
        ),
      ]),
    );
  }
}

class NavItem {
  final String label;
  final IconData icon;
  const NavItem(this.label, this.icon);
}

String currentUserAccessRole() {
  final user = db.auth.currentUser;
  final userMetadata = user?.userMetadata ?? const <String, dynamic>{};
  final appMetadata = user?.appMetadata ?? const <String, dynamic>{};

  final roleCandidates = <Object?>[
    appMetadata['role'],
    appMetadata['access_role'],
    appMetadata['user_role'],
    appMetadata['account_type'],
    userMetadata['role'],
    userMetadata['access_role'],
    userMetadata['user_role'],
    userMetadata['account_type'],
  ];

  final normalizedRoles = roleCandidates
      .where((value) => value != null)
      .map((value) => value
          .toString()
          .trim()
          .toLowerCase()
          .replaceAll(RegExp(r'[^a-z0-9]+'), '_'))
      .where((value) => value.isNotEmpty)
      .toList();

  final isAdminFlag =
      appMetadata['is_admin'] == true || userMetadata['is_admin'] == true;
  if (isAdminFlag ||
      normalizedRoles.any((role) =>
          role == 'admin' ||
          role == 'administrator' ||
          role.contains('system_admin'))) {
    return 'admin';
  }

  if (normalizedRoles.any((role) =>
      role == 'ir' ||
      role.contains('incident_report') ||
      role.contains('incident_only'))) {
    return 'ir';
  }

  if (normalizedRoles.any((role) => role.contains('hr'))) return 'hr';

  final email = '${user?.email ?? ''}'.trim().toLowerCase();
  if (email.contains('admin')) return 'admin';
  if (email.contains('incident') || email.contains('ir.')) return 'ir';

  // Existing full-system accounts were created before role metadata was
  // standardized. Keep them in the normal HR workspace instead of hiding
  // modules because a metadata key is absent.
  return 'hr';
}

bool get currentUserIsAdmin => currentUserAccessRole() == 'admin';
bool get currentUserIsIncidentOnly => currentUserAccessRole() == 'ir';
bool get currentUserCanSeeIncidentReport =>
    currentUserIsAdmin ||
    currentUserIsIncidentOnly ||
    currentUserAccessRole() == 'hr';

Future<void> logoutUser(BuildContext context) async {
  final ok = await showDialog<bool>(
    context: context,
    builder: (_) => AlertDialog(
      title: const Text('Log out?'),
      content: const Text('You will need to log in again to continue.'),
      actions: [
        TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: const Text('Cancel')),
        FilledButton.icon(
          onPressed: () => Navigator.pop(context, true),
          icon: const Icon(Icons.logout_rounded),
          label: const Text('Logout'),
        ),
      ],
    ),
  );

  if (ok != true) return;

  try {
    await db.auth.signOut();
  } catch (_) {}

  try {
    html.window.sessionStorage.clear();
  } catch (_) {}

  try {
    html.window.localStorage.remove('supabase.auth.token');
  } catch (_) {}
}

class AppSidebar extends StatelessWidget {
  final int selectedIndex;
  final ValueChanged<int> onChanged;

  const AppSidebar(
      {super.key, required this.selectedIndex, required this.onChanged});

  @override
  Widget build(BuildContext context) {
    final items = currentUserIsIncidentOnly
        ? const [
            NavItem('Incident Report', Icons.report_problem_rounded),
          ]
        : <NavItem>[
            const NavItem('Dashboard', Icons.dashboard_rounded),
            const NavItem('Employees', Icons.groups_rounded),
            const NavItem('Contracts', Icons.assignment_rounded),
            const NavItem('Credentials', Icons.badge_rounded),
            const NavItem('Evaluations', Icons.rate_review_rounded),
            const NavItem('Appointment', Icons.work_outline_rounded),
            const NavItem('Ranking', Icons.leaderboard_rounded),
            if (currentUserCanSeeIncidentReport)
              const NavItem('Incident Report', Icons.report_problem_rounded),
            const NavItem('Reports', Icons.summarize_rounded),
            const NavItem('Resigned Employees', Icons.person_off_rounded),
            const NavItem('Archived', Icons.archive_rounded),
          ];

    return Container(
      width: 252,
      decoration: const BoxDecoration(
        color: _surface,
        border: Border(right: BorderSide(color: _line)),
      ),
      padding: const EdgeInsets.fromLTRB(18, 18, 18, 14),
      child: SafeArea(
        child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Row(children: [
            Container(
              width: 42,
              height: 42,
              decoration: BoxDecoration(
                gradient:
                    const LinearGradient(colors: [_primary, Color(0xFF4F46E5)]),
                borderRadius: BorderRadius.circular(18),
                boxShadow: const [
                  BoxShadow(
                      color: Color(0x332563EB),
                      blurRadius: 18,
                      offset: Offset(0, 8))
                ],
              ),
              child: const Icon(Icons.school_rounded, color: Colors.white),
            ),
            const SizedBox(width: 12),
            const Expanded(
                child: Text('HR Monitoring',
                    style: TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.w900,
                        color: _ink))),
          ]),
          const SizedBox(height: 6),
          const Text('Faculty and staff records',
              style: TextStyle(
                  fontSize: 12, color: _muted, fontWeight: FontWeight.w500)),
          const SizedBox(height: 24),
          Expanded(
            child: ListView.builder(
              padding: EdgeInsets.zero,
              itemCount: items.length,
              itemBuilder: (context, i) => SidebarItem(
                label: items[i].label,
                icon: items[i].icon,
                selected: selectedIndex == i,
                onTap: () => onChanged(i),
              ),
            ),
          ),
          const SizedBox(height: 10),
          SizedBox(
            width: double.infinity,
            child: FilledButton.icon(
              onPressed: () => logoutUser(context),
              icon: const Icon(Icons.logout_rounded, size: 18),
              label: const Text('Logout'),
            ),
          ),
        ]),
      ),
    );
  }
}

class SidebarItem extends StatelessWidget {
  final String label;
  final IconData icon;
  final bool selected;
  final VoidCallback onTap;

  const SidebarItem(
      {super.key,
      required this.label,
      required this.icon,
      required this.selected,
      required this.onTap});

  @override
  Widget build(BuildContext context) => Padding(
        padding: const EdgeInsets.only(bottom: 8),
        child: InkWell(
          borderRadius: BorderRadius.circular(18),
          onTap: onTap,
          child: AnimatedContainer(
            duration: const Duration(milliseconds: 180),
            padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
            decoration: BoxDecoration(
              color: selected ? _primarySoft : Colors.transparent,
              borderRadius: BorderRadius.circular(18),
              border: Border.all(
                  color:
                      selected ? const Color(0xFFBFDBFE) : Colors.transparent),
            ),
            child: Row(children: [
              Icon(icon,
                  color: selected ? _primary : const Color(0xFF64748B),
                  size: 22),
              const SizedBox(width: 12),
              Text(label,
                  style: TextStyle(
                      fontWeight: selected ? FontWeight.w900 : FontWeight.w700,
                      color: selected ? _primary : _ink)),
            ]),
          ),
        ),
      );
}

class PageFrame extends StatelessWidget {
  final String title;
  final String subtitle;
  final Widget child;

  const PageFrame(
      {super.key,
      required this.title,
      required this.subtitle,
      required this.child});

  @override
  Widget build(BuildContext context) => Padding(
        padding: const EdgeInsets.fromLTRB(32, 24, 32, 24),
        child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Text(title,
              style: const TextStyle(
                  fontSize: 30,
                  height: 1.08,
                  fontWeight: FontWeight.w900,
                  color: _ink,
                  letterSpacing: -0.7)),
          const SizedBox(height: 5),
          Text(subtitle,
              style: const TextStyle(
                  color: Color(0xFF52637A),
                  fontSize: 14,
                  fontWeight: FontWeight.w500)),
          const SizedBox(height: 20),
          Expanded(child: child),
        ]),
      );
}

Future<List<dynamic>> loadEmployees({int limit = 1500}) => db
    .from('employees')
    .select(
        'id, name_key, employee_code, full_name, bio_number, gender, education_level, date_hired, starting_date, date_resigned, employment_status, designation, employee_type, civil_status, teaching_status, current_salary, license_summary, birth_date, address, contact_number, email, guardian_name, guardian_relationship, guardian_contact, guardian_address, school_graduated, degree_course, notes')
    .order('full_name')
    .limit(limit);
Future<List<dynamic>> loadContracts({int limit = 1500}) => db
    .from('employee_contracts')
    .select(
        'id, employee_id, contract_type, contract_start_date, duration_months, contract_end_date, status, attachment_url, employees(full_name)')
    .order('contract_end_date', ascending: true)
    .limit(limit);

Future<List<dynamic>> loadResignedEmployees({int limit = 5000}) async {
  final employees = await loadEmployees(limit: limit);
  final employeeRows = employees
      .map((item) => normalizeRow(Map<String, dynamic>.from(item as Map)))
      .toList();

  final resignedIds = <String>{};
  try {
    final contracts = await loadContracts(limit: limit);
    for (final item in contracts) {
      final row = normalizeRow(Map<String, dynamic>.from(item as Map));
      final status = formatValue(row['status']).toLowerCase();
      if (status.contains('resign')) resignedIds.add('${row['employee_id']}');
    }
  } catch (_) {}

  return employeeRows.where((row) {
    final status = formatValue(row['employment_status']).toLowerCase();
    return status.contains('resign') || resignedIds.contains('${row['id']}');
  }).toList()
    ..sort((a, b) =>
        formatValue(a['full_name']).compareTo(formatValue(b['full_name'])));
}

Future<List<dynamic>> loadLicenses({int limit = 1500}) => db
    .from('employee_licenses')
    .select(
        'id, employee_id, license_name, license_number, issued_date, expiry_date, status, attachment_url, employees(full_name)')
    .order('expiry_date')
    .limit(limit);

String credentialListValue(Object? value) {
  final text = formatValue(value)
      .replaceAll('ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬Ãƒâ€šÃ‚Â¢', '')
      .replaceAll('\u2022', '')
      .replaceAll('ÃƒÂ¢Ã¢â€šÂ¬Ã‚Â¢', '')
      .trim();
  return text.isEmpty || text == '-' ? '-' : text;
}

String credentialBulletList(List<Map<String, dynamic>> rows, String key) =>
    rows.map((row) => '\u2022 ${credentialListValue(row[key])}').join('\n');

Future<List<dynamic>> loadLicensesGrouped({int limit = 5000}) async {
  final rows = await loadLicenses(limit: limit);
  final groups = <String, List<Map<String, dynamic>>>{};
  for (final item in rows) {
    final row = normalizeRow(Map<String, dynamic>.from(item as Map));
    final key = '${row['employee_id'] ?? row['employee_name'] ?? ''}';
    groups.putIfAbsent(key, () => <Map<String, dynamic>>[]).add(row);
  }
  final out = <Map<String, dynamic>>[];
  for (final entry in groups.entries) {
    final list = entry.value;
    if (list.isEmpty) continue;
    final first = list.first;
    String bullets(String key) => credentialBulletList(list, key);
    out.add({
      'id': first['id'],
      'employee_id': first['employee_id'],
      'employee_name': first['employee_name'],
      'license_ids': list.map((r) => r['id']).toList(),
      'license_records': list,
      'license_name': bullets('license_name'),
      'license_number': bullets('license_number'),
      'expiry_date': bullets('expiry_date'),
      'status': bullets('status'),
    });
  }
  out.sort((a, b) => formatValue(a['employee_name'])
      .compareTo(formatValue(b['employee_name'])));
  return out;
}

Future<List<dynamic>> loadCertificates({int limit = 1500}) => db
    .from('employee_certificates')
    .select(
        'id, employee_id, certificate_type, certificate_name, certificate_number, issued_date, expiry_date, status, attachment_url, employees(full_name)')
    .order('expiry_date')
    .limit(limit);

Future<List<dynamic>> loadCertificatesGrouped({int limit = 5000}) async {
  final rows = await loadCertificates(limit: limit);
  final groups = <String, List<Map<String, dynamic>>>{};
  for (final item in rows) {
    final row = normalizeRow(Map<String, dynamic>.from(item as Map));
    final key = '${row['employee_id'] ?? row['employee_name'] ?? ''}';
    groups.putIfAbsent(key, () => <Map<String, dynamic>>[]).add(row);
  }
  final out = <Map<String, dynamic>>[];
  for (final entry in groups.entries) {
    final list = entry.value;
    if (list.isEmpty) continue;
    final first = list.first;
    String bullets(String key) => credentialBulletList(list, key);
    out.add({
      'id': first['id'],
      'employee_id': first['employee_id'],
      'employee_name': first['employee_name'],
      'certificate_ids': list.map((r) => r['id']).toList(),
      'certificate_records': list,
      'certificate_name': bullets('certificate_name'),
      'certificate_type': bullets('certificate_type'),
      'certificate_number': bullets('certificate_number'),
      'expiry_date': bullets('expiry_date'),
      'status': bullets('status'),
    });
  }
  out.sort((a, b) => formatValue(a['employee_name'])
      .compareTo(formatValue(b['employee_name'])));
  return out;
}

Future<List<dynamic>> loadSafetyOfficers({int limit = 1500}) => db
    .from('employee_safety_officers')
    .select(
        'id, employee_id, safety_officer_name, certificate_number, issued_date, expiry_date, status, attachment_url, employees(full_name)')
    .order('expiry_date')
    .limit(limit);

Future<List<dynamic>> loadSafetyOfficersGrouped({int limit = 5000}) async {
  final rows = await loadSafetyOfficers(limit: limit);
  final groups = <String, List<Map<String, dynamic>>>{};
  for (final item in rows) {
    final row = normalizeRow(Map<String, dynamic>.from(item as Map));
    final key = '${row['employee_id'] ?? row['employee_name'] ?? ''}';
    groups.putIfAbsent(key, () => <Map<String, dynamic>>[]).add(row);
  }
  final out = <Map<String, dynamic>>[];
  for (final entry in groups.entries) {
    final list = entry.value;
    if (list.isEmpty) continue;
    final first = list.first;
    String bullets(String key) => credentialBulletList(list, key);
    out.add({
      'id': first['id'],
      'employee_id': first['employee_id'],
      'employee_name': first['employee_name'],
      'safety_officer_ids': list.map((r) => r['id']).toList(),
      'safety_officer_records': list,
      'safety_officer_name': bullets('safety_officer_name'),
      'certificate_number': bullets('certificate_number'),
      'expiry_date': bullets('expiry_date'),
      'status': bullets('status'),
    });
  }
  out.sort((a, b) => formatValue(a['employee_name'])
      .compareTo(formatValue(b['employee_name'])));
  return out;
}

Future<List<dynamic>> loadEvaluations({int limit = 1500}) async {
  final rows = await db
      .from('evaluation_records')
      .select(
          'id, employee_id, academic_year, semester, superior_rating, superior_description, peer_rating, peer_description, self_rating, self_description, student_rating, student_description, total_rating, total_description, employees(full_name)')
      .order('academic_year')
      .limit(limit);

  final contractByEmployee = <String, Map<String, dynamic>>{};
  try {
    final contracts = await db
        .from('employee_contracts')
        .select('employee_id, contract_type, contract_start_date, id')
        .order('contract_start_date', ascending: false)
        .limit(5000);
    for (final item in contracts) {
      final contract = Map<String, dynamic>.from(item as Map);
      final employeeId = '${contract['employee_id'] ?? ''}'.trim();
      if (employeeId.isEmpty || contractByEmployee.containsKey(employeeId))
        continue;
      contractByEmployee[employeeId] = contract;
    }
  } catch (_) {}

  return rows.map((item) {
    final row = Map<String, dynamic>.from(item as Map);
    if (row['employees'] is Map) {
      row['employee_name'] =
          formatValue((row['employees'] as Map)['full_name']).toUpperCase();
    }
    final employeeId = '${row['employee_id'] ?? ''}'.trim();
    final contract = contractByEmployee[employeeId];
    if (contract != null) {
      row['contract_type'] = contract['contract_type'];
      row['latest_contract_type'] = contract['contract_type'];
    }
    return row;
  }).toList();
}

Future<Set<String>> loadLatestPartTimeEmployeeIds() async {
  final ids = <String>{};
  try {
    final contracts = await db
        .from('employee_contracts')
        .select('employee_id, contract_type, contract_start_date, id')
        .order('contract_start_date', ascending: false)
        .limit(5000);
    final seen = <String>{};
    for (final item in contracts) {
      final contract = Map<String, dynamic>.from(item as Map);
      final employeeId = '${contract['employee_id'] ?? ''}'.trim();
      if (employeeId.isEmpty || !seen.add(employeeId)) continue;
      if (isPartTimeContractType(contract['contract_type']))
        ids.add(employeeId);
    }
  } catch (_) {}
  return ids;
}

bool isPartTimeContractType(Object? value) {
  final text = formatValue(value)
      .toLowerCase()
      .replaceAll('_', '-')
      .replaceAll(RegExp(r'\s+'), '-');
  return text.contains('part-time') || text.contains('parttime');
}

bool isPartTimeEvaluationRow(Map<String, dynamic> row) {
  return isPartTimeContractType(row['contract_type']) ||
      isPartTimeContractType(row['latest_contract_type']) ||
      isPartTimeContractType(row['employee_type']);
}

Future<List<dynamic>> loadRankings({int limit = 1500}) => db
    .from('ranking_applications')
    .select(
        'id, employee_id, cycle_id, appointment, previous_rank_text, previous_salary, applied_rank_text, applied_salary, points_earned, approved_rank_text, approved_salary, approved_date, effective_date, employees(full_name), ranking_cycles(name)')
    .order('points_earned', ascending: false)
    .limit(limit);

bool isResignedText(Object? value) {
  final text = '${value ?? ''}'.toLowerCase();
  return text.contains('resign');
}

bool rowHasResignedStatus(Map<String, dynamic> row) {
  return isResignedText(row['employment_status']) ||
      isResignedText(row['employee_status']) ||
      isResignedText(row['status']) ||
      isResignedText(row['latest_status']) ||
      isResignedText(row['contract_status']);
}

Future<Set<String>> loadResignedEmployeeIdSet() async {
  final ids = <String>{};

  try {
    final employees = await db
        .from('employees')
        .select('id, employment_status, employee_status, status, latest_status')
        .limit(5000);
    for (final item in employees) {
      final row = Map<String, dynamic>.from(item as Map);
      if (rowHasResignedStatus(row)) ids.add('${row['id']}');
    }
  } catch (_) {}

  try {
    final contracts = await db
        .from('employee_contracts')
        .select('employee_id, status')
        .limit(5000);
    for (final item in contracts) {
      final row = Map<String, dynamic>.from(item as Map);
      if (isResignedText(row['status'])) ids.add('${row['employee_id']}');
    }
  } catch (_) {}

  ids.removeWhere((value) => value.trim().isEmpty || value == 'null');
  return ids;
}

String rowEmployeeId(Map<String, dynamic> row) {
  final raw = row['employee_id'] ?? row['id'];
  return '${raw ?? ''}'.trim();
}

Future<List<dynamic>> activeOnlyRows(Future<List<dynamic>> source) async {
  final rows = await source;
  final resignedIds = await loadResignedEmployeeIdSet();
  return rows.where((item) {
    final row = normalizeRow(Map<String, dynamic>.from(item as Map));
    final id = rowEmployeeId(row);
    if (id.isNotEmpty && resignedIds.contains(id)) return false;
    if (rowHasResignedStatus(row)) return false;
    if (!isOfficialActiveEmployeeRow(row)) return false;
    return true;
  }).toList();
}

Future<List<dynamic>> loadActiveEmployees({int limit = 5000}) =>
    activeOnlyRows(loadEmployees(limit: limit));

Future<List<dynamic>> loadAppointments({int limit = 5000}) => db
    .from('employee_appointments')
    .select(
        'id, employee_id, category, appointment_title, appointment_type, other_duties, attachment_url, employees(full_name)')
    .order('category')
    .limit(limit);

class DashboardData {
  final int activeEmployees;
  final int activeFaculty;
  final int resignedEmployees;
  final int totalFemale;
  final int totalMale;
  final int contractsTotal;
  final int contractsOngoing;
  final int contractsForRenewal;
  final int expiredContracts;
  final int licensesTotal;
  final int licensesDue;
  final int certificatesTotal;
  final int certificatesDue;
  final int evaluationsTotal;
  final int appointmentsTotal;
  final int rankingsTotal;

  const DashboardData({
    required this.activeEmployees,
    required this.activeFaculty,
    required this.resignedEmployees,
    required this.totalFemale,
    required this.totalMale,
    required this.contractsTotal,
    required this.contractsOngoing,
    required this.contractsForRenewal,
    required this.expiredContracts,
    required this.licensesTotal,
    required this.licensesDue,
    required this.certificatesTotal,
    required this.certificatesDue,
    required this.evaluationsTotal,
    required this.appointmentsTotal,
    required this.rankingsTotal,
  });

  int get totalGender => totalFemale + totalMale;
  int get credentialsTotal => licensesTotal + certificatesTotal;
}

Map<String, dynamic> dashboardRow(dynamic item) =>
    normalizeRow(Map<String, dynamic>.from(item as Map));

String dashboardStatus(dynamic item) =>
    formatValue(dashboardRow(item)['status']).trim().toLowerCase();

bool dashboardStatusContains(dynamic item, List<String> terms) {
  final status = dashboardStatus(item);
  return terms.any(status.contains);
}

Future<DashboardData> loadDashboardData() async {
  final results = await Future.wait<List<dynamic>>([
    loadActiveEmployees(limit: 5000),
    loadResignedEmployees(limit: 5000),
    activeOnlyRows(loadContracts(limit: 5000)),
    activeOnlyRows(loadLicenses(limit: 5000)),
    activeOnlyRows(loadCertificates(limit: 5000)),
    activeOnlyRows(loadEvaluations(limit: 5000)),
    activeOnlyRows(loadAppointments(limit: 5000)),
    activeOnlyRows(loadRankings(limit: 5000)),
  ]);

  final employees = results[0];
  final resignedEmployees = results[1];
  final contracts = results[2];
  final licenses = results[3];
  final certificates = results[4];
  final evaluations = results[5];
  final appointments = results[6];
  final rankings = results[7];

  var female = 0;
  var male = 0;
  var faculty = 0;

  for (final item in employees) {
    final row = dashboardRow(item);
    final gender = formatValue(row['gender']).trim().toLowerCase();
    if (gender == 'female' || gender == 'f') female++;
    if (gender == 'male' || gender == 'm') male++;

    final roleText = [
      row['designation'],
      row['employee_type'],
      row['teaching_status'],
      row['education_level'],
    ].map(formatValue).join(' ').toLowerCase();
    if (roleText.contains('faculty') ||
        roleText.contains('teacher') ||
        roleText.contains('teaching')) {
      faculty++;
    }
  }

  final contractsForRenewal = contracts
      .where((item) => dashboardStatusContains(item, ['renew']))
      .length;
  final expiredContracts = contracts
      .where((item) => dashboardStatusContains(item, ['expired']))
      .length;
  final contractsOngoing = contracts
      .where((item) =>
          dashboardStatusContains(item, ['ongoing', 'on-going', 'active']))
      .length;
  final licensesDue = licenses
      .where((item) => dashboardStatusContains(item, ['renew', 'expired']))
      .length;
  final certificatesDue = certificates
      .where((item) => dashboardStatusContains(item, ['renew', 'expired']))
      .length;

  return DashboardData(
    activeEmployees: employees.length,
    activeFaculty: faculty,
    resignedEmployees: resignedEmployees.length,
    totalFemale: female,
    totalMale: male,
    contractsTotal: contracts.length,
    contractsOngoing: contractsOngoing,
    contractsForRenewal: contractsForRenewal,
    expiredContracts: expiredContracts,
    licensesTotal: licenses.length,
    licensesDue: licensesDue,
    certificatesTotal: certificates.length,
    certificatesDue: certificatesDue,
    evaluationsTotal: evaluations.length,
    appointmentsTotal: appointments.length,
    rankingsTotal: rankings.length,
  );
}

class DashboardPage extends StatelessWidget {
  final ValueChanged<int> onNavigate;
  const DashboardPage({super.key, required this.onNavigate});

  @override
  Widget build(BuildContext context) => PageFrame(
        title: 'Dashboard',
        subtitle:
            'Live summary based on the current data shown in each module. Click a card to open its module.',
        child: FutureBuilder<DashboardData>(
          future: loadDashboardData(),
          builder: (_, snap) {
            if (snap.connectionState != ConnectionState.done) {
              return const Center(child: CircularProgressIndicator());
            }
            if (snap.hasError) return ErrorBox('${snap.error}');
            final data = snap.data ??
                const DashboardData(
                  activeEmployees: 0,
                  activeFaculty: 0,
                  resignedEmployees: 0,
                  totalFemale: 0,
                  totalMale: 0,
                  contractsTotal: 0,
                  contractsOngoing: 0,
                  contractsForRenewal: 0,
                  expiredContracts: 0,
                  licensesTotal: 0,
                  licensesDue: 0,
                  certificatesTotal: 0,
                  certificatesDue: 0,
                  evaluationsTotal: 0,
                  appointmentsTotal: 0,
                  rankingsTotal: 0,
                );

            final moduleCards = <Metric>[
              Metric(
                  'Employees',
                  data.activeEmployees,
                  Icons.people_alt_rounded,
                  const Color(0xFFEFF6FF),
                  const Color(0xFF1D4ED8),
                  targetIndex: 1),
              Metric('Contracts', data.contractsTotal, Icons.assignment_rounded,
                  const Color(0xFFFFFBEB), const Color(0xFFB45309),
                  targetIndex: 2),
              Metric('Credentials', data.credentialsTotal, Icons.badge_rounded,
                  const Color(0xFFF5F3FF), const Color(0xFF6D28D9),
                  targetIndex: 3),
              Metric(
                  'Evaluations',
                  data.evaluationsTotal,
                  Icons.rate_review_rounded,
                  const Color(0xFFECFEFF),
                  const Color(0xFF0E7490),
                  targetIndex: 4),
              Metric(
                  'Appointments',
                  data.appointmentsTotal,
                  Icons.work_outline_rounded,
                  const Color(0xFFF0FDF4),
                  const Color(0xFF15803D),
                  targetIndex: 5),
              Metric('Ranking', data.rankingsTotal, Icons.leaderboard_rounded,
                  const Color(0xFFF8FAFC), _ink,
                  targetIndex: 6),
              Metric('Reports', data.totalGender, Icons.summarize_rounded,
                  const Color(0xFFFFF7ED), const Color(0xFFC2410C),
                  targetIndex: 8),
              Metric(
                  'Resigned Employees',
                  data.resignedEmployees,
                  Icons.person_off_rounded,
                  const Color(0xFFFEF2F2),
                  const Color(0xFFB91C1C),
                  targetIndex: 9),
            ];

            final attentionCards = <Metric>[
              Metric(
                  'Ongoing Contracts',
                  data.contractsOngoing,
                  Icons.verified_rounded,
                  const Color(0xFFF0FDF4),
                  const Color(0xFF15803D),
                  targetIndex: 2),
              Metric(
                  'For Renewal',
                  data.contractsForRenewal,
                  Icons.schedule_rounded,
                  const Color(0xFFFFFBEB),
                  const Color(0xFFB45309),
                  targetIndex: 2),
              Metric(
                  'Expired Contracts',
                  data.expiredContracts,
                  Icons.warning_amber_rounded,
                  const Color(0xFFFEF2F2),
                  const Color(0xFFB91C1C),
                  targetIndex: 2),
              Metric('Licenses Due', data.licensesDue, Icons.badge_rounded,
                  const Color(0xFFF5F3FF), const Color(0xFF6D28D9),
                  targetIndex: 3),
              Metric(
                  'Certificates Due',
                  data.certificatesDue,
                  Icons.workspace_premium_rounded,
                  const Color(0xFFECFEFF),
                  const Color(0xFF0E7490),
                  targetIndex: 3),
            ];

            final reportCards = <Metric>[
              Metric('Total Female', data.totalFemale, Icons.female_rounded,
                  const Color(0xFFFDF2F8), const Color(0xFFDB2777),
                  targetIndex: 8),
              Metric('Total Male', data.totalMale, Icons.male_rounded,
                  const Color(0xFFEFF6FF), const Color(0xFF2563EB),
                  targetIndex: 8),
              Metric('Total Gender', data.totalGender, Icons.wc_rounded,
                  const Color(0xFFF8FAFC), _ink,
                  targetIndex: 8),
              Metric('Active Faculty', data.activeFaculty, Icons.school_rounded,
                  const Color(0xFFF0FDF4), const Color(0xFF15803D),
                  targetIndex: 1),
              Metric('License Summary', data.licensesTotal, Icons.badge_rounded,
                  const Color(0xFFFFF7ED), const Color(0xFFC2410C),
                  targetIndex: 8),
              Metric(
                  'NC/TM Summary',
                  data.certificatesTotal,
                  Icons.workspace_premium_rounded,
                  const Color(0xFFECFEFF),
                  const Color(0xFF0E7490),
                  targetIndex: 8),
            ];

            return RefreshIndicator(
              onRefresh: () async {
                _crudTableDataCache.clear();
                await loadDashboardData();
              },
              child: SingleChildScrollView(
                physics: const AlwaysScrollableScrollPhysics(),
                child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text('Per Module Data',
                          style: TextStyle(
                              fontWeight: FontWeight.w900,
                              color: _ink,
                              fontSize: 16)),
                      const SizedBox(height: 14),
                      Wrap(
                          spacing: 24,
                          runSpacing: 24,
                          children: moduleCards
                              .map((m) => MetricCard(m, onNavigate: onNavigate))
                              .toList()),
                      const SizedBox(height: 30),
                      const Text('Needs Attention',
                          style: TextStyle(
                              fontWeight: FontWeight.w900,
                              color: _ink,
                              fontSize: 16)),
                      const SizedBox(height: 14),
                      Wrap(
                          spacing: 24,
                          runSpacing: 24,
                          children: attentionCards
                              .map((m) => MetricCard(m, onNavigate: onNavigate))
                              .toList()),
                      const SizedBox(height: 30),
                      const Text('Report Totals',
                          style: TextStyle(
                              fontWeight: FontWeight.w900,
                              color: _ink,
                              fontSize: 16)),
                      const SizedBox(height: 14),
                      Wrap(
                          spacing: 24,
                          runSpacing: 24,
                          children: reportCards
                              .map((m) => MetricCard(m, onNavigate: onNavigate))
                              .toList()),
                      const SizedBox(height: 30),
                      Wrap(spacing: 20, runSpacing: 14, children: [
                        QuickCard('Manage Employees', Icons.people_alt_rounded,
                            () => onNavigate(1)),
                        QuickCard('Manage Contracts', Icons.assignment_rounded,
                            () => onNavigate(2)),
                        QuickCard('Manage Credentials', Icons.badge_rounded,
                            () => onNavigate(3)),
                        QuickCard('Open Reports', Icons.summarize_rounded,
                            () => onNavigate(8)),
                      ]),
                    ]),
              ),
            );
          },
        ),
      );
}

class Metric {
  final String title;
  final Object? value;
  final IconData icon;
  final Color bg;
  final Color fg;
  final int? targetIndex;
  const Metric(this.title, this.value, this.icon, this.bg, this.fg,
      {this.targetIndex});
}

class MetricCard extends StatelessWidget {
  final Metric metric;
  final ValueChanged<int>? onNavigate;
  const MetricCard(this.metric, {super.key, this.onNavigate});

  @override
  Widget build(BuildContext context) {
    final content = Padding(
      padding: const EdgeInsets.all(18),
      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        Row(children: [
          Container(
              width: 42,
              height: 42,
              decoration: BoxDecoration(
                  color: metric.bg, borderRadius: BorderRadius.circular(14)),
              child: Icon(metric.icon, color: metric.fg)),
          const Spacer(),
          Text('${metric.value ?? 0}',
              style: const TextStyle(
                  fontSize: 34,
                  fontWeight: FontWeight.w900,
                  color: _ink,
                  letterSpacing: -0.7)),
        ]),
        const Spacer(),
        Row(children: [
          Expanded(
              child: Text(metric.title,
                  style: const TextStyle(
                      fontWeight: FontWeight.w900, color: _ink))),
          if (metric.targetIndex != null)
            const Icon(Icons.chevron_right_rounded, color: Color(0xFF64748B)),
        ]),
      ]),
    );

    return SizedBox(
      width: 248,
      height: 128,
      child: Card(
        child: metric.targetIndex == null || onNavigate == null
            ? content
            : InkWell(
                borderRadius: BorderRadius.circular(22),
                onTap: () => onNavigate!(metric.targetIndex!),
                child: content,
              ),
      ),
    );
  }
}

class QuickCard extends StatelessWidget {
  final String title;
  final IconData icon;
  final VoidCallback onTap;
  const QuickCard(this.title, this.icon, this.onTap, {super.key});

  @override
  Widget build(BuildContext context) => SizedBox(
        width: 245,
        child: Card(
          child: InkWell(
            borderRadius: BorderRadius.circular(22),
            onTap: onTap,
            child: Padding(
              padding: const EdgeInsets.all(18),
              child: Row(children: [
                Icon(icon, color: _primary),
                const SizedBox(width: 12),
                Expanded(
                    child: Text(title,
                        style: const TextStyle(
                            fontWeight: FontWeight.w900, color: _ink))),
                const Icon(Icons.chevron_right_rounded, color: _muted),
              ]),
            ),
          ),
        ),
      );
}

class EmployeesPage extends StatefulWidget {
  const EmployeesPage({super.key});

  @override
  State<EmployeesPage> createState() => _EmployeesPageState();
}

class _EmployeesPageState extends State<EmployeesPage> {
  int refreshToken = 0;
  String genderFilter = 'All';

  void refreshEmployees() => setState(() => refreshToken++);

  String _genderKey(Object? value) {
    final gender = '${value ?? ''}'.trim().toLowerCase();
    if (gender == 'male' || gender == 'm') return 'Male';
    if (gender == 'female' || gender == 'f') return 'Female';
    return 'Unspecified';
  }

  bool _matchesGenderFilter(Map<String, dynamic> row) =>
      genderFilter == 'All' || _genderKey(row['gender']) == genderFilter;

  Future<List<dynamic>> _loadEmployees() async {
    final rows = await loadActiveEmployees(limit: 5000);
    if (genderFilter == 'All') return rows;
    return rows
        .where((item) => _matchesGenderFilter(
            normalizeRow(Map<String, dynamic>.from(item as Map))))
        .toList();
  }

  String _employeeReportTitle() => genderFilter == 'All'
      ? 'Employee Report'
      : 'Employee Report - $genderFilter';

  bool isResignedEmployeeRow(Map<String, dynamic> row) {
    final values = [
      row['employment_status'],
      row['employee_status'],
      row['status'],
      row['latest_status'],
      row['contract_status'],
    ];
    return values
        .any((value) => formatValue(value).toLowerCase().contains('resign'));
  }

  @override
  Widget build(BuildContext context) => PageFrame(
        title: 'Employees',
        subtitle:
            'Add full employee information, contract, credentials, and view complete records.',
        child: Column(children: [
          Card(
            child: Padding(
              padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
              child: Row(children: [
                const Text('Filter:',
                    style: TextStyle(fontWeight: FontWeight.w900, color: _ink)),
                const SizedBox(width: 10),
                SizedBox(
                  width: 260,
                  child: DropdownButtonFormField<String>(
                    value: genderFilter,
                    isExpanded: true,
                    decoration: const InputDecoration(labelText: 'Gender'),
                    items: const [
                      DropdownMenuItem(
                          value: 'All', child: Text('All Genders')),
                      DropdownMenuItem(value: 'Male', child: Text('Male')),
                      DropdownMenuItem(value: 'Female', child: Text('Female')),
                      DropdownMenuItem(
                          value: 'Unspecified',
                          child: Text('Unspecified / Other')),
                    ],
                    onChanged: (value) =>
                        setState(() => genderFilter = value ?? 'All'),
                  ),
                ),
                const SizedBox(width: 12),
                const Expanded(
                  child: Text(
                      'The table and Print button will follow the selected gender filter.',
                      style: TextStyle(
                          color: _muted, fontWeight: FontWeight.w600)),
                ),
              ]),
            ),
          ),
          const SizedBox(height: 8),
          Expanded(
            child: CrudTable(
              pageSizeOptions: const [1, 10, 100],
              initialPageSize: 10,
              key: ValueKey('employees-$refreshToken-$genderFilter'),
              load: () => _loadEmployees(),
              searchHint:
                  'Search employee, bio number, gender, education, status, or date hired',
              addLabel: 'Add Employee',
              reportTitle: _employeeReportTitle(),
              archiveTableName: 'employees',
              archiveModuleName: 'Employees',
              columns: const [
                GridCol('full_name', 'Employee Name', flex: 3, primary: true),
                GridCol('bio_number', 'Bio Number'),
                GridCol('gender', 'Gender'),
                GridCol('education_level', 'Educational Attainment', flex: 2),
                GridCol('date_hired_display', 'Date Hired'),
                GridCol('employment_status', 'Status', isStatus: true),
              ],
              onAdd: (ctx, refresh) => addEmployeeFull(ctx, refresh),
              onView: viewEmployee,
              onEdit: editEmployee,
              extraAction: employeeResignRowAction,
              onDelete: (row) =>
                  db.from('employees').delete().eq('id', row['id']),
            ),
          ),
        ]),
      );
}

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
    if (lower.contains('ongoing') || lower.contains('on-going'))
      return 'On-going';
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
    return _statusKey(row['status']).toLowerCase() ==
        statusFilter.toLowerCase();
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
              padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
              child: Row(children: [
                const Text('Filter:',
                    style: TextStyle(fontWeight: FontWeight.w900, color: _ink)),
                const SizedBox(width: 10),
                SizedBox(
                  width: 280,
                  child: DropdownButtonFormField<String>(
                    value: contractTypeFilter,
                    isExpanded: true,
                    decoration:
                        const InputDecoration(labelText: 'Contract Type'),
                    items: const [
                      DropdownMenuItem(
                          value: 'All', child: Text('All Contract Types')),
                      DropdownMenuItem(
                          value: 'Full-time', child: Text('Full-time')),
                      DropdownMenuItem(
                          value: 'Full-time-Probationary',
                          child: Text('Full-time-Probationary')),
                      DropdownMenuItem(
                          value: 'Part-time', child: Text('Part-time')),
                      DropdownMenuItem(
                          value: 'Probationary', child: Text('Probationary')),
                      DropdownMenuItem(
                          value: 'Compliance', child: Text('Compliance')),
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
                      DropdownMenuItem(
                          value: 'All', child: Text('All Statuses')),
                      DropdownMenuItem(
                          value: 'On-going', child: Text('On-going')),
                      DropdownMenuItem(
                          value: 'For Renewal', child: Text('For Renewal')),
                      DropdownMenuItem(
                          value: 'Expired', child: Text('Expired')),
                      DropdownMenuItem(
                          value: 'Resigned', child: Text('Resigned')),
                      DropdownMenuItem(
                          value: 'Unspecified', child: Text('Unspecified')),
                    ],
                    onChanged: (value) =>
                        setState(() => statusFilter = value ?? 'All'),
                  ),
                ),
                const SizedBox(width: 12),
                const Expanded(
                  child: Text(
                    'The table and Print button will follow the selected contract type and status filters.',
                    style:
                        TextStyle(color: _muted, fontWeight: FontWeight.w600),
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
              archiveTableName: 'employee_contracts',
              archiveModuleName: 'Contracts',
              columns: const [
                GridCol('employee_name', 'Employee Name',
                    flex: 3, primary: true),
                GridCol('contract_type', 'Contract Type', flex: 2),
                GridCol('status', 'Status', isStatus: true),
                GridCol('contract_start_date', 'Start'),
                GridCol('duration_months', 'Months', isNumber: true),
                GridCol('contract_end_date', 'End'),
                GridCol('days_left', 'Days Left', isNumber: true),
              ],
              onAdd: (ctx, refresh) => editContract(ctx, null, refresh),
              onView: viewContract,
              onEdit: editContract,
              onDelete: (row) =>
                  db.from('employee_contracts').delete().eq('id', row['id']),
            ),
          ),
        ]),
      );
}

class CredentialsPage extends StatelessWidget {
  const CredentialsPage({super.key});

  @override
  Widget build(BuildContext context) => PageFrame(
        title: 'Credentials',
        subtitle:
            'Manage licenses, national certificates, and safety officer credentials linked to employees.',
        child: const DefaultTabController(
          length: 3,
          child: Column(children: [
            Align(
                alignment: Alignment.centerLeft,
                child: SizedBox(
                    width: 430,
                    child: TabBar(tabs: [
                      Tab(text: 'Licenses'),
                      Tab(text: 'National Certificates'),
                      Tab(text: 'Safety Officer')
                    ]))),
            SizedBox(height: 16),
            Expanded(
                child: TabBarView(children: [
              LicensesTab(),
              CertificatesTab(),
              SafetyOfficersTab()
            ])),
          ]),
        ),
      );
}

class LicensesTab extends StatelessWidget {
  const LicensesTab({super.key});

  @override
  Widget build(BuildContext context) => CrudTable(
        load: () => activeOnlyRows(loadLicensesGrouped()),
        searchHint: 'Search employee, license name, number, or status',
        addLabel: 'Add License',
        archiveTableName: 'employee_licenses',
        archiveModuleName: 'Credentials - Licenses',
        columns: const [
          GridCol('employee_name', 'Employee Name', flex: 3, primary: true),
          GridCol('license_name', 'License', flex: 2),
          GridCol('license_number', 'License No.', flex: 2),
          GridCol('expiry_date', 'Expiry'),
          GridCol('status', 'Status', isStatus: true),
        ],
        onAdd: (ctx, refresh) => editLicense(ctx, null, refresh),
        onView: viewLicenseGroup,
        onEdit: editLicense,
        onDelete: (row) async {
          final ids = row['license_ids'];
          if (ids is List && ids.isNotEmpty) {
            for (final id in ids) {
              await db.from('employee_licenses').delete().eq('id', id);
            }
          } else {
            await db.from('employee_licenses').delete().eq('id', row['id']);
          }
        },
      );
}

class CertificatesTab extends StatelessWidget {
  const CertificatesTab({super.key});

  @override
  Widget build(BuildContext context) => CrudTable(
        load: () => activeOnlyRows(loadCertificatesGrouped()),
        searchHint: 'Search employee, certificate, number, or status',
        addLabel: 'Add Certificate',
        archiveTableName: 'employee_certificates',
        archiveModuleName: 'Credentials - Certificates',
        columns: const [
          GridCol('employee_name', 'Employee Name', flex: 3, primary: true),
          GridCol('certificate_name', 'Certificate', flex: 3),
          GridCol('certificate_type', 'Type', flex: 2),
          GridCol('certificate_number', 'Certificate No.', flex: 2),
          GridCol('expiry_date', 'Expiry'),
          GridCol('status', 'Status', isStatus: true),
        ],
        onAdd: (ctx, refresh) => editCertificate(ctx, null, refresh),
        onView: viewCertificateGroup,
        onEdit: editCertificate,
        onDelete: (row) async {
          final ids = row['certificate_ids'];
          if (ids is List && ids.isNotEmpty) {
            for (final id in ids) {
              await db.from('employee_certificates').delete().eq('id', id);
            }
          } else {
            await db.from('employee_certificates').delete().eq('id', row['id']);
          }
        },
      );
}

class SafetyOfficersTab extends StatelessWidget {
  const SafetyOfficersTab({super.key});

  @override
  Widget build(BuildContext context) => CrudTable(
        load: () => activeOnlyRows(loadSafetyOfficersGrouped()),
        searchHint:
            'Search employee, safety officer, certificate number, or status',
        addLabel: 'Add Safety Officer',
        archiveTableName: 'employee_safety_officers',
        archiveModuleName: 'Credentials - Safety Officer',
        columns: const [
          GridCol('employee_name', 'Employee Name', flex: 3, primary: true),
          GridCol('safety_officer_name', 'Safety Officer', flex: 3),
          GridCol('certificate_number', 'Certificate No.', flex: 2),
          GridCol('expiry_date', 'Expiry'),
          GridCol('status', 'Status', isStatus: true),
        ],
        onAdd: (ctx, refresh) => editSafetyOfficer(ctx, null, refresh),
        onView: viewSafetyOfficerGroup,
        onEdit: editSafetyOfficer,
        onDelete: (row) async {
          final ids = row['safety_officer_ids'];
          if (ids is List && ids.isNotEmpty) {
            for (final id in ids) {
              await db.from('employee_safety_officers').delete().eq('id', id);
            }
          } else {
            await db
                .from('employee_safety_officers')
                .delete()
                .eq('id', row['id']);
          }
        },
      );
}

class EvaluationsPage extends StatefulWidget {
  const EvaluationsPage({super.key});

  @override
  State<EvaluationsPage> createState() => _EvaluationsPageState();
}

class _EvaluationsPageState extends State<EvaluationsPage> {
  int refreshSeed = 0;

  void refreshEvaluations() => setState(() => refreshSeed++);

  @override
  Widget build(BuildContext context) => PageFrame(
        title: 'Evaluations',
        subtitle: 'Manage faculty evaluation records by evaluation type.',
        child: DefaultTabController(
          length: 5,
          child: Column(children: [
            Card(
              child: Padding(
                padding:
                    const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
                child: Row(children: [
                  const Expanded(
                    child: Text(
                      'Use one Add Evaluation form to encode Superior, Peer-to-Peer, Self, and Student ratings together.',
                      style:
                          TextStyle(color: _muted, fontWeight: FontWeight.w700),
                    ),
                  ),
                  FilledButton.icon(
                    onPressed: () =>
                        editFullEvaluation(context, null, refreshEvaluations),
                    icon: const Icon(Icons.add_rounded),
                    label: const Text('Add Evaluation'),
                  ),
                ]),
              ),
            ),
            const SizedBox(height: 12),
            const Align(
              alignment: Alignment.centerLeft,
              child: SizedBox(
                width: 820,
                child: TabBar(
                  isScrollable: true,
                  tabs: [
                    Tab(text: 'Superior'),
                    Tab(text: 'Peer-to-Peer'),
                    Tab(text: 'Self'),
                    Tab(text: 'Student'),
                    Tab(text: 'Overall'),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 16),
            Expanded(
              child: TabBarView(children: [
                EvaluationTab(
                  key: ValueKey('superior-$refreshSeed'),
                  title: 'Superior Evaluation',
                  ratingKey: 'superior_rating',
                  descriptionKey: 'superior_description',
                  kind: EvaluationKind.superior,
                ),
                EvaluationTab(
                  key: ValueKey('peer-$refreshSeed'),
                  title: 'Peer-to-Peer Evaluation',
                  ratingKey: 'peer_rating',
                  descriptionKey: 'peer_description',
                  kind: EvaluationKind.peer,
                ),
                EvaluationTab(
                  key: ValueKey('self-$refreshSeed'),
                  title: 'Self Evaluation',
                  ratingKey: 'self_rating',
                  descriptionKey: 'self_description',
                  kind: EvaluationKind.self,
                ),
                EvaluationTab(
                  key: ValueKey('student-$refreshSeed'),
                  title: 'Student Evaluation',
                  ratingKey: 'student_rating',
                  descriptionKey: 'student_description',
                  kind: EvaluationKind.student,
                ),
                OverallEvaluationTab(key: ValueKey('overall-$refreshSeed')),
              ]),
            ),
          ]),
        ),
      );
}

enum EvaluationKind { superior, peer, self, student }

class EvaluationTab extends StatelessWidget {
  final String title;
  final String ratingKey;
  final String descriptionKey;
  final EvaluationKind kind;

  const EvaluationTab({
    super.key,
    required this.title,
    required this.ratingKey,
    required this.descriptionKey,
    required this.kind,
  });

  Future<List<dynamic>> _loadRows() async {
    final rows = await activeOnlyRows(loadEvaluations(limit: 5000));
    final normalized = rows.map((item) {
      final row = normalizeRow(Map<String, dynamic>.from(item as Map));
      row['evaluation_rating'] = row[ratingKey];
      row['evaluation_description'] =
          evaluationDescription(row, kind, ratingKey, descriptionKey);
      return row;
    }).where((row) {
      if ((kind == EvaluationKind.superior || kind == EvaluationKind.peer) &&
          isPartTimeEvaluationRow(row)) {
        return false;
      }
      return true;
    }).toList();

    normalized.sort((a, b) => formatValue(a['employee_name'])
        .compareTo(formatValue(b['employee_name'])));

    final seen = <String>{};
    final unique = <Map<String, dynamic>>[];
    for (final row in normalized) {
      final key = '${row['employee_id'] ?? row['employee_name'] ?? ''}'
          .trim()
          .toLowerCase();
      if (key.isEmpty || !seen.add(key)) continue;
      unique.add(row);
    }
    return unique;
  }

  @override
  Widget build(BuildContext context) => CrudTable(
        load: () => _loadRows(),
        searchHint: 'Search employee, rating, or description',
        addLabel: 'Add Evaluation',
        allowAdd: false,
        reportTitle: '$title Report',
        archiveTableName: 'evaluation_records',
        archiveModuleName: 'Evaluations',
        columns: const [
          GridCol('employee_name', 'Employee Name', flex: 3, primary: true),
          GridCol('evaluation_rating', 'Rating', isNumber: true),
          GridCol('evaluation_description', 'Description', flex: 2),
        ],
        onView: (ctx, row) => viewEvaluationForKind(ctx, row, kind),
        onEdit: (ctx, row, refresh) =>
            editEvaluationForKind(ctx, row, refresh, kind),
        onDelete: (row) =>
            db.from('evaluation_records').delete().eq('id', row['id']),
      );
}

class OverallEvaluationTab extends StatelessWidget {
  const OverallEvaluationTab({super.key});

  Future<List<dynamic>> _loadRows() async {
    final rows = await activeOnlyRows(loadEvaluations(limit: 5000));
    final normalized = rows.map((item) {
      final row = normalizeRow(Map<String, dynamic>.from(item as Map));
      final recomputed = recomputeEvaluationTotals(row);
      row['total_rating'] = recomputed['total_rating'];
      row['total_description'] = recomputed['total_description'];
      return row;
    }).toList();
    normalized.sort((a, b) => formatValue(a['employee_name'])
        .compareTo(formatValue(b['employee_name'])));
    return normalized;
  }

  @override
  Widget build(BuildContext context) => CrudTable(
        load: () => _loadRows(),
        searchHint: 'Search employee, total rating, or overall description',
        addLabel: 'Add Evaluation',
        allowAdd: false,
        reportTitle: 'Overall Evaluation Report',
        columns: const [
          GridCol('employee_name', 'Employee Name', flex: 3, primary: true),
          GridCol('superior_rating', 'Superior', isNumber: true),
          GridCol('peer_rating', 'Peer', isNumber: true),
          GridCol('self_rating', 'Self', isNumber: true),
          GridCol('student_rating', 'Student', isNumber: true),
          GridCol('total_rating', 'Total', isNumber: true),
          GridCol('total_description', 'Overall Description', flex: 2),
        ],
        onView: viewEvaluation,
        showDelete: false,
        onDelete: (row) async {},
      );
}

String evaluationDescription(Map<String, dynamic> row, EvaluationKind kind,
    String ratingKey, String descriptionKey) {
  final saved = formatValueRaw(row[descriptionKey]).trim();
  if (saved.isNotEmpty && saved != '-') return saved.toUpperCase();
  return evaluationScoreDescription(kind, row[ratingKey]).toUpperCase();
}

String evaluationKindTitle(EvaluationKind kind) => switch (kind) {
      EvaluationKind.superior => 'Superior Evaluation',
      EvaluationKind.peer => 'Peer-to-Peer Evaluation',
      EvaluationKind.self => 'Self Evaluation',
      EvaluationKind.student => 'Student Evaluation',
    };

String evaluationRatingKeyForKind(EvaluationKind kind) => switch (kind) {
      EvaluationKind.superior => 'superior_rating',
      EvaluationKind.peer => 'peer_rating',
      EvaluationKind.self => 'self_rating',
      EvaluationKind.student => 'student_rating',
    };

String evaluationDescriptionKeyForKind(EvaluationKind kind) => switch (kind) {
      EvaluationKind.superior => 'superior_description',
      EvaluationKind.peer => 'peer_description',
      EvaluationKind.self => 'self_description',
      EvaluationKind.student => 'student_description',
    };

double evaluationMaxScore(EvaluationKind kind) => switch (kind) {
      EvaluationKind.superior => 100,
      EvaluationKind.peer => 100,
      EvaluationKind.self => 5,
      EvaluationKind.student => 5,
    };

double? evaluationScoreAsDouble(Object? value) {
  final text = formatValue(value).replaceAll(',', '').trim();
  if (text.isEmpty || text == '-') return null;
  return double.tryParse(text);
}

String evaluationScoreDescription(EvaluationKind kind, Object? value) {
  final score = evaluationScoreAsDouble(value);
  if (score == null) return '';
  switch (kind) {
    case EvaluationKind.superior:
    case EvaluationKind.peer:
      if (score >= 85) return 'EXCEEDS EXPECTATION';
      if (score >= 75) return 'MEETS EXPECTATION';
      return 'UNACCEPTABLE';
    case EvaluationKind.self:
      if (score >= 4.50) return 'OUTSTANDING';
      if (score >= 4.00) return 'VERY SATISFACTORY';
      if (score >= 3.00) return 'SATISFACTORY';
      return 'UNSATISFACTORY';
    case EvaluationKind.student:
      if (score >= 4.25) return 'EXCELLENT';
      if (score >= 3.75) return 'GOOD';
      if (score >= 3.00) return 'SATISFACTORY';
      return 'NEEDS IMPROVEMENT';
  }
}

String overallEvaluationDescription(Object? value) {
  final score = evaluationScoreAsDouble(value);
  if (score == null) return '';
  if (score >= 85) return 'EXCEEDS EXPECTATION';
  if (score >= 75) return 'MEETS EXPECTATION';
  return 'UNACCEPTABLE';
}

String evaluationScoreDisplay(Object? value) {
  final score = evaluationScoreAsDouble(value);
  if (score == null) return '-';
  final fixed = score.toStringAsFixed(2);
  return fixed
      .replaceFirst(RegExp(r'\.00$'), '')
      .replaceFirst(RegExp(r'0$'), '');
}

Map<String, dynamic> recomputeEvaluationTotals(Map<String, dynamic> row) {
  final data = Map<String, dynamic>.from(row);
  final isPartTime = isPartTimeEvaluationRow(data);
  if (isPartTime) {
    data['superior_rating'] = null;
    data['superior_description'] = null;
    data['peer_rating'] = null;
    data['peer_description'] = null;
  }
  final parts = <double>[];
  void addPart(String key, double max) {
    final score = evaluationScoreAsDouble(data[key]);
    if (score != null) parts.add((score / max) * 100);
  }

  if (!isPartTime) {
    addPart('superior_rating', 100);
    addPart('peer_rating', 100);
  }
  addPart('self_rating', 5);
  addPart('student_rating', 5);

  if (parts.isNotEmpty) {
    final total = parts.reduce((a, b) => a + b) / parts.length;
    data['total_rating'] = double.parse(total.toStringAsFixed(2));
    data['total_description'] = overallEvaluationDescription(total);
  }
  return data;
}

Widget evaluationRatingBox(
    EvaluationKind kind,
    TextEditingController rating,
    TextEditingController description,
    VoidCallback recompute,
    StateSetter setDialogState,
    {VoidCallback? onDateSubmit}) {
  final maxScore = evaluationMaxScore(kind);
  return Wrap(spacing: 14, runSpacing: 14, children: [
    SizedBox(
      width: 354,
      child: TextFormField(
        controller: rating,
        keyboardType: const TextInputType.numberWithOptions(decimal: true),
        decoration: InputDecoration(
          labelText:
              '${evaluationKindTitle(kind)} Rating (out of ${maxScore.toStringAsFixed(0)})',
          helperText: 'Maximum score: ${maxScore.toStringAsFixed(0)}',
        ),
        validator: (value) {
          final score = double.tryParse('${value ?? ''}'.trim());
          if (score == null) return 'Required';
          if (score < 0 || score > maxScore) {
            return 'Enter 0 to ${maxScore.toStringAsFixed(0)}';
          }
          return null;
        },
        onChanged: (_) => setDialogState(recompute),
      ),
    ),
    SizedBox(
      width: 354,
      child: TextFormField(
        controller: description,
        readOnly: true,
        decoration: const InputDecoration(
          labelText: 'Description',
          suffixIcon: Icon(Icons.auto_fix_high_rounded),
        ),
        validator: (value) => value == null || value.trim().isEmpty
            ? 'Enter a valid rating first'
            : null,
      ),
    ),
  ]);
}

Future<Map<String, dynamic>?> showFullEvaluationDialog(BuildContext context,
    Map<String, dynamic>? row, List<EditOption> employees) async {
  final isAdd = row == null;
  final initial = normalizeRow(row ?? {});
  final formKey = GlobalKey<FormState>();
  String? employeeId = isAdd ? null : initial['employee_id']?.toString();
  final partTimeEmployeeIds = await loadLatestPartTimeEmployeeIds();
  bool selectedEmployeeIsPartTime() =>
      employeeId != null && partTimeEmployeeIds.contains(employeeId);
  final superior =
      TextEditingController(text: formatEditValue(initial['superior_rating']));
  final superiorDesc = TextEditingController(
      text: formatEditValue(initial['superior_description']));
  final peer =
      TextEditingController(text: formatEditValue(initial['peer_rating']));
  final peerDesc =
      TextEditingController(text: formatEditValue(initial['peer_description']));
  final selfRating =
      TextEditingController(text: formatEditValue(initial['self_rating']));
  final selfDesc =
      TextEditingController(text: formatEditValue(initial['self_description']));
  final student =
      TextEditingController(text: formatEditValue(initial['student_rating']));
  final studentDesc = TextEditingController(
      text: formatEditValue(initial['student_description']));
  final total =
      TextEditingController(text: formatEditValue(initial['total_rating']));
  final overall = TextEditingController(
      text: formatEditValue(initial['total_description']));

  void recomputeAll() {
    final isPartTimeEmployee = selectedEmployeeIsPartTime();
    if (isPartTimeEmployee) {
      superior.clear();
      superiorDesc.clear();
      peer.clear();
      peerDesc.clear();
    } else {
      superiorDesc.text =
          evaluationScoreDescription(EvaluationKind.superior, superior.text);
      peerDesc.text =
          evaluationScoreDescription(EvaluationKind.peer, peer.text);
    }
    selfDesc.text =
        evaluationScoreDescription(EvaluationKind.self, selfRating.text);
    studentDesc.text =
        evaluationScoreDescription(EvaluationKind.student, student.text);
    final computed = recomputeEvaluationTotals({
      'contract_type': isPartTimeEmployee ? 'PART-TIME' : '',
      'superior_rating': superior.text,
      'peer_rating': peer.text,
      'self_rating': selfRating.text,
      'student_rating': student.text,
    });
    total.text = evaluationScoreDisplay(computed['total_rating']);
    overall.text = formatValue(computed['total_description']);
  }

  recomputeAll();

  final result = await showDialog<Map<String, dynamic>>(
    context: context,
    builder: (_) => StatefulBuilder(
      builder: (context, setDialogState) => AlertDialog(
        title: Text(isAdd ? 'Add Evaluation' : 'Edit Evaluation'),
        content: SizedBox(
          width: 790,
          child: Form(
            key: formKey,
            child: SingleChildScrollView(
              child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const DialogSectionTitle('Employee Information'),
                    if (isAdd)
                      employeeAutocompleteField(
                        employees: employees,
                        employeeId: employeeId,
                        width: 728,
                        onEmployeeChanged: (value) => setDialogState(() {
                          employeeId = value;
                          recomputeAll();
                        }),
                      )
                    else
                      ReadOnlyEmployeeBox(linkedEmployeeName(initial)),
                    const SizedBox(height: 16),
                    if (selectedEmployeeIsPartTime())
                      Container(
                        width: 728,
                        padding: const EdgeInsets.all(14),
                        decoration: BoxDecoration(
                          color: Color(0xFFEFF6FF),
                          borderRadius: BorderRadius.circular(14),
                          border: Border.all(color: Color(0xFFBFDBFE)),
                        ),
                        child: const Text(
                          'PART-TIME EMPLOYEES USE SELF AND STUDENT EVALUATIONS ONLY.',
                          style: TextStyle(
                              color: Color(0xFF1E3A8A),
                              fontWeight: FontWeight.w900),
                        ),
                      )
                    else ...[
                      const DialogSectionTitle('Superior Evaluation'),
                      evaluationRatingBox(EvaluationKind.superior, superior,
                          superiorDesc, recomputeAll, setDialogState),
                      const SizedBox(height: 16),
                      const DialogSectionTitle('Peer-to-Peer Evaluation'),
                      evaluationRatingBox(EvaluationKind.peer, peer, peerDesc,
                          recomputeAll, setDialogState),
                      const SizedBox(height: 16),
                    ],
                    const DialogSectionTitle('Self Evaluation'),
                    evaluationRatingBox(EvaluationKind.self, selfRating,
                        selfDesc, recomputeAll, setDialogState),
                    const SizedBox(height: 16),
                    const DialogSectionTitle('Student Evaluation'),
                    evaluationRatingBox(EvaluationKind.student, student,
                        studentDesc, recomputeAll, setDialogState),
                    const SizedBox(height: 16),
                    const DialogSectionTitle('Total / Overall'),
                    Wrap(spacing: 14, runSpacing: 14, children: [
                      SizedBox(
                        width: 354,
                        child: TextFormField(
                          controller: total,
                          readOnly: true,
                          decoration: const InputDecoration(
                              labelText: 'Total Rating (out of 100)'),
                        ),
                      ),
                      SizedBox(
                        width: 354,
                        child: TextFormField(
                          controller: overall,
                          readOnly: true,
                          decoration: const InputDecoration(
                              labelText: 'Overall Description'),
                        ),
                      ),
                    ]),
                  ]),
            ),
          ),
        ),
        actions: [
          TextButton(
              onPressed: () => Navigator.pop(context),
              child: const Text('Cancel')),
          FilledButton(
            onPressed: () {
              recomputeAll();
              if (!formKey.currentState!.validate()) return;
              final isPartTimeEmployee = selectedEmployeeIsPartTime();
              final out = <String, dynamic>{
                if (isAdd) 'employee_id': employeeId,
                'contract_type': isPartTimeEmployee ? 'PART-TIME' : null,
                'superior_rating': isPartTimeEmployee
                    ? null
                    : double.tryParse(superior.text.trim()),
                'superior_description':
                    isPartTimeEmployee ? null : superiorDesc.text.trim(),
                'peer_rating': isPartTimeEmployee
                    ? null
                    : double.tryParse(peer.text.trim()),
                'peer_description':
                    isPartTimeEmployee ? null : peerDesc.text.trim(),
                'self_rating': double.tryParse(selfRating.text.trim()),
                'self_description': selfDesc.text.trim(),
                'student_rating': double.tryParse(student.text.trim()),
                'student_description': studentDesc.text.trim(),
                'total_rating': double.tryParse(total.text.trim()),
                'total_description': overall.text.trim(),
              }..removeWhere((_, value) =>
                  value != null && value.toString().trim().isEmpty);
              Navigator.pop(context, out);
            },
            child: const Text('Save'),
          ),
        ],
      ),
    ),
  );

  for (final controller in [
    superior,
    superiorDesc,
    peer,
    peerDesc,
    selfRating,
    selfDesc,
    student,
    studentDesc,
    total,
    overall,
  ]) {
    controller.dispose();
  }
  return result;
}

Future<Map<String, dynamic>?> showEvaluationKindOnlyDialog(
    BuildContext context, Map<String, dynamic> row, EvaluationKind kind) async {
  final normalized = normalizeRow(row);
  final formKey = GlobalKey<FormState>();
  final ratingKey = evaluationRatingKeyForKind(kind);
  final descriptionKey = evaluationDescriptionKeyForKind(kind);
  final rating =
      TextEditingController(text: formatEditValue(normalized[ratingKey]));
  final description = TextEditingController(
      text: formatEditValue(normalized[descriptionKey]).isEmpty
          ? evaluationScoreDescription(kind, normalized[ratingKey])
          : formatEditValue(normalized[descriptionKey]));

  void recompute() {
    description.text = evaluationScoreDescription(kind, rating.text);
  }

  final result = await showDialog<Map<String, dynamic>>(
    context: context,
    builder: (_) => StatefulBuilder(
      builder: (context, setDialogState) => AlertDialog(
        title: Text('Edit ${evaluationKindTitle(kind)}'),
        content: SizedBox(
          width: 790,
          child: Form(
            key: formKey,
            child: SingleChildScrollView(
              child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const DialogSectionTitle('Employee Information'),
                    ReadOnlyEmployeeBox(linkedEmployeeName(normalized)),
                    const SizedBox(height: 16),
                    DialogSectionTitle(evaluationKindTitle(kind)),
                    evaluationRatingBox(
                        kind, rating, description, recompute, setDialogState),
                  ]),
            ),
          ),
        ),
        actions: [
          TextButton(
              onPressed: () => Navigator.pop(context),
              child: const Text('Cancel')),
          FilledButton(
            onPressed: () {
              recompute();
              if (!formKey.currentState!.validate()) return;
              Navigator.pop(context, <String, dynamic>{
                ratingKey: double.tryParse(rating.text.trim()),
                descriptionKey: description.text.trim(),
              });
            },
            child: const Text('Save'),
          ),
        ],
      ),
    ),
  );
  rating.dispose();
  description.dispose();
  return result;
}

Future<void> viewEvaluationForKind(
    BuildContext context, Map<String, dynamic> row, EvaluationKind kind) async {
  final normalized = normalizeRow(row);
  final ratingKey = evaluationRatingKeyForKind(kind);
  final descriptionKey = evaluationDescriptionKeyForKind(kind);
  await showDialog<void>(
    context: context,
    builder: (_) => AlertDialog(
      title: Text(
          '${evaluationKindTitle(kind)} - ${formatValue(normalized['employee_name'])}'),
      content: SizedBox(
        width: 680,
        child: Wrap(spacing: 10, runSpacing: 10, children: [
          DetailTile('Employee Name', formatValue(normalized['employee_name'])),
          DetailTile('Rating / ${evaluationMaxScore(kind).toStringAsFixed(0)}',
              evaluationScoreDisplay(normalized[ratingKey])),
          DetailTile(
              'Description',
              evaluationDescription(
                  normalized, kind, ratingKey, descriptionKey)),
        ]),
      ),
      actions: [
        TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Close')),
      ],
    ),
  );
}

Future<void> viewEvaluation(
    BuildContext context, Map<String, dynamic> row) async {
  final normalized = normalizeRow(row);
  final computed = recomputeEvaluationTotals(normalized);
  await showDialog<void>(
    context: context,
    builder: (_) => AlertDialog(
      title: Text(
          'Overall Evaluation - ${formatValue(normalized['employee_name'])}'),
      content: SizedBox(
        width: 850,
        child: SingleChildScrollView(
          child:
              Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
            Wrap(spacing: 10, runSpacing: 10, children: [
              DetailTile(
                  'Employee Name', formatValue(normalized['employee_name'])),
              DetailTile('Superior Rating / 100',
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
                      EvaluationKind.peer, normalized['peer_rating'])),
              DetailTile('Self Rating / 5',
                  evaluationScoreDisplay(normalized['self_rating'])),
              DetailTile(
                  'Self Description',
                  evaluationScoreDescription(
                      EvaluationKind.self, normalized['self_rating'])),
              DetailTile('Student Rating / 5',
                  evaluationScoreDisplay(normalized['student_rating'])),
              DetailTile(
                  'Student Description',
                  evaluationScoreDescription(
                      EvaluationKind.student, normalized['student_rating'])),
              DetailTile('Total Rating / 100',
                  evaluationScoreDisplay(computed['total_rating'])),
              DetailTile('Overall Description',
                  formatValue(computed['total_description'])),
            ]),
          ]),
        ),
      ),
      actions: [
        TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Close')),
      ],
    ),
  );
}

Future<void> editEvaluationForKind(BuildContext context,
    Map<String, dynamic> row, VoidCallback refresh, EvaluationKind kind) async {
  if ((kind == EvaluationKind.superior || kind == EvaluationKind.peer) &&
      isPartTimeEvaluationRow(normalizeRow(row))) {
    showSnack(context,
        'PART-TIME EMPLOYEES DO NOT HAVE SUPERIOR OR PEER-TO-PEER EVALUATION.');
    return;
  }
  final data = await showEvaluationKindOnlyDialog(context, row, kind);
  if (data == null) return;

  try {
    final merged = upperCaseDataMap(
        recomputeEvaluationTotals({...normalizeRow(row), ...data}));
    merged.remove('id');
    await db.from('evaluation_records').update(merged).eq('id', row['id']);
    refresh();
    if (context.mounted)
      showSnack(context, '${evaluationKindTitle(kind)} saved.');
  } catch (e) {
    if (context.mounted) showSnack(context, 'Save Evaluation Failed: $e');
  }
}

Future<void> editFullEvaluation(BuildContext context, Map<String, dynamic>? row,
    VoidCallback refresh) async {
  final isAdd = row == null;
  final data = await showFullEvaluationDialog(
      context, row, isAdd ? await employeeOptions() : const <EditOption>[]);
  if (data == null) return;

  try {
    if (isAdd) {
      final employeeId = data['employee_id'];
      final existingRows = await db
          .from('evaluation_records')
          .select()
          .eq('employee_id', employeeId)
          .limit(1);
      if (existingRows is List && existingRows.isNotEmpty) {
        final existing =
            normalizeRow(Map<String, dynamic>.from(existingRows.first as Map));
        final merged =
            upperCaseDataMap(recomputeEvaluationTotals({...existing, ...data}));
        merged.remove('id');
        await db
            .from('evaluation_records')
            .update(merged)
            .eq('id', existing['id']);
      } else {
        await db
            .from('evaluation_records')
            .insert(upperCaseDataMap(recomputeEvaluationTotals(data)));
      }
    } else {
      final merged = upperCaseDataMap(
          recomputeEvaluationTotals({...normalizeRow(row), ...data}));
      merged.remove('id');
      await db.from('evaluation_records').update(merged).eq('id', row['id']);
    }
    refresh();
    if (context.mounted) showSnack(context, 'Evaluation saved.');
  } catch (e) {
    if (context.mounted) showSnack(context, 'Save Evaluation Failed: $e');
  }
}

Future<void> viewSafetyOfficerGroup(
    BuildContext context, Map<String, dynamic> row) async {
  final normalized = normalizeRow(row);
  final records = normalized['safety_officer_records'] is List
      ? normalized['safety_officer_records'] as List<dynamic>
      : <dynamic>[normalized];
  await showDialog<void>(
    context: context,
    builder: (_) => AlertDialog(
      title:
          Text('Safety Officer - ${formatValue(normalized['employee_name'])}'),
      content: SizedBox(
        width: 820,
        child: SingleChildScrollView(
          child:
              Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
            relatedSection('Safety Officer Records', records, const [
              'safety_officer_name',
              'certificate_number',
              'issued_date',
              'expiry_date',
              'status',
              'attachment_url'
            ]),
          ]),
        ),
      ),
      actions: [
        TextButton(
            onPressed: () => Navigator.pop(context), child: const Text('Close'))
      ],
    ),
  );
}

Map<String, dynamic> firstSafetyOfficerRecord(Map<String, dynamic>? row) {
  final normalized = normalizeRow(row ?? {});
  final records = normalized['safety_officer_records'];
  if (records is List && records.isNotEmpty && records.first is Map) {
    return normalizeRow(Map<String, dynamic>.from(records.first as Map));
  }
  return normalized;
}

Future<void> editSafetyOfficer(BuildContext context, Map<String, dynamic>? row,
    VoidCallback refresh) async {
  final isAdd = row == null;
  final source = firstSafetyOfficerRecord(row);
  final fields = <EditField>[
    if (isAdd)
      EditField('employee_id', 'Employee Name',
          kind: FieldKind.dropdown,
          required: true,
          options: await employeeOptions()),
    const EditField('safety_officer_name', 'Safety Officer',
        kind: FieldKind.dropdown,
        required: true,
        options: [
          EditOption('Safety Officer 1', 'Safety Officer 1'),
          EditOption('Safety Officer 2', 'Safety Officer 2'),
          EditOption('Safety Officer 3', 'Safety Officer 3'),
          EditOption('Safety Officer 4', 'Safety Officer 4'),
        ]),
    const EditField('certificate_number', 'Certificate Number', required: true),
    const EditField('issued_date', 'Issued Date', kind: FieldKind.date),
    const EditField('expiry_date', 'Expiry Date',
        kind: FieldKind.date, required: true),
    const EditField('attachment_url', 'Attachment URL'),
    const EditField('status', 'Status', kind: FieldKind.dropdown, options: [
      EditOption('Active', 'Active'),
      EditOption('For Renewal', 'For Renewal'),
      EditOption('Expired', 'Expired'),
    ]),
  ];

  final data = await showRecordDialog(
    context,
    isAdd ? 'Add Safety Officer' : 'Edit Safety Officer',
    fields,
    source,
    readOnlyEmployeeName: isAdd ? null : linkedEmployeeName(source),
  );
  if (data == null) return;
  final computedStatus = certificateStatusFromExpiry(data['expiry_date'] ?? '');
  if ((data['status'] == null || '${data['status']}'.trim().isEmpty) &&
      computedStatus.isNotEmpty) {
    data['status'] = computedStatus;
  }
  await saveRow(context, 'employee_safety_officers',
      isAdd ? null : source['id'], data, refresh);
}

class AppointmentPage extends StatelessWidget {
  const AppointmentPage({super.key});

  @override
  Widget build(BuildContext context) => PageFrame(
        title: 'Appointment',
        subtitle:
            'View employee appointment classifications and assigned appointment/designation from the ranking Excel list.',
        child: CrudTable(
          load: () => activeOnlyRows(loadAppointments()),
          searchHint:
              'Search employee, appointment type, appointment, other duties, type, or PDF',
          addLabel: 'Add Appointment',
          reportTitle: 'Appointment Reference Report',
          archiveTableName: 'employee_appointments',
          archiveModuleName: 'Appointment',
          columns: const [
            GridCol('employee_name', 'Employee Name', flex: 3, primary: true),
            GridCol('category', 'Appointment Type', flex: 2),
            GridCol('appointment_title', 'Appointment', flex: 3),
            GridCol('other_duties', 'Other Duties', flex: 3),
            GridCol('appointment_type', 'Type', flex: 2),
          ],
          onAdd: (ctx, refresh) => editAppointment(ctx, null, refresh),
          onView: viewAppointment,
          onEdit: editAppointment,
          onDelete: (row) =>
              db.from('employee_appointments').delete().eq('id', row['id']),
        ),
      );
}

Future<void> viewAppointment(
    BuildContext context, Map<String, dynamic> row) async {
  final normalized = normalizeRow(row);
  final titleName = formatValue(normalized['employee_name']).trim().isEmpty ||
          formatValue(normalized['employee_name']) == '-'
      ? linkedEmployeeName(normalized)
      : formatValue(normalized['employee_name']);

  await showDialog<void>(
    context: context,
    builder: (_) => AlertDialog(
      title: Text(titleName),
      content: SizedBox(
        width: 850,
        child: SingleChildScrollView(
          child:
              Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
            const DialogSectionTitle('Appointment Information'),
            Wrap(spacing: 10, runSpacing: 10, children: [
              DetailTile('Employee Name', titleName),
              DetailTile('Appointment Type',
                  formatDetailValue(normalized['category'], 'category')),
              DetailTile(
                  'Appointment',
                  formatDetailValue(
                      normalized['appointment_title'], 'appointment_title')),
              DetailTile(
                  'Other Duties',
                  formatDetailValue(
                      normalized['other_duties'], 'other_duties')),
              DetailTile(
                  'Type',
                  formatDetailValue(
                      normalized['appointment_type'], 'appointment_type')),
              AttachmentPdfTile(
                  'Appointment PDF', normalized['attachment_url']),
            ]),
          ]),
        ),
      ),
      actions: [
        TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Close')),
      ],
    ),
  );
}

Future<void> editAppointment(BuildContext context, Map<String, dynamic>? row,
    VoidCallback refresh) async {
  final isAdd = row == null;
  final source = normalizeRow(row ?? {});
  final employees = await employeeOptions();
  String? employeeId = isAdd ? null : source['employee_id']?.toString();
  final category =
      TextEditingController(text: formatEditValue(source['category']));
  final appointmentTitle =
      TextEditingController(text: formatEditValue(source['appointment_title']));
  final otherDuties =
      TextEditingController(text: formatEditValue(source['other_duties']));
  final appointmentType =
      TextEditingController(text: formatEditValue(source['appointment_type']));
  String attachmentUrl = formatEditValue(source['attachment_url']);
  String attachmentFileName = attachmentUrl.isEmpty || attachmentUrl == '-'
      ? ''
      : Uri.decodeFull(attachmentUrl.split('/').last.split('?').first);
  bool uploading = false;
  final formKey = GlobalKey<FormState>();

  final result = await showDialog<Map<String, dynamic>>(
    context: context,
    builder: (_) => StatefulBuilder(
      builder: (context, setDialogState) => AlertDialog(
        title: Text(isAdd ? 'Add Appointment' : 'Edit Appointment'),
        content: SizedBox(
          width: 790,
          child: Form(
            key: formKey,
            child: SingleChildScrollView(
              child: Wrap(spacing: 14, runSpacing: 14, children: [
                const DialogSectionTitle('Employee Information'),
                if (isAdd)
                  employeeAutocompleteField(
                    employees: employees,
                    employeeId: employeeId,
                    width: 728,
                    onEmployeeChanged: (v) =>
                        setDialogState(() => employeeId = v),
                  )
                else
                  ReadOnlyEmployeeBox(linkedEmployeeName(source)),
                const DialogSectionTitle('Appointment Information'),
                searchableOptionBox(
                    'Appointment Type', category, appointmentCategoryOptions),
                SizedBox(
                    width: 354,
                    child: TextFormField(
                        controller: appointmentTitle,
                        decoration:
                            const InputDecoration(labelText: 'Appointment'),
                        validator: (v) =>
                            v == null || v.trim().isEmpty ? 'Required' : null)),
                SizedBox(
                    width: 728,
                    child: TextFormField(
                        controller: otherDuties,
                        minLines: 2,
                        maxLines: 4,
                        decoration:
                            const InputDecoration(labelText: 'Other Duties'))),
                searchableOptionBox(
                    'Type', appointmentType, appointmentTypeOptions),
                SizedBox(
                  width: 354,
                  child: Container(
                    padding: const EdgeInsets.all(14),
                    decoration: BoxDecoration(
                        color: Colors.white,
                        borderRadius: BorderRadius.circular(18),
                        border: Border.all(color: _line)),
                    child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          OutlinedButton.icon(
                            onPressed: uploading
                                ? null
                                : () async {
                                    setDialogState(() => uploading = true);
                                    final uploaded =
                                        await pickAndUploadAppointmentPdf(
                                            context);
                                    if (!context.mounted) return;
                                    setDialogState(() {
                                      if (uploaded != null) {
                                        attachmentUrl = uploaded.url;
                                        attachmentFileName = uploaded.fileName;
                                      }
                                      uploading = false;
                                    });
                                  },
                            icon: uploading
                                ? const SizedBox(
                                    width: 16,
                                    height: 16,
                                    child: CircularProgressIndicator(
                                        strokeWidth: 2))
                                : const Icon(Icons.picture_as_pdf_rounded),
                            label: Text(uploading
                                ? 'Uploading...'
                                : (attachmentFileName.isEmpty
                                    ? 'Attach PDF'
                                    : 'Change PDF')),
                          ),
                          const SizedBox(height: 8),
                          Text(
                              attachmentFileName.isEmpty
                                  ? 'No PDF attached'
                                  : attachmentFileName,
                              maxLines: 2,
                              overflow: TextOverflow.ellipsis,
                              style: TextStyle(
                                  color: attachmentFileName.isEmpty
                                      ? _muted
                                      : _ink,
                                  fontWeight: FontWeight.w700,
                                  fontSize: 12)),
                          if (attachmentUrl.trim().isNotEmpty &&
                              attachmentUrl != '-')
                            TextButton.icon(
                                onPressed: () =>
                                    openPdfAttachment(context, attachmentUrl),
                                icon: const Icon(Icons.open_in_new_rounded),
                                label: const Text('Open PDF')),
                        ]),
                  ),
                ),
              ]),
            ),
          ),
        ),
        actions: [
          TextButton(
              onPressed: () => Navigator.pop(context),
              child: const Text('Cancel')),
          FilledButton(
              onPressed: () {
                if (!formKey.currentState!.validate()) return;
                Navigator.pop(
                    context,
                    <String, dynamic>{
                      'employee_id': isAdd
                          ? emptyToNull(employeeId)
                          : source['employee_id'],
                      'category': category.text.trim(),
                      'appointment_title': appointmentTitle.text.trim(),
                      'other_duties': otherDuties.text.trim(),
                      'appointment_type': appointmentType.text.trim(),
                      'attachment_url': emptyToNull(attachmentUrl),
                    }..removeWhere((_, value) =>
                        value == null || value.toString().trim().isEmpty));
              },
              child: const Text('Save')),
        ],
      ),
    ),
  );
  for (final c in [category, appointmentTitle, otherDuties, appointmentType]) {
    c.dispose();
  }
  if (result == null) return;
  await saveRow(context, 'employee_appointments', isAdd ? null : source['id'],
      result, refresh);
}

class RankingPage extends StatefulWidget {
  const RankingPage({super.key});

  @override
  State<RankingPage> createState() => _RankingPageState();
}

class _RankingPageState extends State<RankingPage> {
  String filter = 'All';
  String rankFilter = 'All';
  late Future<List<EditOption>> rankFilterOptionsFuture;

  @override
  void initState() {
    super.initState();
    rankFilterOptionsFuture = rankOptions();
  }

  bool _matchesRankingFilter(Map<String, dynamic> row, String selected) {
    final text = '${row['appointment'] ?? ''}'
        .toLowerCase()
        .replaceAll('_', ' ')
        .replaceAll('-', ' ');
    final isFullTime = text.contains('full') && text.contains('time');
    final isProbationary = text.contains('probationary');
    if (selected == 'Full-time') return isFullTime;
    if (selected == 'Probationary') return isProbationary;
    return isFullTime || isProbationary;
  }

  Iterable<String> _rankValues(Map<String, dynamic> row) sync* {
    for (final key in const [
      'previous_rank_text',
      'applied_rank_text',
      'approved_rank_text'
    ]) {
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
    final appointmentLabel =
        filter == 'All' ? 'Full-time and Probationary' : filter;
    final rankLabel = rankFilter == 'All' ? 'All Ranks' : rankFilter;
    return 'Ranking Report - $appointmentLabel - $rankLabel';
  }

  Future<List<dynamic>> _loadRankings() async {
    final rows = await activeOnlyRows(loadRankings(limit: 5000));
    return rows
        .map((item) => normalizeRow(Map<String, dynamic>.from(item as Map)))
        .where((row) =>
            _matchesRankingFilter(row, filter) && _matchesRankFilter(row))
        .toList();
  }

  @override
  Widget build(BuildContext context) => PageFrame(
        title: '2026 Faculty Ranking',
        subtitle:
            'Manage faculty ranking applications following the Excel ranking summary layout.',
        child: Column(children: [
          Card(
            child: Padding(
              padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
              child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(children: [
                      const Text('Filter:',
                          style: TextStyle(
                              fontWeight: FontWeight.w900, color: _ink)),
                      const SizedBox(width: 12),
                      for (final item in const [
                        'All',
                        'Full-time',
                        'Probationary'
                      ]) ...[
                        ChoiceChip(
                          label: Text(item == 'All'
                              ? 'All (Full-time + Probationary)'
                              : item),
                          selected: filter == item,
                          onSelected: (_) => setState(() {
                            filter = item;
                            rankFilter = 'All';
                          }),
                        ),
                        const SizedBox(width: 8),
                      ],
                    ]),
                    const SizedBox(height: 8),
                    FutureBuilder<List<EditOption>>(
                      future: rankFilterOptionsFuture,
                      builder: (context, snap) {
                        final ranks = snap.data ?? const <EditOption>[];
                        final options = <EditOption>[
                          const EditOption('All', 'All Ranks'),
                          ...uniqueOptions(ranks).map((option) =>
                              EditOption(option.value, option.value)),
                        ];
                        final selectedRank =
                            options.any((option) => option.value == rankFilter)
                                ? rankFilter
                                : 'All';
                        return rankFilterAutocompleteBox(
                          selectedRank: selectedRank,
                          options: options,
                          onChanged: (value) =>
                              setState(() => rankFilter = value),
                        );
                      },
                    ),
                  ]),
            ),
          ),
          const SizedBox(height: 14),
          Expanded(
            child: CrudTable(
              key: ValueKey('$filter|$rankFilter'),
              load: () => _loadRankings(),
              searchHint:
                  'Search employee, rank, salary, points, or appointment',
              addLabel: 'Add Ranking',
              reportTitle: _rankingReportTitle(),
              archiveTableName: 'ranking_applications',
              archiveModuleName: 'Ranking',
              minTableWidth: 0,
              showColumnDividers: true,
              columns: const [
                GridCol('employee_name', 'Employee Name',
                    flex: 5, primary: true),
                GridCol('appointment_title', 'Appointment', flex: 4),
                GridCol('previous_rank_text', 'Previous Rank', flex: 3),
                GridCol('previous_salary', 'Basic Salary',
                    flex: 3, isMoney: true),
                GridCol('applied_rank_text', 'Rank Applied', flex: 3),
                GridCol('applied_salary', 'Basic Salary Adjustment',
                    flex: 4, isMoney: true),
                GridCol('points_earned', 'Points Earned',
                    flex: 3, isNumber: true),
                GridCol('approved_rank_text', 'Approved Rank', flex: 3),
                GridCol('approved_date', 'Approved Date', flex: 3),
                GridCol('effective_date', 'Effective Date', flex: 3),
              ],
              onAdd: (ctx, refresh) => editRanking(ctx, null, refresh),
              onView: viewRanking,
              onEdit: editRanking,
              onApprove: approveRanking,
              showDelete: true,
              onDelete: (row) =>
                  db.from('ranking_applications').delete().eq('id', row['id']),
            ),
          ),
        ]),
      );
}

class RankFilterAutocompleteBox extends StatefulWidget {
  final String selectedRank;
  final List<EditOption> options;
  final ValueChanged<String> onChanged;

  const RankFilterAutocompleteBox(
      {super.key,
      required this.selectedRank,
      required this.options,
      required this.onChanged});

  @override
  State<RankFilterAutocompleteBox> createState() =>
      _RankFilterAutocompleteBoxState();
}

class _RankFilterAutocompleteBoxState extends State<RankFilterAutocompleteBox> {
  late TextEditingController controller;

  @override
  void initState() {
    super.initState();
    controller = TextEditingController(
        text: widget.selectedRank == 'All' ? 'All Ranks' : widget.selectedRank);
  }

  @override
  void didUpdateWidget(covariant RankFilterAutocompleteBox oldWidget) {
    super.didUpdateWidget(oldWidget);
    final nextText =
        widget.selectedRank == 'All' ? 'All Ranks' : widget.selectedRank;
    if (oldWidget.selectedRank != widget.selectedRank &&
        controller.text != nextText) {
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
            final sorted = uniqueOptions(widget.options).toList()
              ..sort((a, b) =>
                  a.label.toLowerCase().compareTo(b.label.toLowerCase()));
            final query = textEditingValue.text.trim().toLowerCase();
            if (query.isEmpty) return sorted;
            final normalizedQuery = normalizeRankKey(query);
            return sorted.where((option) {
              final value = option.value.toLowerCase();
              final label = option.label.toLowerCase();
              final normalizedValue = normalizeRankKey(option.value);
              final normalizedLabel = normalizeRankKey(option.label);
              return value.contains(query) ||
                  label.contains(query) ||
                  normalizedValue.contains(normalizedQuery) ||
                  normalizedLabel.contains(normalizedQuery);
            });
          },
          onSelected: (option) {
            controller.text = option.label;
            widget.onChanged(option.value);
          },
          fieldViewBuilder:
              (context, textController, focusNode, onFieldSubmitted) {
            if (textController.text != controller.text)
              textController.text = controller.text;
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
                if (widget.selectedRank == 'All')
                  textController.selection = TextSelection(
                      baseOffset: 0, extentOffset: textController.text.length);
              },
              onChanged: (value) {
                controller.text = value;
                final clean = value.trim();
                if (clean.isEmpty) {
                  widget.onChanged('All');
                  return;
                }
                final exact = uniqueOptions(widget.options)
                    .where((option) =>
                        option.label.toLowerCase() == clean.toLowerCase() ||
                        option.value.toLowerCase() == clean.toLowerCase() ||
                        normalizeRankKey(option.value) ==
                            normalizeRankKey(clean))
                    .toList();
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
                constraints:
                    const BoxConstraints(maxWidth: 520, maxHeight: 320),
                child: ListView.separated(
                  padding: EdgeInsets.zero,
                  shrinkWrap: true,
                  itemCount: options.length,
                  separatorBuilder: (_, __) => const Divider(height: 1),
                  itemBuilder: (context, index) {
                    final option = options.elementAt(index);
                    return ListTile(
                      dense: true,
                      title:
                          Text(option.label, overflow: TextOverflow.ellipsis),
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

Widget rankFilterAutocompleteBox(
        {required String selectedRank,
        required List<EditOption> options,
        required ValueChanged<String> onChanged}) =>
    RankFilterAutocompleteBox(
        selectedRank: selectedRank, options: options, onChanged: onChanged);

String employeeImportClean(String? value) {
  final v = (value ?? '').replaceAll('\u0000', '').trim();
  if (v.isEmpty) return '';
  final lower = v.toLowerCase();
  if (lower == 'null' || lower == 'none' || lower == 'n/a') return '';
  return v;
}

bool employeeImportIsBlank(Object? value) {
  final v = employeeImportClean('$value');
  return v.isEmpty || v == '0';
}

String employeeImportAny(Map<String, String> row, List<String> keys) {
  String normHeader(String value) =>
      value.toLowerCase().replaceAll(RegExp(r'[^a-z0-9]+'), '');
  final normalized = <String, String>{};
  for (final entry in row.entries) {
    normalized[normHeader(entry.key)] = entry.value;
  }
  for (final key in keys) {
    final direct = employeeImportClean(row[key]);
    if (direct.isNotEmpty) return direct;
    final loose = employeeImportClean(normalized[normHeader(key)]);
    if (loose.isNotEmpty) return loose;
  }
  return '';
}

String employeeImportPrimaryNameKey(String value) {
  final cleaned = value.replaceAll('.', ' ').replaceAll(',', ',').trim();
  if (cleaned.contains(',')) {
    final parts = cleaned.split(',');
    final last = parts.first.trim();
    final rest = parts.skip(1).join(' ').trim();
    final first = rest
        .split(RegExp(r'\s+'))
        .where((p) => p.trim().isNotEmpty)
        .cast<String>()
        .toList();
    if (last.isNotEmpty && first.isNotEmpty)
      return employeeImportNormalizeName('$last ${first.first}');
  }
  final tokens = employeeImportNormalizeName(cleaned)
      .split(RegExp(r'\s+'))
      .where((p) => p.isNotEmpty)
      .toList();
  if (tokens.length >= 2) return '${tokens.first} ${tokens[1]}';
  return employeeImportNormalizeName(cleaned);
}

Set<String> employeeImportCsvMatchKeys(Map<String, String> row) {
  final first = employeeImportAny(row, const [
    'emp_first_name',
    'first_name',
    'firstname',
    'given_name',
    'givenname'
  ]);
  final middle = employeeImportAny(row,
      const ['emp_middle_name', 'middle_name', 'middlename', 'middle_initial']);
  final last = employeeImportAny(row, const [
    'emp_last_name',
    'last_name',
    'lastname',
    'surname',
    'family_name'
  ]);
  final full =
      employeeImportAny(row, const ['full_name', 'employee_name', 'name']);
  return <String>{
    employeeImportNormalizeName('$last $first $middle'),
    employeeImportNormalizeName('$last $first'),
    employeeImportNormalizeName('$first $middle $last'),
    employeeImportNormalizeName('$first $last'),
    employeeImportNormalizeName(full),
    employeeImportPrimaryNameKey(full),
    employeeImportPrimaryNameKey('$last, $first $middle'),
  }..removeWhere((k) => k.isEmpty || k == 'NONE');
}

List<Map<String, dynamic>> employeeImportFindMatches(
    List<Map<String, dynamic>> existingRows,
    Map<String, List<Map<String, dynamic>>> byKey,
    Map<String, String> csvRow,
    String exactKey,
    String fullName) {
  final found = <String, Map<String, dynamic>>{};
  void addMatches(Iterable<Map<String, dynamic>> matches) {
    for (final item in matches) {
      found['${item['id']}'] = item;
    }
  }

  addMatches(byKey[exactKey] ?? const <Map<String, dynamic>>[]);
  for (final key in employeeImportCsvMatchKeys(csvRow)) {
    addMatches(byKey[key] ?? const <Map<String, dynamic>>[]);
  }

  if (found.isNotEmpty) return found.values.toList();

  final csvKeys = employeeImportCsvMatchKeys(csvRow);
  for (final item in existingRows) {
    final existingKeys = <String>{
      employeeImportNormalizeName('${item['name_key'] ?? ''}'),
      employeeImportNormalizeName('${item['full_name'] ?? ''}'),
      employeeImportPrimaryNameKey('${item['full_name'] ?? ''}'),
    }..removeWhere((k) => k.isEmpty);
    if (existingKeys.any(csvKeys.contains)) found['${item['id']}'] = item;
  }
  return found.values.toList();
}

String employeeImportNormalizeName(String value) {
  var v = value.toUpperCase().replaceAll('ÃƒÆ’Ã†â€™ÃƒÂ¢Ã¢â€šÂ¬Ã‹Å“', 'N');
  for (final token in const [
    'ATTY',
    'MR',
    'MS',
    'MRS',
    'JR',
    'SR',
    'III',
    'IV',
    'LPT',
    'MAED',
    'MBM',
    'MBA',
    'PHD',
    'RSW',
    'RCRIM',
    'RGC',
    'CPA',
    'RL',
    'CHRA',
    'MIT',
    'MST',
    'MSCRIM',
    'MSSW',
    'MMREM',
    'REA',
    'REB',
    'RPM',
    'PRM',
    'DBM',
    'CEPL',
    'MAPS',
    'MAT',
    'PE',
    'MSHRM',
    'CTP',
    'CHP',
    'MSPSY',
    'MSPY'
  ]) {
    v = v.replaceAll(RegExp('\\b$token\\b'), ' ');
  }
  return v
      .replaceAll(RegExp(r'[^A-Z0-9]+'), ' ')
      .trim()
      .replaceAll(RegExp(r'\s+'), ' ');
}

List<List<String>> parseEmployeeImportCsv(String input) {
  final rows = <List<String>>[];
  var row = <String>[];
  final cell = StringBuffer();
  var quoted = false;
  for (var i = 0; i < input.length; i++) {
    final ch = input[i];
    if (quoted) {
      if (ch == '"') {
        if (i + 1 < input.length && input[i + 1] == '"') {
          cell.write('"');
          i++;
        } else {
          quoted = false;
        }
      } else {
        cell.write(ch);
      }
    } else {
      if (ch == '"') {
        quoted = true;
      } else if (ch == ',') {
        row.add(cell.toString());
        cell.clear();
      } else if (ch == '\n') {
        row.add(cell.toString().replaceAll('\r', ''));
        cell.clear();
        rows.add(row);
        row = <String>[];
      } else {
        cell.write(ch);
      }
    }
  }
  if (cell.isNotEmpty || row.isNotEmpty) {
    row.add(cell.toString().replaceAll('\r', ''));
    rows.add(row);
  }
  return rows;
}

String employeeImportFullName(Map<String, String> r) {
  final existingFull =
      employeeImportAny(r, const ['full_name', 'employee_name', 'name']);
  if (existingFull.isNotEmpty)
    return existingFull.toUpperCase().replaceAll(RegExp(r'\s+'), ' ').trim();
  final last = employeeImportAny(r, const [
    'emp_last_name',
    'last_name',
    'lastname',
    'surname',
    'family_name'
  ]).toUpperCase();
  final first = employeeImportAny(r, const [
    'emp_first_name',
    'first_name',
    'firstname',
    'given_name',
    'givenname'
  ]).toUpperCase();
  final middle = employeeImportAny(r, const [
    'emp_middle_name',
    'middle_name',
    'middlename',
    'middle_initial'
  ]).toUpperCase();
  return [
    if (last.isNotEmpty) '$last,',
    if (first.isNotEmpty) first,
    if (middle.isNotEmpty) middle
  ].join(' ').replaceAll(RegExp(r'\s+'), ' ').trim();
}

String? employeeImportDate(String value) {
  final v = employeeImportClean(value);
  if (v.isEmpty || v == '0000-00-00') return null;
  final match = RegExp(r'^(\d{4})-(\d{1,2})-(\d{1,2})').firstMatch(v);
  if (match == null) return null;
  final y = int.tryParse(match.group(1)!);
  final m = int.tryParse(match.group(2)!);
  final d = int.tryParse(match.group(3)!);
  if (y == null || m == null || d == null || y < 1900) return null;
  return '${y.toString().padLeft(4, '0')}-${m.toString().padLeft(2, '0')}-${d.toString().padLeft(2, '0')}';
}

String employeeImportStatus(String value) {
  final v = employeeImportClean(value).toLowerCase();
  if (v.contains('inactive') ||
      v.contains('resigned') ||
      v.contains('separated')) return 'inactive';
  return 'active';
}

String employeeImportType(String value) {
  final v = employeeImportClean(value).toLowerCase();
  if (v.contains('part')) return 'part_time';
  if (v.contains('staff')) return 'staff';
  if (v.contains('probation')) return 'probationary';
  return 'full_time';
}

void putIfMissing(Map<String, dynamic> target, Map<String, dynamic> existing,
    String key, Object? value) {
  final v = value == null ? '' : employeeImportClean('$value');
  if (v.isEmpty) return;
  if (employeeImportIsBlank(existing[key])) target[key] = v;
}

Future<String> pickEmployeeCsvText() async {
  final input = html.FileUploadInputElement()..accept = '.csv,text/csv';
  input.click();
  await input.onChange.first;
  final file = input.files?.isNotEmpty == true ? input.files!.first : null;
  if (file == null) return '';
  final reader = html.FileReader();
  reader.readAsText(file);
  await reader.onLoad.first;
  return '${reader.result ?? ''}';
}

Future<void> importEmployeeCsvInfo(BuildContext context) async {
  try {
    final csvText = await pickEmployeeCsvText();
    if (csvText.trim().isEmpty) return;
    final rows = parseEmployeeImportCsv(csvText);
    if (rows.length < 2) {
      if (context.mounted) showSnack(context, 'No CSV rows found.');
      return;
    }
    final headers = rows.first.map((h) => h.trim()).toList();
    final existingRows = (await loadEmployees(limit: 5000))
        .map((e) => normalizeRow(Map<String, dynamic>.from(e as Map)))
        .toList();
    final byKey = <String, List<Map<String, dynamic>>>{};
    for (final e in existingRows) {
      final keys = <String>{
        employeeImportNormalizeName('${e['name_key'] ?? ''}'),
        employeeImportNormalizeName('${e['full_name'] ?? ''}'),
        employeeImportPrimaryNameKey('${e['full_name'] ?? ''}'),
      }..removeWhere((k) => k.isEmpty);
      final notes = '${e['notes'] ?? ''}';
      if (notes.toLowerCase().contains('aliases:')) {
        for (final alias in notes.split('|')) {
          final k =
              employeeImportNormalizeName(alias.replaceAll('Aliases:', ''));
          if (k.isNotEmpty) keys.add(k);
        }
      }
      for (final k in keys) {
        byKey.putIfAbsent(k, () => <Map<String, dynamic>>[]).add(e);
      }
    }

    final updates = <Map<String, dynamic>>[];
    var notFound = 0;
    final ambiguous = <String>[];
    var invalid = 0;
    var noChanges = 0;

    for (var i = 1; i < rows.length; i++) {
      final row = rows[i];
      final r = <String, String>{};
      for (var c = 0; c < headers.length && c < row.length; c++) {
        r[headers[c]] = row[c];
      }
      final first = employeeImportAny(r, const [
        'emp_first_name',
        'first_name',
        'firstname',
        'given_name',
        'givenname'
      ]);
      final last = employeeImportAny(r, const [
        'emp_last_name',
        'last_name',
        'lastname',
        'surname',
        'family_name'
      ]);
      if (first.isEmpty ||
          last.isEmpty ||
          first.toUpperCase() == 'NONE' ||
          last.toUpperCase() == 'NONE') {
        invalid++;
        continue;
      }
      final fullName = employeeImportFullName(r);
      final key = employeeImportNormalizeName(
          '$last $first ${employeeImportAny(r, const [
            'emp_middle_name',
            'middle_name',
            'middlename',
            'middle_initial'
          ])}');
      final data = <String, dynamic>{
        'name_key': key,
        'full_name': fullName,
        'bio_number': employeeImportAny(r, const [
          'bio_number',
          'biometric_number',
          'bio_no',
          'emp_bio_number',
          'emp_id',
          'employee_id',
          'employee_code'
        ]),
        'employee_code': employeeImportAny(
            r, const ['employee_code', 'emp_code', 'emp_id', 'employee_id']),
        'gender': employeeImportAny(r, const ['emp_gender', 'gender', 'sex']),
        'birth_date': employeeImportDate(employeeImportAny(r, const [
          'birthdate',
          'birth_date',
          'date_of_birth',
          'dob',
          'emp_birthdate'
        ])),
        'civil_status': employeeImportAny(
            r, const ['civil_status', 'civilstatus', 'marital_status']),
        'address': employeeImportAny(r, const [
          'emp_address',
          'address',
          'home_address',
          'residential_address'
        ]),
        'email':
            employeeImportAny(r, const ['email', 'email_address', 'emp_email']),
        'contact_number': employeeImportAny(r, const [
          'contact_no',
          'contact_number',
          'mobile_number',
          'phone_number',
          'emp_contact_no'
        ]),
        'school_graduated': employeeImportAny(
            r, const ['school_graduated', 'school', 'college_university']),
        'degree_course': employeeImportAny(
            r, const ['degree_attained', 'degree_course', 'course', 'program']),
        'education_level': employeeImportAny(r, const [
          'education_level',
          'educational_attainment',
          'degree_attained',
          'degree_course'
        ]),
        'date_hired': employeeImportDate(employeeImportAny(r, const [
          'employment_date',
          'date_hired',
          'hired_date',
          'date_started'
        ])),
        'starting_date': employeeImportDate(employeeImportAny(r, const [
          'employment_date',
          'date_hired',
          'hired_date',
          'date_started'
        ])),
        'guardian_name': employeeImportAny(
            r, const ['emp_g_name', 'guardian_name', 'emergency_contact_name']),
        'guardian_address': employeeImportAny(r, const [
          'emp_g_address',
          'guardian_address',
          'emergency_contact_address'
        ]),
        'guardian_contact': employeeImportAny(r, const [
          'emp_g_contact',
          'guardian_contact',
          'emergency_contact_number'
        ]),
        'designation': employeeImportAny(
            r, const ['emp_designation', 'designation', 'position']),
        'employment_status': employeeImportStatus(employeeImportAny(
            r, const ['is_active', 'status', 'employment_status'])),
        'employee_type': employeeImportType(employeeImportAny(
            r, const ['emp_status', 'employee_type', 'appointment_status'])),
        'source_workbook': 'tbl_employee.csv',
        'source_sheet': 'CSV Import',
        'source_row': i + 1,
        'updated_at': DateTime.now().toIso8601String(),
      }..removeWhere(
          (_, value) => value == null || employeeImportClean('$value').isEmpty);

      final matches =
          employeeImportFindMatches(existingRows, byKey, r, key, fullName);
      if (matches.length > 1) {
        ambiguous.add(fullName);
        continue;
      }
      if (matches.length == 1) {
        final e = matches.first;
        final update = <String, dynamic>{'id': e['id'], 'label': fullName};
        for (final field in [
          'bio_number',
          'employee_code',
          'gender',
          'birth_date',
          'civil_status',
          'address',
          'email',
          'contact_number',
          'school_graduated',
          'degree_course',
          'education_level',
          'date_hired',
          'starting_date',
          'guardian_name',
          'guardian_address',
          'guardian_contact',
          'designation',
          'employment_status',
          'employee_type'
        ]) {
          putIfMissing(update, e, field, data[field]);
        }
        if (update.length > 2)
          updates.add(update);
        else
          noChanges++;
      } else {
        notFound++;
      }
    }

    final ok = await showDialog<bool>(
      context: context,
      builder: (_) => AlertDialog(
        title: const Text('Import Employee Info?'),
        content: SizedBox(
          width: 520,
          child: Text(
              'Matched updates: ${updates.length}\nEmployees not found in system: $notFound\nNo changes needed: $noChanges\nSkipped invalid: $invalid\nSkipped ambiguous: ${ambiguous.length}\n\nOnly blank/missing fields will be filled. Existing non-empty values will not be overwritten. No new employee records will be added.'),
        ),
        actions: [
          TextButton(
              onPressed: () => Navigator.pop(context, false),
              child: const Text('Cancel')),
          FilledButton(
              onPressed: () => Navigator.pop(context, true),
              child: const Text('Apply Import')),
        ],
      ),
    );
    if (ok != true) return;

    for (final u in updates) {
      final id = u.remove('id');
      u.remove('label');
      await db.from('employees').update(u).eq('id', id);
    }
    if (context.mounted)
      showSnack(context,
          'Employee import completed. Updated ${updates.length}, not found $notFound, skipped ${ambiguous.length + invalid}.');
  } catch (e) {
    if (context.mounted) showSnack(context, 'Employee import failed: $e');
  }
}

class GridCol {
  final String key;
  final String label;
  final int flex;
  final bool primary;
  final bool isStatus;
  final bool isMoney;
  final bool isNumber;
  const GridCol(this.key, this.label,
      {this.flex = 1,
      this.primary = false,
      this.isStatus = false,
      this.isMoney = false,
      this.isNumber = false});
}

typedef AddHandler = Future<void> Function(
    BuildContext context, VoidCallback refresh);
typedef EditHandler = Future<void> Function(
    BuildContext context, Map<String, dynamic> row, VoidCallback refresh);
typedef ViewHandler = Future<void> Function(
    BuildContext context, Map<String, dynamic> row);
typedef ExtraRowActionBuilder = Widget? Function(
    BuildContext context, Map<String, dynamic> row, VoidCallback refresh);
typedef CrudCellBuilder = Widget? Function(BuildContext context,
    Map<String, dynamic> row, GridCol column, VoidCallback refresh);

class CrudTable extends StatefulWidget {
  final Future<List<dynamic>> Function() load;
  final String searchHint;
  final String initialSearch;
  final String addLabel;
  final bool allowAdd;
  final List<GridCol> columns;
  final AddHandler? onAdd;
  final EditHandler? onEdit;
  final ViewHandler? onView;
  final EditHandler? onApprove;
  final ExtraRowActionBuilder? extraAction;
  final CrudCellBuilder? cellBuilder;
  final bool showDelete;
  final String? reportTitle;
  final String? archiveTableName;
  final String? archiveModuleName;
  final List<int> pageSizeOptions;
  final int initialPageSize;
  final double minTableWidth;
  final bool showColumnDividers;
  final Future<dynamic> Function(Map<String, dynamic> row) onDelete;

  final bool showActions;
  const CrudTable(
      {super.key,
      required this.load,
      required this.searchHint,
      this.initialSearch = '',
      required this.addLabel,
      this.allowAdd = true,
      required this.columns,
      this.onAdd,
      this.onEdit,
      this.onView,
      this.onApprove,
      this.extraAction,
      this.cellBuilder,
      this.showDelete = true,
      this.showActions = true,
      this.reportTitle,
      this.archiveTableName,
      this.archiveModuleName,
      this.pageSizeOptions = const [1, 10, 100],
      this.initialPageSize = 10,
      this.minTableWidth = 0,
      this.showColumnDividers = false,
      required this.onDelete});

  @override
  State<CrudTable> createState() => _CrudTableState();
}

class _CrudTableState extends State<CrudTable> {
  late Future<List<dynamic>> future;
  String query = '';
  final ScrollController tableScrollController = ScrollController();
  final ScrollController crudOuterScrollController = ScrollController();
  int page = 0;
  int pageSize = _pageSize;
  String? sortKey;
  bool sortAscending = true;

  String get cacheKey =>
      widget.key?.toString() ?? widget.reportTitle ?? widget.addLabel;

  Future<List<dynamic>> loadAndCache() async {
    final rows = await widget.load();
    _crudTableDataCache[cacheKey] = rows;
    return rows;
  }

  @override
  void dispose() {
    tableScrollController.dispose();
    crudOuterScrollController.dispose();
    super.dispose();
  }

  @override
  void initState() {
    super.initState();
    query = widget.initialSearch;
    final options = widget.pageSizeOptions.isEmpty
        ? const [1, 10, 100]
        : widget.pageSizeOptions;
    pageSize = options.contains(widget.initialPageSize)
        ? widget.initialPageSize
        : options.first;
    future = loadAndCache();
    sortKey = widget.columns.first.key;
  }

  void refresh() => setState(() {
        future = loadAndCache();
      });

  void scrollBothToTop() {
    if (!mounted) return;
    if (tableScrollController.hasClients) tableScrollController.jumpTo(0);
    if (crudOuterScrollController.hasClients)
      crudOuterScrollController.jumpTo(0);
  }

  void goToTablePage(int nextPage) {
    setState(() => page = nextPage);
    WidgetsBinding.instance.addPostFrameCallback((_) {
      scrollBothToTop();
      WidgetsBinding.instance.addPostFrameCallback((_) => scrollBothToTop());
    });
  }

  double get actionWidth {
    if (!widget.showActions) return 0;
    var count = widget.onEdit == null ? 0 : 1; // Edit button
    if (widget.onView != null) count++;
    if (widget.onApprove != null) count++;
    if (widget.showDelete) count++;
    if (widget.extraAction != null) count++;
    return (count * 46).toDouble();
  }

  void printRows(List<Map<String, dynamic>> rows) {
    final baseTitle = widget.reportTitle ??
        (widget.addLabel.toLowerCase().startsWith('add ')
            ? '${widget.addLabel.substring(4)} Report'
            : '${widget.addLabel} Report');
    final printWindow = html.window.open('about:blank', '_blank');
    try {
      final markup = buildPrintableReportHtml(baseTitle, widget.columns, rows);
      final blob = html.Blob([markup], 'text/html');
      final url = html.Url.createObjectUrlFromBlob(blob);
      if (printWindow != null) {
        printWindow.location.href = url;
      } else {
        html.window.open(url, '_blank');
      }
    } catch (e) {
      if (mounted) showSnack(context, 'Print Failed: $e');
    }
  }

  @override
  Widget build(BuildContext context) => FutureBuilder<List<dynamic>>(
        future: future,
        initialData: _crudTableDataCache[cacheKey],
        builder: (context, snap) {
          final hasUsableData = snap.data != null;
          if (snap.connectionState != ConnectionState.done && !hasUsableData) {
            return const Center(child: CircularProgressIndicator());
          }
          if (snap.hasError && !hasUsableData) return ErrorBox('${snap.error}');
          final rows = (snap.data ?? [])
              .map((item) =>
                  normalizeRow(Map<String, dynamic>.from(item as Map)))
              .toList();
          final filtered = query.trim().isEmpty
              ? rows
              : rows
                  .where((row) =>
                      searchableText(row).contains(query.toLowerCase()))
                  .toList();
          final activeSortKey = sortKey ?? widget.columns.first.key;
          final sorted = [...filtered]
            ..sort((a, b) => compareRows(a, b, activeSortKey, sortAscending));
          final pageCount =
              sorted.isEmpty ? 1 : ((sorted.length - 1) ~/ pageSize) + 1;
          final safePage = page.clamp(0, pageCount - 1).toInt();
          final startIndex = sorted.isEmpty ? 0 : safePage * pageSize;
          final pageRows = sorted.skip(startIndex).take(pageSize).toList();
          final endIndex = sorted.isEmpty ? 0 : startIndex + pageRows.length;
          return Column(children: [
            TableToolbar(
              total: rows.length,
              showing: sorted.length,
              hint: widget.searchHint,
              addLabel: widget.addLabel,
              allowAdd: widget.allowAdd && widget.onAdd != null,
              columns: widget.columns,
              sortKey: activeSortKey,
              sortAscending: sortAscending,
              onSearch: (value) => setState(() {
                query = value;
                page = 0;
              }),
              onRefresh: refresh,
              onPrint: () => printRows(sorted),
              onAdd: widget.onAdd == null
                  ? null
                  : () => widget.onAdd!(context, refresh),
              onSortChanged: (value) => setState(() {
                sortKey = value ?? widget.columns.first.key;
                page = 0;
              }),
              onToggleSortDirection: () => setState(() {
                sortAscending = !sortAscending;
                page = 0;
              }),
            ),
            if (widget.pageSizeOptions.length > 1) ...[
              const SizedBox(height: 2),
              Align(
                alignment: Alignment.centerLeft,
                child: SizedBox(
                  width: 198,
                  height: 42,
                  child: Stack(
                    clipBehavior: Clip.none,
                    children: [
                      Positioned.fill(
                        child: Container(
                          padding: const EdgeInsets.fromLTRB(14, 7, 8, 4),
                          decoration: BoxDecoration(
                            color: _surface,
                            borderRadius: BorderRadius.circular(18),
                            border: Border.all(color: _primary, width: 1.4),
                          ),
                          child: DropdownButtonHideUnderline(
                            child: DropdownButton<int>(
                              value: pageSize,
                              isExpanded: true,
                              isDense: true,
                              borderRadius: BorderRadius.circular(16),
                              icon: const Icon(
                                  Icons.keyboard_arrow_down_rounded,
                                  size: 20),
                              style: const TextStyle(
                                color: _ink,
                                fontSize: 13,
                                fontWeight: FontWeight.w600,
                              ),
                              items: widget.pageSizeOptions
                                  .map((value) => DropdownMenuItem<int>(
                                        value: value,
                                        child: Text('$value per page'),
                                      ))
                                  .toList(),
                              onChanged: (value) => setState(() {
                                pageSize = value ?? pageSize;
                                page = 0;
                                WidgetsBinding.instance.addPostFrameCallback(
                                    (_) => scrollBothToTop());
                              }),
                            ),
                          ),
                        ),
                      ),
                      Positioned(
                        left: 13,
                        top: -8,
                        child: Container(
                          padding: const EdgeInsets.symmetric(horizontal: 4),
                          color: _bg,
                          child: const Text(
                            'Display Names',
                            style: TextStyle(
                              color: _primary,
                              fontSize: 11.5,
                              fontWeight: FontWeight.w800,
                              height: 1,
                            ),
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ],
            const SizedBox(height: 10),
            Expanded(
                child: sorted.isEmpty
                    ? const EmptyBox()
                    : buildTable(pageRows, activeSortKey)),
            const SizedBox(height: 6),
            PaginationFooter(
              page: safePage,
              pageCount: pageCount,
              start: sorted.isEmpty ? 0 : startIndex + 1,
              end: endIndex,
              total: sorted.length,
              onPrevious:
                  safePage > 0 ? () => goToTablePage(safePage - 1) : null,
              onNext: safePage < pageCount - 1
                  ? () => goToTablePage(safePage + 1)
                  : null,
            ),
          ]);
        },
      );

  Widget buildTable(List<Map<String, dynamic>> rows, String activeSortKey) =>
      Card(
        child: ClipRRect(
          borderRadius: BorderRadius.circular(22),
          child: LayoutBuilder(
            builder: (context, constraints) {
              final tableWidth = constraints.maxWidth > widget.minTableWidth
                  ? constraints.maxWidth
                  : widget.minTableWidth;
              return Scrollbar(
                controller: crudOuterScrollController,
                thumbVisibility: widget.minTableWidth > constraints.maxWidth,
                trackVisibility: widget.minTableWidth > constraints.maxWidth,
                notificationPredicate: (notification) =>
                    notification.metrics.axis == Axis.horizontal,
                child: SingleChildScrollView(
                  controller: crudOuterScrollController,
                  scrollDirection: Axis.horizontal,
                  child: SizedBox(
                    width: tableWidth,
                    child: Column(children: [
                      TableHeader(
                          columns: widget.columns,
                          sortKey: activeSortKey,
                          sortAscending: sortAscending,
                          showActions: widget.showActions,
                          actionWidth: actionWidth,
                          showColumnDividers: widget.showColumnDividers,
                          onSort: (key) {
                            setState(() {
                              if (sortKey == key) {
                                sortAscending = !sortAscending;
                              } else {
                                sortKey = key;
                                sortAscending = true;
                              }
                              page = 0;
                            });
                          }),
                      const Divider(height: 1, color: _line),
                      Expanded(
                        child: ListView.separated(
                          controller: tableScrollController,
                          itemCount: rows.length,
                          separatorBuilder: (_, __) =>
                              const Divider(height: 1, color: _line),
                          itemBuilder: (_, i) => TableRowItem(
                  row: rows[i],
                  columns: widget.columns,
                  index: i,
                  actionWidth: actionWidth,
                  showColumnDividers: widget.showColumnDividers,
                  onView: !widget.showActions || widget.onView == null
                      ? null
                      : () => widget.onView!(context, rows[i]),
                  onEdit: !widget.showActions || widget.onEdit == null
                      ? null
                      : () => widget.onEdit!(context, rows[i], refresh),
                  onApprove: widget.onApprove == null
                      ? null
                      : () => widget.onApprove!(context, rows[i], refresh),
                  approveDisabled: widget.onApprove != null &&
                      (formatEditValue(normalizeRow(rows[i])['approved_date'])
                              .isNotEmpty ||
                          formatEditValue(
                                  normalizeRow(rows[i])['approved_rank_text'])
                              .isNotEmpty),
                  extraAction: widget.extraAction == null
                      ? null
                      : widget.extraAction!(context, rows[i], refresh),
                  cellBuilder: widget.cellBuilder == null
                      ? null
                      : (cellContext, row, column) => widget.cellBuilder!(
                          cellContext, row, column, refresh),
                  onDelete: widget.showActions && widget.showDelete
                      ? () => confirmDelete(context, rows[i])
                      : null,
                          ),
                        ),
                      ),
                    ]),
                  ),
                ),
              );
            },
          ),
        ),
      );

  Future<void> confirmDelete(
      BuildContext context, Map<String, dynamic> row) async {
    final ok = await showDialog<bool>(
      context: context,
      builder: (_) => AlertDialog(
        title: const Text('Delete Record?'),
        content: Text(
            'This will remove ${formatValue(valueFor(row, widget.columns.first.key))} from this module.'),
        actions: [
          TextButton(
              onPressed: () => Navigator.pop(context, false),
              child: const Text('Cancel')),
          FilledButton.tonal(
              onPressed: () => Navigator.pop(context, true),
              child: const Text('Delete')),
        ],
      ),
    );
    if (ok != true) return;
    try {
      await archiveDeletedRecord(
        tableName: widget.archiveTableName,
        moduleName: widget.archiveModuleName ??
            archiveModuleFromTitle(widget.reportTitle, widget.addLabel),
        row: row,
      );
      await widget.onDelete(row);
      refresh();
      if (mounted) showSnack(context, 'Record Deleted.');
    } catch (e) {
      if (mounted) showSnack(context, 'Delete Failed: $e');
    }
  }
}

class TableToolbar extends StatelessWidget {
  final int total;
  final int showing;
  final String hint;
  final String addLabel;
  final bool allowAdd;
  final List<GridCol> columns;
  final String sortKey;
  final bool sortAscending;
  final ValueChanged<String> onSearch;
  final VoidCallback onRefresh;
  final VoidCallback onPrint;
  final VoidCallback? onAdd;
  final ValueChanged<String?> onSortChanged;
  final VoidCallback onToggleSortDirection;

  const TableToolbar(
      {super.key,
      required this.total,
      required this.showing,
      required this.hint,
      required this.addLabel,
      required this.allowAdd,
      required this.columns,
      required this.sortKey,
      required this.sortAscending,
      required this.onSearch,
      required this.onRefresh,
      required this.onPrint,
      required this.onAdd,
      required this.onSortChanged,
      required this.onToggleSortDirection});

  @override
  Widget build(BuildContext context) => Card(
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
          child: LayoutBuilder(builder: (context, constraints) {
            final compact = constraints.maxWidth < 940;
            final search = SizedBox(
              width: compact ? constraints.maxWidth : 390,
              child: TextField(
                  onChanged: onSearch,
                  decoration: InputDecoration(
                      prefixIcon: const Icon(Icons.search_rounded),
                      hintText: hint,
                      filled: true,
                      fillColor: _surfaceSoft)),
            );
            final sort = SizedBox(
              width: 200,
              child: DropdownButtonFormField<String>(
                  value: sortKey,
                  isExpanded: true,
                  decoration: const InputDecoration(labelText: 'Sort By'),
                  items: columns
                      .map((c) => DropdownMenuItem(
                          value: c.key,
                          child:
                              Text(c.label, overflow: TextOverflow.ellipsis)))
                      .toList(),
                  onChanged: onSortChanged),
            );
            final widgets = <Widget>[
              search,
              sort,
              OutlinedButton.icon(
                  onPressed: onToggleSortDirection,
                  icon: Icon(
                      sortAscending
                          ? Icons.arrow_upward_rounded
                          : Icons.arrow_downward_rounded,
                      size: 18),
                  label: Text(sortAscending ? 'A-Z' : 'Z-A')),
              Container(
                padding:
                    const EdgeInsets.symmetric(horizontal: 14, vertical: 13),
                decoration: BoxDecoration(
                    color: const Color(0xFFF8FAFC),
                    borderRadius: BorderRadius.circular(999),
                    border: Border.all(color: _line)),
                child: Row(mainAxisSize: MainAxisSize.min, children: [
                  const Icon(Icons.table_rows_rounded,
                      size: 18, color: _accent),
                  const SizedBox(width: 8),
                  Text('$showing Of $total',
                      style: const TextStyle(
                          color: Color(0xFF475569),
                          fontWeight: FontWeight.w800))
                ]),
              ),
              OutlinedButton.icon(
                  onPressed: onRefresh,
                  icon: const Icon(Icons.refresh_rounded),
                  label: const Text('Refresh')),
              FilledButton.tonalIcon(
                  onPressed: onPrint,
                  icon: const Icon(Icons.print_rounded),
                  label: const Text('Print')),
            ];
            if (allowAdd && onAdd != null)
              widgets.add(FilledButton.icon(
                  onPressed: onAdd,
                  icon: const Icon(Icons.add_rounded),
                  label: Text(addLabel)));
            if (compact)
              return Wrap(
                  spacing: 10,
                  runSpacing: 10,
                  crossAxisAlignment: WrapCrossAlignment.center,
                  children: widgets);
            return Row(children: [
              Expanded(child: search),
              for (final w in widgets.skip(1)) ...[const SizedBox(width: 12), w]
            ]);
          }),
        ),
      );
}

class TableHeader extends StatelessWidget {
  final List<GridCol> columns;
  final String sortKey;
  final bool sortAscending;
  final bool showActions;
  final double actionWidth;
  final bool showColumnDividers;
  final ValueChanged<String> onSort;

  const TableHeader(
      {super.key,
      required this.columns,
      required this.sortKey,
      required this.sortAscending,
      required this.showActions,
      required this.actionWidth,
      this.showColumnDividers = false,
      required this.onSort});

  @override
  Widget build(BuildContext context) => Container(
        color: const Color(0xFFF8FAFC),
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 5),
        child: Row(children: [
          for (final col in columns)
            Expanded(
              flex: col.flex,
              child: Container(
                decoration: showColumnDividers
                    ? const BoxDecoration(
                        border: Border(
                            right: BorderSide(
                                color: Color(0xFFD8E0EC), width: 1)))
                    : null,
                child: InkWell(
                  borderRadius: BorderRadius.circular(8),
                  onTap: () => onSort(col.key),
                  child: Padding(
                    padding: EdgeInsets.symmetric(
                        horizontal: showColumnDividers ? 5 : 12),
                    child: Row(children: [
                      Expanded(
                          child: Text(col.label,
                              maxLines: showColumnDividers ? 4 : 2,
                              softWrap: true,
                              overflow: showColumnDividers
                                  ? TextOverflow.visible
                                  : TextOverflow.ellipsis,
                              style: TextStyle(
                                  fontWeight: FontWeight.w900,
                                  color: _ink,
                                  fontSize: showColumnDividers ? 11.5 : 13.5,
                                  height: 1.15))),
                      if (sortKey == col.key)
                        Icon(
                            sortAscending
                                ? Icons.arrow_upward_rounded
                                : Icons.arrow_downward_rounded,
                            size: 15,
                            color: _primary),
                    ]),
                  ),
                ),
              ),
            ),
          if (showActions)
            SizedBox(
                width: actionWidth,
                child: const Text('Actions',
                    textAlign: TextAlign.center,
                    style: TextStyle(
                        fontWeight: FontWeight.w900,
                        color: _ink,
                        fontSize: 13))),
        ]),
      );
}

class TableRowItem extends StatelessWidget {
  final Map<String, dynamic> row;
  final List<GridCol> columns;
  final int index;
  final double actionWidth;
  final bool showColumnDividers;
  final VoidCallback? onView;
  final VoidCallback? onEdit;
  final VoidCallback? onApprove;
  final bool approveDisabled;
  final Widget? extraAction;
  final Widget? Function(BuildContext context, Map<String, dynamic> row,
      GridCol column)? cellBuilder;
  final VoidCallback? onDelete;

  const TableRowItem(
      {super.key,
      required this.row,
      required this.columns,
      required this.index,
      required this.actionWidth,
      this.showColumnDividers = false,
      this.onView,
      this.onEdit,
      this.onApprove,
      this.approveDisabled = false,
      this.extraAction,
      this.cellBuilder,
      this.onDelete});

  @override
  Widget build(BuildContext context) => Container(
        color: index.isEven ? _surface : _surfaceSoft,
        padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 11),
        constraints: const BoxConstraints(minHeight: 54),
        child: Row(crossAxisAlignment: CrossAxisAlignment.center, children: [
          for (final col in columns)
            Expanded(
                flex: col.flex,
                child: Container(
                    constraints: const BoxConstraints(minHeight: 48),
                    alignment: Alignment.centerLeft,
                    decoration: showColumnDividers
                        ? const BoxDecoration(
                            border: Border(
                                right: BorderSide(
                                    color: Color(0xFFE2E8F0), width: 1)))
                        : null,
                    padding: EdgeInsets.symmetric(
                        horizontal: showColumnDividers ? 5 : 12),
                    child: cellBuilder?.call(context, row, col) ??
                        tableCell(
                          col,
                          valueFor(row, col.key),
                          wrapText: showColumnDividers,
                        ),
                  ),
                ),
          SizedBox(
            width: actionWidth,
            child: Row(mainAxisAlignment: MainAxisAlignment.center, children: [
              if (onView != null)
                IconButton(
                    tooltip: 'View',
                    onPressed: onView,
                    icon: const Icon(Icons.visibility_rounded,
                        color: Color(0xFF0E7490), size: 19)),
              if (onEdit != null)
                IconButton(
                    tooltip: 'Edit',
                    onPressed: onEdit,
                    icon: const Icon(Icons.edit_rounded,
                        color: _primary, size: 19)),
              if (onApprove != null)
                IconButton(
                    tooltip: approveDisabled
                        ? 'Ranking already approved'
                        : 'Approve Applied Rank',
                    onPressed: approveDisabled ? null : onApprove,
                    icon: Icon(Icons.check_circle_rounded,
                        color: approveDisabled
                            ? const Color(0xFF94A3B8)
                            : const Color(0xFF16A34A),
                        size: 19)),
              if (extraAction != null) extraAction!,
              if (onDelete != null)
                IconButton(
                    tooltip: 'Delete',
                    onPressed: onDelete,
                    icon: const Icon(Icons.delete_outline_rounded,
                        color: _danger, size: 19)),
            ]),
          ),
        ]),
      );
}

Widget tableCell(GridCol col, Object? raw, {bool wrapText = false}) {
  if (col.isStatus)
    return Align(
        alignment: Alignment.centerLeft, child: StatusChip(formatValue(raw)));
  final text = col.isMoney
      ? formatMoney(raw)
      : col.isNumber
          ? formatNumber(raw)
          : formatValue(raw);
  return Tooltip(
      message: text,
      waitDuration: const Duration(milliseconds: 600),
      child: Text(text,
          maxLines: wrapText ? null : 2,
          softWrap: true,
          overflow: wrapText ? TextOverflow.visible : TextOverflow.ellipsis,
          style: TextStyle(
              fontWeight: col.primary ? FontWeight.w800 : FontWeight.w500,
              color: _ink,
              fontSize: wrapText ? 11.5 : 12.5,
              height: 1.15)));
}

class PaginationFooter extends StatelessWidget {
  final int page;
  final int pageCount;
  final int start;
  final int end;
  final int total;
  final VoidCallback? onPrevious;
  final VoidCallback? onNext;

  const PaginationFooter(
      {super.key,
      required this.page,
      required this.pageCount,
      required this.start,
      required this.end,
      required this.total,
      this.onPrevious,
      this.onNext});

  @override
  Widget build(BuildContext context) => Card(
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
          child: Row(children: [
            Expanded(
                child: Text(
                    total == 0
                        ? 'No Records'
                        : 'Showing $start-$end Of $total - Page ${page + 1} Of $pageCount',
                    style: const TextStyle(
                        color: _muted, fontWeight: FontWeight.w800))),
            OutlinedButton.icon(
                onPressed: onPrevious,
                icon: const Icon(Icons.chevron_left_rounded),
                label: const Text('Previous')),
            const SizedBox(width: 8),
            FilledButton.icon(
                onPressed: onNext,
                icon: const Icon(Icons.chevron_right_rounded),
                label: const Text('Next')),
          ]),
        ),
      );
}

class StatusChip extends StatelessWidget {
  final String label;
  const StatusChip(this.label, {super.key});

  @override
  Widget build(BuildContext context) {
    final v = label.toLowerCase();
    Color bg = const Color(0xFFF1F5F9);
    Color fg = _ink;
    if (v.contains('active') ||
        v.contains('ongoing') ||
        v.contains('on-going')) {
      bg = const Color(0xFFDCFCE7);
      fg = const Color(0xFF166534);
    }
    if (v.contains('renewal') ||
        v.contains('due') ||
        v.contains('waiting') ||
        v == 'pending' ||
        v.contains('conference')) {
      bg = const Color(0xFFFEF3C7);
      fg = const Color(0xFF92400E);
    }
    if (v.contains('responded on time') || v == 'resolved') {
      bg = const Color(0xFFDCFCE7);
      fg = const Color(0xFF166534);
    }
    if (v.contains('responded late') ||
        v.contains('warning') ||
        v.contains('waive')) {
      bg = const Color(0xFFFFEDD5);
      fg = const Color(0xFF9A3412);
    }
    if (v.contains('expired') ||
        v.contains('inactive') ||
        v.contains('separated') ||
        v.contains('resigned') ||
        v.contains('non-renewal') ||
        v.contains('dismissal')) {
      bg = const Color(0xFFFEE2E2);
      fg = const Color(0xFF991B1B);
    }
    return Container(
        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
        decoration:
            BoxDecoration(color: bg, borderRadius: BorderRadius.circular(999)),
        child: Text(label,
            maxLines: 1,
            overflow: TextOverflow.ellipsis,
            style: TextStyle(
                color: fg, fontSize: 12, fontWeight: FontWeight.w900)));
  }
}

class ErrorBox extends StatelessWidget {
  final String message;
  const ErrorBox(this.message, {super.key});

  @override
  Widget build(BuildContext context) => Card(
      color: const Color(0xFFFFF7ED),
      child: Padding(
          padding: const EdgeInsets.all(18),
          child: Text('Unable To Load Records: $message',
              style: const TextStyle(color: Color(0xFF9A3412)))));
}

class EmptyBox extends StatelessWidget {
  const EmptyBox({super.key});

  @override
  Widget build(BuildContext context) => const Card(
      child: Center(
          child: Padding(
              padding: EdgeInsets.all(34),
              child: Text('No Matching Records Found.',
                  style:
                      TextStyle(color: _muted, fontWeight: FontWeight.w700)))));
}

enum FieldKind { text, number, integer, date, dropdown, multiline }

class EditOption {
  final String value;
  final String label;
  final num? salary;
  const EditOption(this.value, this.label, {this.salary});
}

class EditField {
  final String key;
  final String label;
  final FieldKind kind;
  final bool required;
  final List<EditOption> options;
  final int lines;
  const EditField(this.key, this.label,
      {this.kind = FieldKind.text,
      this.required = false,
      this.options = const [],
      this.lines = 1});
}

class ReadOnlyEmployeeBox extends StatelessWidget {
  final String employeeName;
  const ReadOnlyEmployeeBox(this.employeeName, {super.key});

  @override
  Widget build(BuildContext context) => SizedBox(
        width: 728,
        child: Container(
          padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
          decoration: BoxDecoration(
              color: const Color(0xFFF8FAFC),
              borderRadius: BorderRadius.circular(18),
              border: Border.all(color: _line)),
          child:
              Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
            const Text('Employee Name',
                style: TextStyle(
                    color: Color(0xFF1E40AF),
                    fontWeight: FontWeight.w700,
                    fontSize: 12)),
            const SizedBox(height: 4),
            Text(employeeName,
                style: const TextStyle(
                    color: _ink, fontSize: 15, fontWeight: FontWeight.w800)),
          ]),
        ),
      );
}

Widget employeeAutocompleteField({
  required List<EditOption> employees,
  required String? employeeId,
  required ValueChanged<String?> onEmployeeChanged,
  double width = 354,
}) =>
    SizedBox(
      width: width,
      child: Autocomplete<EditOption>(
        displayStringForOption: (option) => option.label,
        optionsBuilder: (textEditingValue) {
          final sortedEmployees = uniqueOptions(employees).toList()
            ..sort((a, b) =>
                a.label.toLowerCase().compareTo(b.label.toLowerCase()));
          final query = textEditingValue.text.trim().toLowerCase();
          if (query.isEmpty) return sortedEmployees;
          final normalizedQuery = normalizeName(query);
          return sortedEmployees.where((option) {
            final label = option.label.toLowerCase();
            final normalizedLabel = normalizeName(option.label);
            return label.contains(query) ||
                normalizedLabel.contains(normalizedQuery);
          });
        },
        onSelected: (option) => onEmployeeChanged(option.value),
        fieldViewBuilder:
            (context, textController, focusNode, onFieldSubmitted) =>
                TextFormField(
          controller: textController,
          focusNode: focusNode,
          decoration: const InputDecoration(
            labelText: 'Employee Name',
            hintText: 'Select or type employee name',
            suffixIcon: Icon(Icons.search_rounded),
          ),
          validator: (_) => employeeId == null || employeeId.isEmpty
              ? 'Please select employee from the list'
              : null,
          onChanged: (value) {
            final typed = value.trim().toLowerCase();
            final exact = uniqueOptions(employees)
                .where((option) => option.label.toLowerCase() == typed)
                .toList();
            if (exact.isNotEmpty) {
              onEmployeeChanged(exact.first.value);
            } else {
              onEmployeeChanged(null);
            }
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

Widget addEmployeeSelectedLicenseCard(BuildContext context,
        SelectedLicenseInput entry, StateSetter setDialogState) =>
    SizedBox(
      width: 728,
      child: Container(
        margin: const EdgeInsets.only(bottom: 12),
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(18),
          border: Border.all(color: _line),
        ),
        child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Row(children: [
            Expanded(
              child: Text(entry.name,
                  maxLines: 2,
                  overflow: TextOverflow.ellipsis,
                  style: const TextStyle(
                      fontWeight: FontWeight.w900, color: _ink)),
            ),
            StatusChip(entry.status.isEmpty ? 'Select Expiry' : entry.status),
          ]),
          const SizedBox(height: 12),
          Wrap(
              spacing: 12,
              runSpacing: 12,
              crossAxisAlignment: WrapCrossAlignment.center,
              children: [
                SizedBox(
                  width: 220,
                  child: TextFormField(
                    controller: entry.number,
                    decoration:
                        const InputDecoration(labelText: 'License Number'),
                    validator: (value) => value == null || value.trim().isEmpty
                        ? 'Required'
                        : null,
                  ),
                ),
                SizedBox(
                  width: 220,
                  child: TextFormField(
                    controller: entry.expiry,
                    readOnly: true,
                    onTap: () => pickDateIntoController(context, entry.expiry,
                        afterPick: () => setDialogState(() => entry.status =
                            licenseStatusFromExpiry(entry.expiry.text))),
                    decoration: InputDecoration(
                      labelText: 'Expiry Date',
                      suffixIcon: IconButton(
                        tooltip: 'Pick expiry date',
                        icon: const Icon(Icons.calendar_month_rounded),
                        onPressed: () => pickDateIntoController(
                            context, entry.expiry,
                            afterPick: () => setDialogState(() => entry.status =
                                licenseStatusFromExpiry(entry.expiry.text))),
                      ),
                    ),
                    validator: (value) {
                      if (value == null || value.trim().isEmpty)
                        return 'Required';
                      return parseFlexibleDate(value.trim()) == null
                          ? 'Select a valid date'
                          : null;
                    },
                  ),
                ),
                OutlinedButton.icon(
                  onPressed: entry.uploadingAttachment
                      ? null
                      : () => pickAndUploadLicensePdf(
                          context, entry, setDialogState),
                  icon: entry.uploadingAttachment
                      ? const SizedBox(
                          width: 16,
                          height: 16,
                          child: CircularProgressIndicator(strokeWidth: 2))
                      : const Icon(Icons.picture_as_pdf_rounded),
                  label: Text(entry.uploadingAttachment
                      ? 'Uploading...'
                      : (entry.attachmentFileName.isEmpty
                          ? 'Attach PDF'
                          : 'Change PDF')),
                ),
                SizedBox(
                  width: 220,
                  child: Text(
                    entry.attachmentFileName.isEmpty
                        ? 'No PDF attached'
                        : entry.attachmentFileName,
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                    style: TextStyle(
                        color: entry.attachmentFileName.isEmpty ? _muted : _ink,
                        fontWeight: FontWeight.w700,
                        fontSize: 12),
                  ),
                ),
              ]),
        ]),
      ),
    );

Widget addEmployeeSelectedCertificateCard(BuildContext context,
        SelectedCertificateInput entry, StateSetter setDialogState) =>
    SizedBox(
      width: 728,
      child: Container(
        margin: const EdgeInsets.only(bottom: 12),
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(18),
          border: Border.all(color: _line),
        ),
        child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Row(children: [
            Expanded(
              child: Text(entry.name,
                  maxLines: 2,
                  overflow: TextOverflow.ellipsis,
                  style: const TextStyle(
                      fontWeight: FontWeight.w900, color: _ink)),
            ),
            StatusChip(entry.status.isEmpty ? 'Select Expiry' : entry.status),
          ]),
          const SizedBox(height: 12),
          Wrap(
              spacing: 12,
              runSpacing: 12,
              crossAxisAlignment: WrapCrossAlignment.center,
              children: [
                SizedBox(
                  width: 220,
                  child: TextFormField(
                    controller: entry.number,
                    decoration:
                        const InputDecoration(labelText: 'Certificate Number'),
                    validator: (value) => value == null || value.trim().isEmpty
                        ? 'Required'
                        : null,
                  ),
                ),
                SizedBox(
                  width: 220,
                  child: TextFormField(
                    controller: entry.expiry,
                    readOnly: true,
                    onTap: () => pickDateIntoController(context, entry.expiry,
                        afterPick: () => setDialogState(() => entry.status =
                            certificateStatusFromExpiry(entry.expiry.text))),
                    decoration: InputDecoration(
                      labelText: 'Expiry Date',
                      suffixIcon: IconButton(
                        tooltip: 'Pick expiry date',
                        icon: const Icon(Icons.calendar_month_rounded),
                        onPressed: () => pickDateIntoController(
                            context, entry.expiry,
                            afterPick: () => setDialogState(() => entry.status =
                                certificateStatusFromExpiry(
                                    entry.expiry.text))),
                      ),
                    ),
                    validator: (value) {
                      if (value == null || value.trim().isEmpty)
                        return 'Required';
                      return parseFlexibleDate(value.trim()) == null
                          ? 'Select a valid date'
                          : null;
                    },
                  ),
                ),
                OutlinedButton.icon(
                  onPressed: entry.uploadingAttachment
                      ? null
                      : () => pickAndUploadCertificatePdf(
                          context, entry, setDialogState),
                  icon: entry.uploadingAttachment
                      ? const SizedBox(
                          width: 16,
                          height: 16,
                          child: CircularProgressIndicator(strokeWidth: 2))
                      : const Icon(Icons.picture_as_pdf_rounded),
                  label: Text(entry.uploadingAttachment
                      ? 'Uploading...'
                      : (entry.attachmentFileName.isEmpty
                          ? 'Attach PDF'
                          : 'Change PDF')),
                ),
                SizedBox(
                  width: 220,
                  child: Text(
                    entry.attachmentFileName.isEmpty
                        ? 'No PDF attached'
                        : entry.attachmentFileName,
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                    style: TextStyle(
                        color: entry.attachmentFileName.isEmpty ? _muted : _ink,
                        fontWeight: FontWeight.w700,
                        fontSize: 12),
                  ),
                ),
              ]),
        ]),
      ),
    );

void openPdfAttachment(BuildContext context, Object? rawUrl) {
  final url = formatValue(rawUrl).trim();
  if (url.isEmpty || url == '-' || !url.toLowerCase().startsWith('http')) {
    showSnack(context, 'No PDF attachment available.');
    return;
  }
  final win = html.window.open(url, '_blank');
  if (win == null) {
    showSnack(context, 'Please allow pop-ups to open the PDF.');
  }
}

class DialogSectionTitle extends StatelessWidget {
  final String title;
  final double width;
  const DialogSectionTitle(this.title, {super.key, this.width = 728});

  @override
  Widget build(BuildContext context) => SizedBox(
        width: width,
        child: Container(
          margin: const EdgeInsets.only(top: 14, bottom: 8),
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
          decoration: BoxDecoration(
            color: const Color(0xFFEFF6FF),
            borderRadius: BorderRadius.circular(14),
            border: Border.all(color: const Color(0xFFBFDBFE)),
          ),
          child: Row(children: [
            const Expanded(
                child: Divider(color: Color(0xFF93C5FD), thickness: 1)),
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 14),
              child: Text(
                title.toUpperCase(),
                textAlign: TextAlign.center,
                style: const TextStyle(
                  fontSize: 13,
                  fontWeight: FontWeight.w900,
                  color: Color(0xFF1E3A8A),
                  letterSpacing: 0.6,
                ),
              ),
            ),
            const Expanded(
                child: Divider(color: Color(0xFF93C5FD), thickness: 1)),
          ]),
        ),
      );
}

Future<void> pickDateIntoController(
    BuildContext context, TextEditingController controller,
    {VoidCallback? afterPick}) async {
  final initial = parseFlexibleDate(controller.text) ?? DateTime.now();
  final picked = await showDatePicker(
    initialEntryMode: DatePickerEntryMode.calendarOnly,
    context: context,
    initialDate: initial,
    firstDate: DateTime(1900),
    lastDate: DateTime(DateTime.now().year + 30),
  );
  if (picked == null) return;
  controller.text = DateFormat('MM/dd/yyyy').format(picked);
  afterPick?.call();
}

class EmployeeStatusActionRow extends StatelessWidget {
  final String status;
  final Future<void> Function() onMarkResigned;
  const EmployeeStatusActionRow(
      {super.key, required this.status, required this.onMarkResigned});

  @override
  Widget build(BuildContext context) => SizedBox(
        width: 728,
        child: Container(
          padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
          decoration: BoxDecoration(
              color: const Color(0xFFF8FAFC),
              borderRadius: BorderRadius.circular(18),
              border: Border.all(color: _line)),
          child: Row(children: [
            const Text('Status:',
                style: TextStyle(color: _muted, fontWeight: FontWeight.w800)),
            const SizedBox(width: 10),
            StatusChip(status.isEmpty || status == '-' ? 'Active' : status),
            const Spacer(),
            FilledButton.tonalIcon(
              onPressed: status.toLowerCase().contains('resign')
                  ? null
                  : () async {
                      await onMarkResigned();
                      if (context.mounted) Navigator.of(context).pop();
                    },
              icon: const Icon(Icons.person_off_rounded),
              label: const Text('Mark as Resigned'),
            ),
          ]),
        ),
      );
}

String dialogSectionForField(String key) {
  const sections = <String, String>{
    'full_name': 'Personal Information',
    'bio_number': 'Personal Information',
    'gender': 'Personal Information',
    'civil_status': 'Personal Information',
    'birth_date': 'Personal Information',
    'address': 'Personal Information',
    'contact_number': 'Personal Information',
    'email': 'Personal Information',
    'education_level': 'Educational Background',
    'school_graduated': 'Educational Background',
    'degree_course': 'Educational Background',
    'guardian_name': 'Guardian Information',
    'guardian_relationship': 'Guardian Information',
    'guardian_contact': 'Guardian Information',
    'guardian_address': 'Guardian Information',
    'designation': 'Employment Information',
    'employee_type': 'Employment Information',
    'teaching_status': 'Employment Information',
    'employment_status': 'Employment Information',
    'date_hired': 'Employment Information',
    'date_resigned': 'Employment Information',
    'starting_date': 'Employment Information',
    'current_salary': 'Employment Information',
    'license_summary': 'Employment Information',
    'notes': 'Employment Information',
    'contract_type': 'Contract Information',
    'contract_start_date': 'Contract Information',
    'duration_months': 'Contract Information',
    'contract_end_date': 'Contract Information',
    'contract_attachment_url': 'Contract Information',
    'contract_status': 'Contract Information',
    'credential_kind': 'Credential Information',
    'license_name': 'License Information',
    'license_number': 'License Information',
    'license_issued_date': 'License Information',
    'license_expiry_date': 'License Information',
    'license_attachment_url': 'License Information',
    'license_status': 'License Information',
    'certificate_type': 'Certificate Information',
    'certificate_name': 'Certificate Information',
    'certificate_number': 'Certificate Information',
    'certificate_issued_date': 'Certificate Information',
    'certificate_expiry_date': 'Certificate Information',
    'certificate_attachment_url': 'Certificate Information',
    'certificate_status': 'Certificate Information',
  };
  return sections[key] ?? 'Other Information';
}

List<Widget> buildDialogFieldWidgets(
  BuildContext context,
  List<EditField> fields,
  Map<String, TextEditingController> controllers,
  Map<String, String?> selected,
  StateSetter setDialogState, {
  VoidCallback? onDateSubmit,
}) {
  final widgets = <Widget>[];
  String? currentSection;

  for (final f in fields) {
    final section = dialogSectionForField(f.key);
    if (section != currentSection) {
      if (widgets.isNotEmpty)
        widgets.add(const SizedBox(width: 728, height: 4));
      widgets.add(DialogSectionTitle(section));
      currentSection = section;
    }

    final width = f.kind == FieldKind.multiline ? 728.0 : 354.0;
    if (f.kind == FieldKind.dropdown) {
      if (f.key == 'employee_id') {
        widgets.add(employeeAutocompleteField(
          employees: f.options,
          employeeId: selected[f.key],
          width: width,
          onEmployeeChanged: (value) =>
              setDialogState(() => selected[f.key] = value),
        ));
        continue;
      }
      final opts = uniqueOptions(f.options);
      widgets.add(SizedBox(
        width: width,
        child: DropdownButtonFormField<String>(
          value: optionValueOrFirst(selected[f.key], opts, f.required),
          isExpanded: true,
          decoration: InputDecoration(labelText: f.label),
          items: opts
              .map((o) => DropdownMenuItem<String>(
                  value: o.value,
                  child: Text(o.label, overflow: TextOverflow.ellipsis)))
              .toList(),
          validator: (v) =>
              f.required && (v == null || v.isEmpty) ? 'Required' : null,
          onChanged: (v) => setDialogState(() => selected[f.key] = v),
        ),
      ));
      continue;
    }

    final isDate = f.kind == FieldKind.date;
    widgets.add(SizedBox(
      width: width,
      child: TextFormField(
        controller: controllers[f.key],
        readOnly: false,
        maxLines: f.kind == FieldKind.multiline ? f.lines : 1,
        keyboardType: isDate
            ? TextInputType.datetime
            : (f.kind == FieldKind.number || f.kind == FieldKind.integer
                ? TextInputType.number
                : TextInputType.text),
        inputFormatters: isDate ? [DateSlashInputFormatter()] : null,
        onFieldSubmitted: isDate ? (_) => onDateSubmit?.call() : null,
        decoration: InputDecoration(
          labelText: f.label,
          hintText: isDate ? 'MM/DD/YYYY' : null,
          suffixIcon: isDate
              ? IconButton(
                  tooltip: 'Pick date',
                  icon: const Icon(Icons.calendar_month_rounded),
                  onPressed: () =>
                      pickDateIntoController(context, controllers[f.key]!),
                )
              : null,
        ),
        validator: (v) {
          if (f.required && (v == null || v.trim().isEmpty)) return 'Required';
          if (isDate &&
              v != null &&
              v.trim().isNotEmpty &&
              parseFlexibleDate(v.trim()) == null) {
            return 'Select a valid date';
          }
          return null;
        },
      ),
    ));
  }

  return widgets;
}

Future<Map<String, dynamic>?> showRecordDialog(BuildContext context,
    String title, List<EditField> fields, Map<String, dynamic>? initial,
    {String? readOnlyEmployeeName, List<Widget> prefix = const []}) async {
  final formKey = GlobalKey<FormState>();
  final controllers = <String, TextEditingController>{};
  final selected = <String, String?>{};
  for (final f in fields) {
    final raw = initial?[f.key]?.toString();
    if (f.kind == FieldKind.dropdown) {
      selected[f.key] = optionValueOrFirst(raw, f.options, f.required);
    } else {
      controllers[f.key] =
          TextEditingController(text: formatEditValue(initial?[f.key]));
    }
  }
  void submitDialog() {
    if (!formKey.currentState!.validate()) return;
    final out = <String, dynamic>{};
    for (final f in fields) {
      out[f.key] = f.kind == FieldKind.dropdown
          ? emptyToNull(selected[f.key])
          : parseFieldValue(controllers[f.key]!.text, f.kind);
    }
    Navigator.pop(context, out);
  }

  final result = await showDialog<Map<String, dynamic>>(
    context: context,
    builder: (_) => StatefulBuilder(
      builder: (context, setDialogState) => AlertDialog(
        title: Text(title),
        content: SizedBox(
          width: 760,
          child: Form(
            key: formKey,
            child: SingleChildScrollView(
              child: Wrap(spacing: 14, runSpacing: 14, children: [
                if (readOnlyEmployeeName != null)
                  ReadOnlyEmployeeBox(readOnlyEmployeeName),
                ...prefix,
                ...buildDialogFieldWidgets(
                  context,
                  fields,
                  controllers,
                  selected,
                  setDialogState,
                  onDateSubmit: submitDialog,
                ),
              ]),
            ),
          ),
        ),
        actions: [
          TextButton(
              onPressed: () => Navigator.pop(context),
              child: const Text('Cancel')),
          FilledButton(
            onPressed: submitDialog,
            child: const Text('Save'),
          ),
        ],
      ),
    ),
  );
  for (final c in controllers.values) {
    c.dispose();
  }
  return result;
}

const educationBackgroundStatusOptions = [
  'Completed',
  'On-going',
  'Undergraduate'
];

class EducationBackgroundInput {
  final TextEditingController educationLevel = TextEditingController();
  final TextEditingController schoolGraduated = TextEditingController();
  final TextEditingController degreeCourse = TextEditingController();
  final TextEditingController yearGraduated = TextEditingController();
  final TextEditingController status = TextEditingController(text: 'Completed');
  final TextEditingController attachment = TextEditingController();
  String attachmentUrl = '';
  String attachmentFileName = '';
  bool uploadingAttachment = false;

  void dispose() {
    educationLevel.dispose();
    schoolGraduated.dispose();
    degreeCourse.dispose();
    yearGraduated.dispose();
    status.dispose();
    attachment.dispose();
  }

  bool get hasInput =>
      educationLevel.text.trim().isNotEmpty ||
      schoolGraduated.text.trim().isNotEmpty ||
      degreeCourse.text.trim().isNotEmpty ||
      yearGraduated.text.trim().isNotEmpty ||
      status.text.trim().isNotEmpty ||
      attachmentUrl.trim().isNotEmpty;

  Map<String, dynamic> toMap() => <String, dynamic>{
        'education_level': educationLevel.text.trim(),
        'school_graduated': schoolGraduated.text.trim(),
        'degree_course': degreeCourse.text.trim(),
        'year_graduated': yearGraduated.text.trim(),
        'status': status.text.trim(),
        'attachment_url': attachmentUrl.trim(),
      }..removeWhere(
          (_, value) => value == null || value.toString().trim().isEmpty);
}

Widget educationBackgroundInputCard(
  BuildContext context,
  EducationBackgroundInput entry,
  StateSetter setDialogState,
  VoidCallback onRemove,
) =>
    Container(
      width: 728,
      margin: const EdgeInsets.only(bottom: 10),
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: const Color(0xFFF8FAFC),
        borderRadius: BorderRadius.circular(18),
        border: Border.all(color: _line),
      ),
      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        Row(children: [
          const Icon(Icons.school_rounded, color: _primary, size: 20),
          const SizedBox(width: 8),
          const Expanded(
            child: Text('Educational Background',
                style: TextStyle(fontWeight: FontWeight.w900, color: _ink)),
          ),
          IconButton(
            tooltip: 'Remove educational background',
            onPressed: onRemove,
            icon: const Icon(Icons.close_rounded, color: _danger),
          ),
        ]),
        const SizedBox(height: 10),
        Wrap(spacing: 10, runSpacing: 10, children: [
          SizedBox(
            width: 342,
            child: TextFormField(
              controller: entry.educationLevel,
              decoration:
                  const InputDecoration(labelText: 'Educational Attainment'),
            ),
          ),
          SizedBox(
            width: 342,
            child: TextFormField(
              controller: entry.schoolGraduated,
              decoration: const InputDecoration(labelText: 'School Graduated'),
            ),
          ),
          SizedBox(
            width: 342,
            child: TextFormField(
              controller: entry.degreeCourse,
              decoration: const InputDecoration(labelText: 'Degree / Course'),
            ),
          ),
          SizedBox(
            width: 140,
            child: TextFormField(
              controller: entry.yearGraduated,
              keyboardType: TextInputType.number,
              decoration: const InputDecoration(labelText: 'Year Graduated'),
            ),
          ),
          SizedBox(
            width: 190,
            child: DropdownButtonFormField<String>(
              isExpanded: true,
              value:
                  educationBackgroundStatusOptions.contains(entry.status.text)
                      ? entry.status.text
                      : 'Completed',
              decoration: const InputDecoration(labelText: 'Status'),
              items: educationBackgroundStatusOptions
                  .map((status) => DropdownMenuItem<String>(
                        value: status,
                        child: Text(status,
                            overflow: TextOverflow.ellipsis,
                            style: const TextStyle(fontSize: 13)),
                      ))
                  .toList(),
              onChanged: (value) => setDialogState(
                  () => entry.status.text = value ?? 'Completed'),
            ),
          ),
          SizedBox(
            width: 342,
            child:
                Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
              OutlinedButton.icon(
                onPressed: entry.uploadingAttachment
                    ? null
                    : () async {
                        setDialogState(() => entry.uploadingAttachment = true);
                        final uploaded =
                            await pickAndUploadEducationPdf(context);
                        if (!context.mounted) return;
                        setDialogState(() {
                          if (uploaded != null) {
                            entry.attachmentUrl = uploaded.url;
                            entry.attachmentFileName = uploaded.fileName;
                            entry.attachment.text = uploaded.url;
                          }
                          entry.uploadingAttachment = false;
                        });
                      },
                icon: entry.uploadingAttachment
                    ? const SizedBox(
                        width: 16,
                        height: 16,
                        child: CircularProgressIndicator(strokeWidth: 2))
                    : const Icon(Icons.picture_as_pdf_rounded),
                label: Text(entry.uploadingAttachment
                    ? 'Uploading...'
                    : (entry.attachmentFileName.isEmpty
                        ? 'Attach PDF'
                        : 'Change PDF')),
              ),
              const SizedBox(height: 6),
              Text(
                entry.attachmentFileName.isEmpty
                    ? 'No PDF attached'
                    : entry.attachmentFileName,
                maxLines: 2,
                overflow: TextOverflow.ellipsis,
                style: TextStyle(
                    color: entry.attachmentFileName.isEmpty ? _muted : _ink,
                    fontWeight: FontWeight.w700,
                    fontSize: 12),
              ),
            ]),
          ),
        ]),
      ]),
    );

class AddEmployeeFullResult {
  final Map<String, dynamic> employee;
  final Map<String, dynamic> contract;
  final List<Map<String, dynamic>> licenses;
  final List<Map<String, dynamic>> certificates;
  final List<Map<String, dynamic>> educationBackgrounds;
  final Map<String, dynamic> appointment;

  const AddEmployeeFullResult({
    required this.employee,
    required this.contract,
    required this.licenses,
    required this.certificates,
    required this.educationBackgrounds,
    required this.appointment,
  });
}

Future<AddEmployeeFullResult?> showAddEmployeeFullDialog(
    BuildContext context,
    List<EditOption> contractTypes,
    List<String> licenseNames,
    List<String> certificateNames) async {
  final formKey = GlobalKey<FormState>();
  final fullName = TextEditingController();
  final bioNumber = TextEditingController();
  final birthDate = TextEditingController();
  final address = TextEditingController();
  final contactNumber = TextEditingController();
  final email = TextEditingController();
  final educationLevel = TextEditingController();
  final schoolGraduated = TextEditingController();
  final degreeCourse = TextEditingController();
  final guardianName = TextEditingController();
  final guardianRelationship = TextEditingController();
  final guardianContact = TextEditingController();
  final guardianAddress = TextEditingController();
  final designation = TextEditingController();
  final dateHired = TextEditingController();
  final contractStart = TextEditingController();
  final durationMonths = TextEditingController();
  final contractEnd = TextEditingController();
  final contractStatus = TextEditingController();
  final employeeAppointmentCategory = TextEditingController();
  final employeeAppointmentTitle = TextEditingController();
  final employeeAppointmentOtherDuties = TextEditingController();
  final employeeAppointmentType = TextEditingController();
  String employeeAppointmentAttachmentUrl = '';
  String employeeAppointmentAttachmentFileName = '';
  bool uploadingEmployeeAppointmentAttachment = false;

  String? gender = 'Male';
  String? civilStatus = 'Single';
  String? employeeType = 'full_time';
  String? teachingStatus = 'Teaching';
  String? employmentStatus = 'active';
  String? contractType =
      contractTypes.isNotEmpty ? contractTypes.first.value : 'Full-time';
  String contractAttachmentUrl = '';
  String contractAttachmentFileName = '';
  bool uploadingContract = false;
  bool isPartTimeEmployee() => employeeType == 'part_time';
  final selectedLicenses = <String, SelectedLicenseInput>{};
  final selectedCertificates = <String, SelectedCertificateInput>{};
  final educationBackgrounds = <EducationBackgroundInput>[
    EducationBackgroundInput(),
  ];

  void recomputeContract() {
    final start = parseFlexibleDate(contractStart.text);
    final months = int.tryParse(durationMonths.text.trim());
    if (start == null || months == null || months <= 0) return;
    final end = addContractMonths(start, months);
    contractEnd.text = DateFormat('MM/dd/yyyy').format(end);
    contractStatus.text = contractStatusFromEndDate(end);
  }

  String? requiredText(String? value) =>
      value == null || value.trim().isEmpty ? 'Required' : null;
  String? requiredDate(String? value) {
    if (value == null || value.trim().isEmpty) return 'Required';
    return parseFlexibleDate(value.trim()) == null
        ? 'Select a valid date'
        : null;
  }

  void submitAddEmployeeDialog() {
    recomputeContract();
    if (!formKey.currentState!.validate()) return;
    final employee = <String, dynamic>{
      'full_name': fullName.text.trim(),
      'bio_number': bioNumber.text.trim(),
      'gender': gender,
      'civil_status': civilStatus,
      'birth_date': toIsoDateInput(birthDate.text),
      'address': address.text.trim(),
      'contact_number': contactNumber.text.trim(),
      'email': emptyToNull(email.text.trim()),
      'education_level': educationLevel.text.trim(),
      'school_graduated': schoolGraduated.text.trim(),
      'degree_course': degreeCourse.text.trim(),
      'guardian_name': guardianName.text.trim(),
      'guardian_relationship': guardianRelationship.text.trim(),
      'guardian_contact': guardianContact.text.trim(),
      'guardian_address': guardianAddress.text.trim(),
      'designation': designation.text.trim(),
      'employee_type': employeeType,
      'teaching_status': teachingStatus,
      'employment_status': employmentStatus,
      'date_hired': toIsoDateInput(dateHired.text),
      'starting_date': toIsoDateInput(dateHired.text),
    }..removeWhere(
        (_, value) => value == null || value.toString().trim().isEmpty);
    employee['name_key'] =
        normalizeName(employee['full_name']?.toString() ?? '');
    final contract = <String, dynamic>{
      'contract_type': contractType,
      'contract_start_date': toIsoDateInput(contractStart.text),
      'duration_months': int.tryParse(durationMonths.text.trim()),
      'contract_end_date': toIsoDateInput(contractEnd.text),
      'attachment_url': emptyToNull(contractAttachmentUrl),
      'status': emptyToNull(contractStatus.text),
    }..removeWhere(
        (_, value) => value == null || value.toString().trim().isEmpty);
    final licenses = selectedLicenses.values
        .map((entry) => <String, dynamic>{
              'license_name': entry.name,
              'license_number': entry.number.text.trim(),
              'expiry_date': toIsoDateInput(entry.expiry.text),
              'attachment_url': emptyToNull(entry.attachmentUrl),
              'status': entry.status.isEmpty
                  ? licenseStatusFromExpiry(entry.expiry.text)
                  : entry.status,
            }..removeWhere(
                (_, value) => value == null || value.toString().trim().isEmpty))
        .toList();
    final certificates = selectedCertificates.values
        .map((entry) => <String, dynamic>{
              'certificate_type': 'National Certificate',
              'certificate_name': entry.name,
              'certificate_number': entry.number.text.trim(),
              'expiry_date': toIsoDateInput(entry.expiry.text),
              'attachment_url': emptyToNull(entry.attachmentUrl),
              'status': entry.status.isEmpty
                  ? certificateStatusFromExpiry(entry.expiry.text)
                  : entry.status,
            }..removeWhere(
                (_, value) => value == null || value.toString().trim().isEmpty))
        .toList();
    final educationRecords = educationBackgrounds
        .where((entry) => entry.hasInput)
        .map((entry) => entry.toMap())
        .where((record) => record.isNotEmpty)
        .toList();
    final appointmentRecord = <String, dynamic>{
      'category': employeeAppointmentCategory.text.trim(),
      'appointment_title': employeeAppointmentTitle.text.trim(),
      'other_duties': employeeAppointmentOtherDuties.text.trim(),
      'appointment_type': employeeAppointmentType.text.trim(),
      'attachment_url': employeeAppointmentAttachmentUrl.trim(),
    }..removeWhere(
        (_, value) => value == null || value.toString().trim().isEmpty);
    Navigator.pop(
        context,
        AddEmployeeFullResult(
          employee: employee,
          contract: contract,
          licenses: licenses,
          certificates: certificates,
          educationBackgrounds: educationRecords,
          appointment: appointmentRecord,
        ));
  }

  Widget textBox(String label, TextEditingController controller,
      {bool required = true,
      int lines = 1,
      bool date = false,
      TextInputType? keyboardType}) {
    return SizedBox(
      width: lines > 1 ? 728 : 354,
      child: TextFormField(
        controller: controller,
        maxLines: lines,
        readOnly: false,
        keyboardType: date ? TextInputType.datetime : keyboardType,
        inputFormatters: date ? [DateSlashInputFormatter()] : null,
        onFieldSubmitted: date ? (_) => submitAddEmployeeDialog() : null,
        decoration: InputDecoration(
          labelText: label,
          hintText: date ? 'MM/DD/YYYY' : null,
          suffixIcon: date
              ? IconButton(
                  tooltip: 'Pick date',
                  icon: const Icon(Icons.calendar_month_rounded),
                  onPressed: () => pickDateIntoController(context, controller),
                )
              : null,
        ),
        validator: (value) => required
            ? (date ? requiredDate(value) : requiredText(value))
            : (date &&
                    value != null &&
                    value.trim().isNotEmpty &&
                    parseFlexibleDate(value.trim()) == null
                ? 'Select a valid date'
                : null),
      ),
    );
  }

  Widget dropdownBox(String label, String? value,
      List<DropdownMenuItem<String>> items, ValueChanged<String?> onChanged,
      {bool required = true}) {
    return SizedBox(
      width: 354,
      child: DropdownButtonFormField<String>(
        value: value,
        isExpanded: true,
        decoration: InputDecoration(labelText: label),
        items: items,
        validator: (v) =>
            required && (v == null || v.isEmpty) ? 'Required' : null,
        onChanged: onChanged,
      ),
    );
  }

  final result = await showDialog<AddEmployeeFullResult>(
    context: context,
    builder: (_) => StatefulBuilder(
      builder: (context, setDialogState) => AlertDialog(
        title: const Text('Add Employee'),
        content: SizedBox(
          width: 790,
          child: Form(
            key: formKey,
            child: SingleChildScrollView(
              child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const DialogSectionTitle('Employee Information'),
                    Wrap(spacing: 14, runSpacing: 14, children: [
                      textBox('Full Name', fullName,
                          required: !isPartTimeEmployee()),
                      textBox('Bio Number', bioNumber,
                          required: !isPartTimeEmployee()),
                      dropdownBox(
                          'Gender',
                          gender,
                          const [
                            DropdownMenuItem(
                                value: 'Male', child: Text('Male')),
                            DropdownMenuItem(
                                value: 'Female', child: Text('Female')),
                          ],
                          (v) => setDialogState(() => gender = v)),
                      dropdownBox(
                          'Civil Status',
                          civilStatus,
                          const [
                            DropdownMenuItem(
                                value: 'Single', child: Text('Single')),
                            DropdownMenuItem(
                                value: 'Married', child: Text('Married')),
                            DropdownMenuItem(
                                value: 'Widowed', child: Text('Widowed')),
                            DropdownMenuItem(
                                value: 'Separated', child: Text('Separated')),
                          ],
                          (v) => setDialogState(() => civilStatus = v)),
                      textBox('Birth Date', birthDate,
                          date: true, required: !isPartTimeEmployee()),
                      textBox('Address', address,
                          lines: 2, required: !isPartTimeEmployee()),
                      textBox('Contact Number', contactNumber,
                          required: !isPartTimeEmployee()),
                      textBox('Email', email, required: false),
                      textBox('Educational Attainment', educationLevel,
                          required: !isPartTimeEmployee()),
                      textBox('School Graduated', schoolGraduated,
                          required: !isPartTimeEmployee()),
                      textBox('Degree / Course', degreeCourse,
                          required: !isPartTimeEmployee()),
                      textBox('Guardian Name', guardianName,
                          required: !isPartTimeEmployee()),
                      textBox('Guardian Relationship', guardianRelationship,
                          required: !isPartTimeEmployee()),
                      textBox('Guardian Contact', guardianContact,
                          required: !isPartTimeEmployee()),
                      textBox('Guardian Address', guardianAddress,
                          lines: 2, required: !isPartTimeEmployee()),
                      textBox('Designation', designation,
                          required: !isPartTimeEmployee()),
                      dropdownBox(
                          'Employee Type',
                          employeeType,
                          const [
                            DropdownMenuItem(
                                value: 'full_time', child: Text('Full Time')),
                            DropdownMenuItem(
                                value: 'probationary',
                                child: Text('Probationary')),
                            DropdownMenuItem(
                                value: 'part_time', child: Text('Part Time')),
                            DropdownMenuItem(
                                value: 'staff', child: Text('Staff')),
                            DropdownMenuItem(
                                value: 'faculty_staff',
                                child: Text('Faculty / Staff')),
                          ],
                          (v) => setDialogState(() => employeeType = v)),
                      dropdownBox(
                          'Teaching Status',
                          teachingStatus,
                          const [
                            DropdownMenuItem(
                                value: 'Teaching', child: Text('Teaching')),
                            DropdownMenuItem(
                                value: 'Non-Teaching',
                                child: Text('Non-Teaching')),
                          ],
                          (v) => setDialogState(() => teachingStatus = v)),
                      dropdownBox(
                          'Employee Status',
                          employmentStatus,
                          const [
                            DropdownMenuItem(
                                value: 'active', child: Text('Active')),
                            DropdownMenuItem(
                                value: 'inactive', child: Text('Inactive')),
                            DropdownMenuItem(
                                value: 'separated', child: Text('Separated')),
                            DropdownMenuItem(
                                value: 'resigned', child: Text('Resigned')),
                          ],
                          (v) => setDialogState(() => employmentStatus = v)),
                      textBox('Date Hired', dateHired,
                          date: true, required: !isPartTimeEmployee()),
                    ]),
                    const SizedBox(height: 16),
                    const DialogSectionTitle('Educational Background Records'),
                    Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          for (final entry in educationBackgrounds)
                            educationBackgroundInputCard(
                              context,
                              entry,
                              setDialogState,
                              () => setDialogState(() {
                                if (educationBackgrounds.length > 1) {
                                  educationBackgrounds.remove(entry);
                                  entry.dispose();
                                } else {
                                  entry.educationLevel.clear();
                                  entry.schoolGraduated.clear();
                                  entry.degreeCourse.clear();
                                  entry.yearGraduated.clear();
                                  entry.status.text = 'Completed';
                                  entry.attachment.clear();
                                  entry.attachmentUrl = '';
                                  entry.attachmentFileName = '';
                                }
                              }),
                            ),
                          OutlinedButton.icon(
                            onPressed: () => setDialogState(() =>
                                educationBackgrounds
                                    .add(EducationBackgroundInput())),
                            icon: const Icon(Icons.add_rounded),
                            label: const Text('Add Educational Background'),
                          ),
                        ]),
                    const SizedBox(height: 16),
                    const DialogSectionTitle('Contract Information'),
                    Wrap(spacing: 14, runSpacing: 14, children: [
                      dropdownBox(
                          'Contract Type',
                          contractType,
                          contractTypes
                              .map((o) => DropdownMenuItem(
                                  value: o.value, child: Text(o.label)))
                              .toList(),
                          (v) => setDialogState(() => contractType = v)),
                      SizedBox(
                        width: 354,
                        child: TextFormField(
                          controller: contractStart,
                          readOnly: false,
                          keyboardType: TextInputType.datetime,
                          inputFormatters: [DateSlashInputFormatter()],
                          onFieldSubmitted: (_) => submitAddEmployeeDialog(),
                          decoration: InputDecoration(
                            labelText: 'Contract Start Date',
                            hintText: 'MM/DD/YYYY',
                            suffixIcon: IconButton(
                              icon: const Icon(Icons.calendar_month_rounded),
                              onPressed: () => pickDateIntoController(
                                  context, contractStart,
                                  afterPick: () =>
                                      setDialogState(recomputeContract)),
                            ),
                          ),
                          validator: (v) =>
                              isPartTimeEmployee() ? null : requiredDate(v),
                        ),
                      ),
                      SizedBox(
                        width: 354,
                        child: TextFormField(
                          controller: durationMonths,
                          keyboardType: TextInputType.number,
                          decoration: const InputDecoration(
                              labelText: 'Duration in Months'),
                          validator: (v) {
                            if (v == null || v.trim().isEmpty) {
                              return isPartTimeEmployee() ? null : 'Required';
                            }
                            final months = int.tryParse(v.trim());
                            if (months == null || months <= 0)
                              return 'Enter valid months';
                            return null;
                          },
                          onChanged: (_) => setDialogState(recomputeContract),
                        ),
                      ),
                      textBox('Contract End Date', contractEnd,
                          date: true, required: !isPartTimeEmployee()),
                      SizedBox(
                        width: 354,
                        child: TextFormField(
                          controller: contractStatus,
                          readOnly: true,
                          decoration: const InputDecoration(
                              labelText: 'Contract Status'),
                          validator: (v) =>
                              isPartTimeEmployee() ? null : requiredText(v),
                        ),
                      ),
                      SizedBox(
                        width: 354,
                        child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              OutlinedButton.icon(
                                onPressed: uploadingContract
                                    ? null
                                    : () async {
                                        setDialogState(
                                            () => uploadingContract = true);
                                        final uploaded =
                                            await pickAndUploadContractPdf(
                                                context);
                                        if (!context.mounted) return;
                                        setDialogState(() {
                                          if (uploaded != null) {
                                            contractAttachmentUrl =
                                                uploaded.url;
                                            contractAttachmentFileName =
                                                uploaded.fileName;
                                          }
                                          uploadingContract = false;
                                        });
                                      },
                                icon: uploadingContract
                                    ? const SizedBox(
                                        width: 16,
                                        height: 16,
                                        child: CircularProgressIndicator(
                                            strokeWidth: 2))
                                    : const Icon(Icons.picture_as_pdf_rounded),
                                label: Text(uploadingContract
                                    ? 'Uploading...'
                                    : 'Attach Contract PDF'),
                              ),
                              const SizedBox(height: 6),
                              Text(
                                  contractAttachmentFileName.isEmpty
                                      ? 'No PDF attached'
                                      : contractAttachmentFileName,
                                  maxLines: 2,
                                  overflow: TextOverflow.ellipsis,
                                  style: const TextStyle(
                                      color: _muted,
                                      fontWeight: FontWeight.w700,
                                      fontSize: 12)),
                            ]),
                      ),
                    ]),
                    const SizedBox(height: 16),
                    const DialogSectionTitle('License Information (Optional)'),
                    Wrap(spacing: 10, runSpacing: 8, children: [
                      for (final license in licenseNames)
                        SizedBox(
                          width: 228,
                          child: CheckboxListTile(
                            dense: true,
                            contentPadding: EdgeInsets.zero,
                            controlAffinity: ListTileControlAffinity.leading,
                            title: Text(license,
                                maxLines: 2,
                                overflow: TextOverflow.ellipsis,
                                style: const TextStyle(
                                    fontSize: 13,
                                    fontWeight: FontWeight.w700,
                                    color: _ink)),
                            value: selectedLicenses.containsKey(license),
                            onChanged: (checked) => setDialogState(() {
                              if (checked == true) {
                                selectedLicenses.putIfAbsent(license,
                                    () => SelectedLicenseInput(license));
                              } else {
                                selectedLicenses.remove(license)?.dispose();
                              }
                            }),
                          ),
                        ),
                    ]),
                    if (selectedLicenses.isNotEmpty) ...[
                      const SizedBox(height: 10),
                      for (final entry in selectedLicenses.values)
                        addEmployeeSelectedLicenseCard(
                            context, entry, setDialogState),
                    ],
                    const SizedBox(height: 16),
                    const DialogSectionTitle(
                        'Certificate Information (Optional)'),
                    Wrap(spacing: 10, runSpacing: 8, children: [
                      for (final cert in certificateNames)
                        SizedBox(
                          width: 228,
                          child: CheckboxListTile(
                            dense: true,
                            contentPadding: EdgeInsets.zero,
                            controlAffinity: ListTileControlAffinity.leading,
                            title: Text(cert,
                                maxLines: 2,
                                overflow: TextOverflow.ellipsis,
                                style: const TextStyle(
                                    fontSize: 13,
                                    fontWeight: FontWeight.w700,
                                    color: _ink)),
                            value: selectedCertificates.containsKey(cert),
                            onChanged: (checked) => setDialogState(() {
                              if (checked == true) {
                                selectedCertificates.putIfAbsent(
                                    cert, () => SelectedCertificateInput(cert));
                              } else {
                                selectedCertificates.remove(cert)?.dispose();
                              }
                            }),
                          ),
                        ),
                    ]),
                    if (selectedCertificates.isNotEmpty) ...[
                      const SizedBox(height: 10),
                      for (final entry in selectedCertificates.values)
                        addEmployeeSelectedCertificateCard(
                            context, entry, setDialogState),
                    ],
                  ]),
            ),
          ),
        ),
        actions: [
          TextButton(
              onPressed: () => Navigator.pop(context),
              child: const Text('Cancel')),
          FilledButton(
            onPressed: submitAddEmployeeDialog,
            child: const Text('Save'),
          ),
        ],
      ),
    ),
  );

  for (final c in [
    fullName,
    bioNumber,
    birthDate,
    address,
    contactNumber,
    email,
    educationLevel,
    schoolGraduated,
    degreeCourse,
    guardianName,
    guardianRelationship,
    guardianContact,
    guardianAddress,
    designation,
    dateHired,
    contractStart,
    durationMonths,
    contractEnd,
    contractStatus,
    employeeAppointmentCategory,
    employeeAppointmentTitle,
    employeeAppointmentOtherDuties,
    employeeAppointmentType
  ]) {
    c.dispose();
  }
  for (final entry in selectedLicenses.values) {
    entry.dispose();
  }
  for (final entry in selectedCertificates.values) {
    entry.dispose();
  }
  for (final entry in educationBackgrounds) {
    entry.dispose();
  }
  return result;
}

Future<void> addEmployeeFull(BuildContext context, VoidCallback refresh) async {
  final result = await showAddEmployeeFullDialog(
    context,
    await contractTypeOptions(),
    await licenseNameOptions(),
    await certificateNameOptions(),
  );
  if (result == null) return;

  try {
    final inserted = await db
        .from('employees')
        .insert(upperCaseDataMap(result.employee))
        .select('id')
        .single();
    final employeeId = inserted['id'];

    if (result.appointment.isNotEmpty) {
      await db.from('employee_appointments').insert({
        ...upperCaseDataMap(result.appointment),
        'employee_id': employeeId,
      });
    }
    if (result.contract.isNotEmpty) {
      await db.from('employee_contracts').insert({
        ...upperCaseDataMap(result.contract),
        'employee_id': employeeId,
      });
    }
    if (result.educationBackgrounds.isNotEmpty) {
      await db.from('employee_educational_backgrounds').insert([
        for (final education in result.educationBackgrounds)
          {...upperCaseDataMap(education), 'employee_id': employeeId}
      ]);
    }
    if (result.licenses.isNotEmpty) {
      await db.from('employee_licenses').insert([
        for (final license in result.licenses)
          {...upperCaseDataMap(license), 'employee_id': employeeId}
      ]);
    }
    if (result.certificates.isNotEmpty) {
      await db.from('employee_certificates').insert([
        for (final certificate in result.certificates)
          {...upperCaseDataMap(certificate), 'employee_id': employeeId}
      ]);
    }

    refresh();
    await showActionAlert(context, 'Employee Saved',
        'Employee, contract, license, and certificate information were saved successfully.');
  } catch (e) {
    showSnack(context, 'Save Failed: $e');
  }
}

Future<void> viewEmployee(
    BuildContext context, Map<String, dynamic> row) async {
  try {
    final contracts = await db
        .from('employee_contracts')
        .select()
        .eq('employee_id', row['id'])
        .order('contract_start_date', ascending: false);
    final educationBackgrounds = await db
        .from('employee_educational_backgrounds')
        .select()
        .eq('employee_id', row['id'])
        .order('year_graduated', ascending: false);
    final licenses = await db
        .from('employee_licenses')
        .select()
        .eq('employee_id', row['id'])
        .order('expiry_date');
    final certificates = await db
        .from('employee_certificates')
        .select()
        .eq('employee_id', row['id'])
        .order('expiry_date');
    if (!context.mounted) return;
    await showDialog<void>(
      context: context,
      builder: (_) => AlertDialog(
        title: Text(formatValue(row['full_name'])),
        content: SizedBox(
          width: 820,
          child: SingleChildScrollView(
            child:
                Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
              detailSection('Personal Information', row, const {
                'Bio Number': 'bio_number',
                'Gender': 'gender',
                'Civil Status': 'civil_status',
                'Birth Date': 'birth_date',
                'Address': 'address',
                'Contact Number': 'contact_number',
                'Email': 'email',
              }),
              detailSection('Educational Background', row, const {
                'Educational Attainment': 'education_level',
                'School Graduated': 'school_graduated',
                'Degree / Course': 'degree_course',
              }),
              relatedSection('Educational Background Records',
                  educationBackgrounds, const [
                'education_level',
                'school_graduated',
                'degree_course',
                'year_graduated',
                'status',
                'attachment_url'
              ]),
              detailSection('Guardian Information', row, const {
                'Guardian Name': 'guardian_name',
                'Relationship': 'guardian_relationship',
                'Guardian Contact': 'guardian_contact',
                'Guardian Address': 'guardian_address',
              }),
              detailSection('Employment Information', row, const {
                'Designation': 'designation',
                'Employee Type': 'employee_type',
                'Teaching Status': 'teaching_status',
                'Date Hired': 'date_hired_display',
                'Date Resigned': 'date_resigned_display',
                'Employee Status': 'employment_status',
              }),
              relatedSection('Contracts', contracts, const [
                'contract_type',
                'contract_start_date',
                'duration_months',
                'contract_end_date',
                'status',
                'attachment_url'
              ]),
              relatedSection('Licenses', licenses, const [
                'license_name',
                'license_number',
                'issued_date',
                'expiry_date',
                'status',
                'attachment_url'
              ]),
              relatedSection('Certificates', certificates, const [
                'certificate_type',
                'certificate_name',
                'certificate_number',
                'issued_date',
                'expiry_date',
                'status',
                'attachment_url'
              ]),
            ]),
          ),
        ),
        actions: [
          TextButton(
              onPressed: () => Navigator.pop(context),
              child: const Text('Close'))
        ],
      ),
    );
  } catch (e) {
    showSnack(context, 'View Failed: $e');
  }
}

Future<void> viewRanking(BuildContext context, Map<String, dynamic> row) async {
  final normalized = normalizeRow(row);
  await showDialog<void>(
    context: context,
    builder: (_) => AlertDialog(
      title: Text(formatValue(normalized['employee_name'])),
      content: SizedBox(
        width: 820,
        child: SingleChildScrollView(
          child:
              Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
            detailSection('Ranking Information', normalized, const {
              'Employee Name': 'employee_name',
              'Appointment': 'appointment',
              'Previous Rank': 'previous_rank_text',
              'Basic Salary': 'previous_salary',
              'Rank Applied': 'applied_rank_text',
              'Basic Salary Adjustment': 'applied_salary',
              'Points Earned': 'points_earned',
              'Approved Rank': 'approved_rank_text',
              'Salary Rate': 'approved_salary',
            }),
          ]),
        ),
      ),
      actions: [
        TextButton(
            onPressed: () => Navigator.pop(context), child: const Text('Close'))
      ],
    ),
  );
}

Widget detailSection(
        String title, Map<String, dynamic> row, Map<String, String> fields) =>
    Padding(
      padding: const EdgeInsets.only(bottom: 18),
      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        Text(title,
            style: const TextStyle(
                fontSize: 16, fontWeight: FontWeight.w900, color: _ink)),
        const SizedBox(height: 8),
        Wrap(spacing: 10, runSpacing: 10, children: [
          for (final item in fields.entries)
            DetailTile(item.key,
                formatDetailValue(valueFor(row, item.value), item.value))
        ]),
      ]),
    );

Widget relatedSection(String title, List<dynamic> records, List<String> keys) =>
    Padding(
      padding: const EdgeInsets.only(bottom: 18),
      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        Text(title,
            style: const TextStyle(
                fontSize: 16, fontWeight: FontWeight.w900, color: _ink)),
        const SizedBox(height: 8),
        if (records.isEmpty)
          const Text('No record added.',
              style: TextStyle(color: _muted, fontWeight: FontWeight.w600))
        else
          for (final rec in records)
            Container(
              width: double.infinity,
              margin: const EdgeInsets.only(bottom: 8),
              padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
              decoration: BoxDecoration(
                  color: const Color(0xFFF8FAFC),
                  borderRadius: BorderRadius.circular(14),
                  border: Border.all(color: _line)),
              child: Wrap(spacing: 8, runSpacing: 8, children: [
                for (final key in keys)
                  DetailTile(
                      titleCase(key), formatDetailValue((rec as Map)[key], key))
              ]),
            ),
      ]),
    );

class AttachmentPdfTile extends StatelessWidget {
  final String label;
  final Object? url;
  const AttachmentPdfTile(this.label, this.url, {super.key});

  @override
  Widget build(BuildContext context) {
    final value = formatValue(url).trim();
    final hasPdf = value.isNotEmpty &&
        value != '-' &&
        value.toLowerCase().startsWith('http');
    return SizedBox(
      width: 354,
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
        decoration: BoxDecoration(
          color: _surfaceSoft,
          borderRadius: BorderRadius.circular(14),
          border: Border.all(color: _line),
        ),
        child: Row(children: [
          const Icon(Icons.picture_as_pdf_rounded, color: _danger, size: 20),
          const SizedBox(width: 10),
          Expanded(
            child: Text(
              hasPdf ? label : 'No PDF attached',
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
              style: const TextStyle(fontWeight: FontWeight.w800, color: _ink),
            ),
          ),
          const SizedBox(width: 8),
          TextButton.icon(
            onPressed: hasPdf ? () => openPdfAttachment(context, value) : null,
            icon: const Icon(Icons.open_in_new_rounded, size: 17),
            label: const Text('Open'),
          ),
        ]),
      ),
    );
  }
}

class DetailTile extends StatelessWidget {
  final String label;
  final String value;
  const DetailTile(this.label, this.value, {super.key});

  @override
  Widget build(BuildContext context) => SizedBox(
        width: 245,
        child: Container(
          padding: const EdgeInsets.all(10),
          decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: _line)),
          child:
              Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
            Text(label,
                style: const TextStyle(
                    fontSize: 11, color: _muted, fontWeight: FontWeight.w800)),
            const SizedBox(height: 3),
            Text(value,
                style: const TextStyle(
                    fontSize: 13, color: _ink, fontWeight: FontWeight.w700)),
          ]),
        ),
      );
}

Future<List<EditOption>> employeeOptions() async {
  final rows = await loadActiveEmployees(limit: 5000);
  final options = rows
      .map((item) {
        final row = normalizeRow(Map<String, dynamic>.from(item as Map));
        return EditOption('${row['id']}', formatValue(row['full_name']));
      })
      .where((option) => option.value.trim().isNotEmpty && option.label != '-')
      .toList();
  options
      .sort((a, b) => a.label.toLowerCase().compareTo(b.label.toLowerCase()));
  return uniqueOptions(options);
}

String licenseFullDescription(Object? value) {
  final raw = '${value ?? ''}'.trim();
  if (raw.isEmpty) return '';
  final key = raw
      .toUpperCase()
      .replaceAll(RegExp(r'[^A-Z0-9]+'), ' ')
      .replaceAll(RegExp(r'\s+'), ' ')
      .trim();
  const descriptions = <String, String>{
    'LPT': 'Licensed Professional Teacher',
    'LICENSED PROFESSIONAL TEACHER LPT': 'Licensed Professional Teacher',
    'LICENSED PROFESSIONAL TEACHER': 'Licensed Professional Teacher',
    'RCRIM': 'Registered Criminologist',
    'REGISTERED CRIMINOLOGIST RCRIM': 'Registered Criminologist',
    'REGISTERED CRIMINOLOGIST': 'Registered Criminologist',
    'RN': 'Registered Nurse',
    'REGISTERED NURSE RN': 'Registered Nurse',
    'REGISTERED NURSE': 'Registered Nurse',
    'RSW': 'Registered Social Worker',
    'REGISTERED SOCIAL WORKER RSW': 'Registered Social Worker',
    'REGISTERED SOCIAL WORKER': 'Registered Social Worker',
    'RL': 'Registered Librarian',
    'REGISTERED LIBRARIAN RL': 'Registered Librarian',
    'REGISTERED LIBRARIAN': 'Registered Librarian',
    'REB': 'Real Estate Broker',
    'REAL ESTATE BROKER REB': 'Real Estate Broker',
    'REAL ESTATE BROKER': 'Real Estate Broker',
    'REA': 'Real Estate Appraiser',
    'REAL ESTATE APPRAISER REA': 'Real Estate Appraiser',
    'REAL ESTATE APPRAISER': 'Real Estate Appraiser',
    'RPM': 'Registered Psychometrician',
    'REGISTERED PSYCHOMETRICIAN RPM': 'Registered Psychometrician',
    'REGISTERED PSYCHOMETRICIAN': 'Registered Psychometrician',
    'RGC': 'Registered Guidance Counselor',
    'RCG': 'Registered Guidance Counselor',
    'REGISTERED GUIDANCE COUNSELOR RGC': 'Registered Guidance Counselor',
    'REGISTERED GUIDANCE COUNSELOR': 'Registered Guidance Counselor',
    'CPA': 'Certified Public Accountant',
    'CERTIFIED PUBLIC ACCOUNTANT CPA': 'Certified Public Accountant',
    'CERTIFIED PUBLIC ACCOUNTANT': 'Certified Public Accountant',
    'PRC': 'Professional Regulation Commission License',
    'PRC LICENSE': 'Professional Regulation Commission License',
    'PROFESSIONAL REGULATION COMMISSION PRC LICENSE':
        'Professional Regulation Commission License',
    'PROFESSIONAL REGULATION COMMISSION LICENSE':
        'Professional Regulation Commission License',
  };
  return descriptions[key] ?? raw;
}

Future<List<String>> licenseNameOptions() async {
  const defaults = <String>[
    'Licensed Professional Teacher',
    'Registered Criminologist',
    'Registered Nurse',
    'Registered Social Worker',
    'Registered Librarian',
    'Real Estate Broker',
    'Real Estate Appraiser',
    'Registered Psychometrician',
    'Registered Guidance Counselor',
    'Certified Public Accountant',
    'Professional Regulation Commission License',
  ];
  final seen = <String>{};
  final out = <String>[];
  void addName(String name) {
    final clean = licenseFullDescription(name);
    if (clean.isEmpty) return;
    final key = clean.toLowerCase();
    if (seen.add(key)) out.add(clean);
  }

  for (final item in defaults) {
    addName(item);
  }
  try {
    final rows = await db
        .from('employee_licenses')
        .select('license_name')
        .order('license_name')
        .limit(3000);
    for (final r in rows) {
      addName('${r['license_name'] ?? ''}');
    }
  } catch (_) {}
  return out;
}

const certificateCategories = <String>[
  'National Certificate I',
  'National Certificate II',
  'National Certificate III',
  'National Certificate IV',
  'Trainer Methodology Certificate I',
  'Trainer Methodology Certificate II',
  'Other Certificates',
];

String certificateCategoryForName(String name) {
  final value = name.trim().toUpperCase();
  if (value.isEmpty) return 'Other Certificates';

  final isTrainerMethodology =
      value.contains('TRAINER METHODOLOGY') ||
      RegExp(r'(^|\s)TM(\s|$)').hasMatch(value);

  if (isTrainerMethodology) {
    if (RegExp(r'(TM\s*II|METHODOLOGY CERTIFICATE\s*II)(?:\s|\)|$)')
        .hasMatch(value)) {
      return 'Trainer Methodology Certificate II';
    }
    return 'Trainer Methodology Certificate I';
  }

  if (RegExp(r'NC\s*IV(?:\s|\)|$)').hasMatch(value)) {
    return 'National Certificate IV';
  }
  if (RegExp(r'NC\s*III(?:\s|\)|$)').hasMatch(value)) {
    return 'National Certificate III';
  }
  if (RegExp(r'NC\s*II(?:\s|\)|$)').hasMatch(value)) {
    return 'National Certificate II';
  }
  if (RegExp(r'NC\s*I(?:\s|\)|$)').hasMatch(value)) {
    return 'National Certificate I';
  }
  return 'Other Certificates';
}

bool isCertificateCategoryLabel(String name) {
  final value = name.trim().toUpperCase();
  return const <String>{
    'NATIONAL CERTIFICATE I (NC I)',
    'NATIONAL CERTIFICATE II (NC II)',
    'NATIONAL CERTIFICATE III (NC III)',
    'NATIONAL CERTIFICATE IV (NC IV)',
    'TRAINER METHODOLOGY CERTIFICATE I (TM I)',
    'TRAINER METHODOLOGY CERTIFICATE II (TM II)',
  }.contains(value);
}

Future<List<String>> certificateNameOptions() async {
  final seen = <String>{};
  final out = <String>[];

  void addName(String name) {
    final clean = name.trim();
    if (clean.isEmpty || isCertificateCategoryLabel(clean)) return;
    final key = clean.toLowerCase();
    if (seen.add(key)) out.add(clean);
  }

  try {
    final rows = await db
        .from('employee_certificates')
        .select('certificate_name')
        .order('certificate_name')
        .limit(3000);
    for (final r in rows) {
      addName('${r['certificate_name'] ?? ''}');
    }
  } catch (_) {}

  out.sort((a, b) {
    final categoryCompare = certificateCategories
        .indexOf(certificateCategoryForName(a))
        .compareTo(certificateCategories.indexOf(certificateCategoryForName(b)));
    return categoryCompare != 0
        ? categoryCompare
        : a.toLowerCase().compareTo(b.toLowerCase());
  });
  return out;
}

Future<Map<String, String>> rankingAppointmentByEmployee() async {
  final rows = await db
      .from('employee_appointments')
      .select('employee_id, category, appointment_title')
      .limit(5000);
  final out = <String, String>{};
  for (final r in rows) {
    final id = r['employee_id']?.toString();
    final category = formatEditValue(r['category']);
    final appointment = formatEditValue(r['appointment_title']);
    if (id != null && id.isNotEmpty && appointment.isNotEmpty) {
      out[id] = category.isEmpty ? appointment : '$category - $appointment';
    }
  }
  return out;
}

Future<List<EditOption>> cycleOptions() async {
  final rows = await db.from('ranking_cycles').select('id, name').order('name');
  return rows
      .map<EditOption>(
          (r) => EditOption(r['id'].toString(), formatValue(r['name'])))
      .toList();
}

Future<List<EditOption>> rankOptions() async {
  try {
    final rows = await db
        .from('ranks')
        .select('name, default_salary')
        .order('sort_order')
        .order('name')
        .limit(500);
    final out = <EditOption>[];
    final seen = <String>{};
    for (final r in rows) {
      final name = formatValue(r['name']);
      final key = normalizeRankKey(name);
      if (key.isEmpty || seen.contains(key)) continue;
      seen.add(key);
      final salary = num.tryParse('${r['default_salary'] ?? ''}');
      final pay = salary == null ? '' : ' - ${formatMoney(salary)}';
      out.add(EditOption(name, '$name$pay', salary: salary));
    }
    return out;
  } catch (_) {
    return const [];
  }
}

String linkedEmployeeName(Map<String, dynamic>? row) {
  if (row?['employees'] is Map)
    return formatValue(row?['employees']['full_name']);
  return 'Linked Employee';
}

Future<bool> ensureNoEmployeeDuplicate(BuildContext context, String tableName,
    Object? employeeId, String moduleName) async {
  if (employeeId == null || employeeId.toString().trim().isEmpty) return true;
  try {
    final existing = await db
        .from(tableName)
        .select('id')
        .eq('employee_id', employeeId)
        .limit(1);
    if (existing.isNotEmpty) {
      showSnack(context,
          'Duplicate prevented: this employee already has a $moduleName record.');
      return false;
    }
    return true;
  } catch (e) {
    showSnack(context, 'Duplicate check failed: $e');
    return false;
  }
}

Future<void> markEmployeeAsResigned(BuildContext context,
    Map<String, dynamic> row, VoidCallback refresh) async {
  final id = row['id'];
  if (id == null) return;
  final ok = await showDialog<bool>(
    context: context,
    builder: (_) => AlertDialog(
      title: const Text('Mark as Resigned?'),
      content: Text(
          'This will mark ${formatValue(row['full_name'])} as resigned and also mark linked contract records as Resigned.'),
      actions: [
        TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: const Text('Cancel')),
        FilledButton.tonalIcon(
          onPressed: () => Navigator.pop(context, true),
          icon: const Icon(Icons.person_off_rounded),
          label: const Text('Mark as Resigned'),
        ),
      ],
    ),
  );
  if (ok != true) return;
  try {
    await db.from('employees').update({
      'employment_status': 'resigned',
      'date_resigned': DateFormat('yyyy-MM-dd').format(DateTime.now()),
    }).eq('id', id);
    await db
        .from('employee_contracts')
        .update({'status': 'Resigned'}).eq('employee_id', id);
    refresh();
    if (context.mounted) showSnack(context, 'Employee marked as resigned.');
  } catch (e) {
    if (context.mounted) showSnack(context, 'Mark as resigned failed: $e');
  }
}

bool employeeRowIsResignedForAction(Map<String, dynamic> row) =>
    formatValue(row['employment_status']).toLowerCase().contains('resign') ||
    formatValue(row['status']).toLowerCase().contains('resign');

Widget? employeeResignRowAction(
    BuildContext context, Map<String, dynamic> row, VoidCallback refresh) {
  if (employeeRowIsResignedForAction(row)) return null;
  return IconButton(
    tooltip: 'Mark as Resigned',
    onPressed: () => markEmployeeAsResigned(context, row, refresh),
    icon: const Icon(Icons.person_off_rounded, color: _danger, size: 19),
  );
}

Future<void> editEmployee(BuildContext context, Map<String, dynamic>? row,
    VoidCallback refresh) async {
  final normalized = normalizeRow(row ?? {});
  final data = await showRecordDialog(
    context,
    row == null ? 'Add Employee' : 'Edit Employee',
    employeeEditFields(),
    normalized,
  );
  if (data == null) return;
  data['name_key'] = normalizeName(data['full_name']?.toString() ?? '');
  data['date_hired'] ??= data['starting_date'];
  data['starting_date'] ??= data['date_hired'];
  await saveRow(context, 'employees', row?['id'], data, refresh);
}

const _contractTypeOptions = <EditOption>[
  EditOption('Full-time', 'Full-time'),
  EditOption('Full-time-Probationary', 'Full-time-Probationary'),
  EditOption('Part-time', 'Part-time'),
  EditOption('Probationary', 'Probationary'),
  EditOption('Compliance', 'Compliance'),
];

class UploadedAttachment {
  final String url;
  final String fileName;
  const UploadedAttachment(this.url, this.fileName);
}

Future<List<EditOption>> contractTypeOptions() async {
  final rows =
      await db.from('employee_contracts').select('contract_type').limit(5000);
  final out = <EditOption>[];
  final seen = <String>{};

  void addType(Object? raw) {
    final value = '${raw ?? ''}'.trim();
    if (value.isEmpty || value == '-') return;
    if (seen.add(value.toLowerCase())) out.add(EditOption(value, value));
  }

  for (final option in _contractTypeOptions) {
    addType(option.value);
  }
  for (final item in rows) {
    if (item is Map) addType(item['contract_type']);
  }
  out.sort((a, b) => a.label.toLowerCase().compareTo(b.label.toLowerCase()));
  return out;
}

String contractDateText(Object? value) {
  final parsed = parseFlexibleDate(value);
  if (parsed == null) return '';
  return DateFormat('MMMM dd, yyyy').format(parsed);
}

DateTime addContractMonths(DateTime start, int months) {
  final monthIndex = start.month + months - 1;
  final year = start.year + (monthIndex ~/ 12);
  final month = (monthIndex % 12) + 1;
  final lastDay = DateTime(year, month + 1, 0).day;
  final day = start.day > lastDay ? lastDay : start.day;
  return DateTime(year, month, day);
}

String contractStatusFromEndDate(Object? value) {
  final parsed = parseFlexibleDate(value);
  if (parsed == null) return '';
  final now = DateTime.now();
  final today = DateTime(now.year, now.month, now.day);
  final end = DateTime(parsed.year, parsed.month, parsed.day);
  final days = end.difference(today).inDays;
  if (days < 0) return 'Expired';
  if (days <= 90) return 'For Renewal';
  return 'On-going';
}

const appointmentCategoryOptions = <EditOption>[
  EditOption('FULL-TIME', 'FULL-TIME'),
  EditOption('PART-TIME', 'PART-TIME'),
  EditOption('PROBATIONARY', 'PROBATIONARY'),
  EditOption('COMPLIANCE', 'COMPLIANCE'),
];

const appointmentTypeOptions = <EditOption>[
  EditOption('PACUCOA', 'PACUCOA'),
  EditOption('RQUAT (CHED)', 'RQUAT (CHED)'),
  EditOption('INSTITUTION', 'INSTITUTION'),
  EditOption('BASIC ED', 'BASIC ED'),
  EditOption('ESC', 'ESC'),
  EditOption('DEPED', 'DEPED'),
  EditOption('PEAC', 'PEAC'),
];

Widget searchableOptionBox(String label, TextEditingController controller,
        List<EditOption> options,
        {double width = 354}) =>
    SizedBox(
      width: width,
      child: Autocomplete<EditOption>(
        initialValue: TextEditingValue(text: controller.text),
        displayStringForOption: (option) => option.label,
        optionsBuilder: (value) {
          final q = value.text.trim().toLowerCase();
          final list = uniqueOptions(options).toList()
            ..sort((a, b) => a.label.compareTo(b.label));
          if (q.isEmpty) return list;
          return list.where((x) =>
              x.label.toLowerCase().contains(q) ||
              x.value.toLowerCase().contains(q));
        },
        onSelected: (option) => controller.text = option.value,
        fieldViewBuilder: (context, textController, focusNode, _) =>
            TextFormField(
          controller: textController,
          focusNode: focusNode,
          decoration: InputDecoration(
              labelText: label,
              hintText: 'Select or type $label',
              suffixIcon: const Icon(Icons.search_rounded)),
          validator: (v) => v == null || v.trim().isEmpty ? 'Required' : null,
          onChanged: (v) => controller.text = v,
        ),
      ),
    );

Future<UploadedAttachment?> pickAndUploadAppointmentPdf(
    BuildContext context) async {
  final file = await pickPdfFileOrNull();
  if (file == null) return null;
  if (!file.name.toLowerCase().endsWith('.pdf') &&
      file.type != 'application/pdf') {
    showSnack(context, 'Only PDF files are allowed.');
    return null;
  }
  try {
    final reader = html.FileReader();
    reader.readAsArrayBuffer(file);
    await reader.onLoad.first;
    final result = reader.result;
    final bytes =
        result is ByteBuffer ? Uint8List.view(result) : result as Uint8List;
    final safeName = file.name.replaceAll(RegExp(r'[^A-Za-z0-9._-]+'), '_');
    final uploadPath =
        'appointments/${DateTime.now().millisecondsSinceEpoch}_$safeName';
    await db.storage.from('hr-attachments').uploadBinary(uploadPath, bytes,
        fileOptions:
            const FileOptions(contentType: 'application/pdf', upsert: true));
    return UploadedAttachment(
        db.storage.from('hr-attachments').getPublicUrl(uploadPath), file.name);
  } catch (e) {
    showSnack(context, 'Appointment PDF upload failed: $e');
    return null;
  }
}

Future<html.File?> pickPdfFileOrNull() async {
  final input = html.FileUploadInputElement()
    ..accept = 'application/pdf,.pdf'
    ..multiple = false;
  input.click();
  await Future.any<dynamic>([
    input.onChange.first,
    input.on['cancel'].first,
    Future.delayed(const Duration(seconds: 30), () => html.Event('timeout')),
  ]);
  return input.files?.isNotEmpty == true ? input.files!.first : null;
}

Future<UploadedAttachment?> pickAndUploadContractPdf(
    BuildContext context) async {
  final file = await pickPdfFileOrNull();
  if (file == null) return null;

  final lowerName = file.name.toLowerCase();
  if (!lowerName.endsWith('.pdf') && file.type != 'application/pdf') {
    showSnack(context, 'Only PDF files are allowed.');
    return null;
  }

  try {
    final reader = html.FileReader();
    reader.readAsArrayBuffer(file);
    await reader.onLoad.first;
    final result = reader.result;
    late final Uint8List bytes;
    if (result is ByteBuffer) {
      bytes = Uint8List.view(result);
    } else if (result is Uint8List) {
      bytes = result;
    } else {
      throw Exception('Unable to read selected PDF file.');
    }

    final safeName = file.name.replaceAll(RegExp(r'[^A-Za-z0-9._-]+'), '_');
    final path = 'contracts/${DateTime.now().millisecondsSinceEpoch}_$safeName';
    await db.storage.from('hr-attachments').uploadBinary(path, bytes,
        fileOptions:
            const FileOptions(contentType: 'application/pdf', upsert: true));
    final url = db.storage.from('hr-attachments').getPublicUrl(path);
    return UploadedAttachment(url, file.name);
  } catch (e) {
    showSnack(context, 'PDF upload failed: $e');
    return null;
  }
}

Future<UploadedAttachment?> pickAndUploadEducationPdf(
    BuildContext context) async {
  final file = await pickPdfFileOrNull();
  if (file == null) return null;

  final lowerName = file.name.toLowerCase();
  if (!lowerName.endsWith('.pdf') && file.type != 'application/pdf') {
    showSnack(context, 'Only PDF files are allowed.');
    return null;
  }

  try {
    final reader = html.FileReader();
    reader.readAsArrayBuffer(file);
    await reader.onLoad.first;
    final result = reader.result;
    late final Uint8List bytes;
    if (result is ByteBuffer) {
      bytes = Uint8List.view(result);
    } else if (result is Uint8List) {
      bytes = result;
    } else {
      throw Exception('Unable to read selected PDF file.');
    }

    final safeName = file.name.replaceAll(RegExp(r'[^A-Za-z0-9._-]+'), '_');
    final uploadPath =
        'education/${DateTime.now().millisecondsSinceEpoch}_$safeName';
    await db.storage.from('hr-attachments').uploadBinary(uploadPath, bytes,
        fileOptions:
            const FileOptions(contentType: 'application/pdf', upsert: true));
    final url = db.storage.from('hr-attachments').getPublicUrl(uploadPath);
    return UploadedAttachment(url, file.name);
  } catch (e) {
    showSnack(context, 'Education PDF upload failed: $e');
    return null;
  }
}

Widget contractTypeAutocompleteBox(
        TextEditingController controller, List<EditOption> options) =>
    SizedBox(
      width: 354,
      child: Autocomplete<EditOption>(
        initialValue: TextEditingValue(text: controller.text),
        displayStringForOption: (option) => option.label,
        optionsBuilder: (textEditingValue) {
          final sorted = uniqueOptions(options).toList()
            ..sort((a, b) =>
                a.label.toLowerCase().compareTo(b.label.toLowerCase()));
          final query = textEditingValue.text.trim().toLowerCase();
          if (query.isEmpty) return sorted;
          final normalizedQuery = normalizeName(query);
          return sorted.where((option) {
            final label = option.label.toLowerCase();
            final normalizedLabel = normalizeName(option.label);
            return label.contains(query) ||
                normalizedLabel.contains(normalizedQuery);
          });
        },
        onSelected: (option) => controller.text = option.value,
        fieldViewBuilder:
            (context, textController, focusNode, onFieldSubmitted) =>
                TextFormField(
          controller: textController,
          focusNode: focusNode,
          decoration: const InputDecoration(
            labelText: 'Contract Type',
            hintText: 'Select or type contract type',
            suffixIcon: Icon(Icons.search_rounded),
          ),
          validator: (value) =>
              value == null || value.trim().isEmpty ? 'Required' : null,
          onChanged: (value) => controller.text = value,
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

Widget contractDatePickerBox(
        BuildContext context,
        TextEditingController controller,
        StateSetter setDialogState,
        VoidCallback recomputeContract) =>
    SizedBox(
      width: 354,
      child: TextFormField(
        controller: controller,
        readOnly: false,
        keyboardType: TextInputType.datetime,
        inputFormatters: [DateSlashInputFormatter()],
        decoration: const InputDecoration(
          labelText: 'Start Date',
          hintText: 'MM/DD/YYYY',
          suffixIcon: Icon(Icons.calendar_month_rounded),
        ),
        validator: (value) {
          if (value == null || value.trim().isEmpty) return 'Required';
          if (parseFlexibleDate(value.trim()) == null) return 'Invalid date';
          return null;
        },
        onFieldSubmitted: (_) => setDialogState(recomputeContract),
      ),
    );

Widget contractReadOnlyBox(String label, TextEditingController controller,
        {IconData? icon}) =>
    SizedBox(
      width: 354,
      child: TextFormField(
        controller: controller,
        readOnly: true,
        style: const TextStyle(color: _muted, fontWeight: FontWeight.w800),
        decoration: InputDecoration(
            labelText: label,
            fillColor: _surfaceSoft,
            suffixIcon: icon == null ? null : Icon(icon)),
      ),
    );

Future<Map<String, dynamic>?> showContractDialog(
    BuildContext context,
    List<EditOption> employees,
    List<EditOption> contractTypes,
    Map<String, dynamic>? initial) async {
  final isAdd = initial == null;
  final formKey = GlobalKey<FormState>();
  String? employeeId = isAdd ? null : initial?['employee_id']?.toString();
  String selectedEmployeeName = isAdd ? '' : linkedEmployeeName(initial);
  final contractType =
      TextEditingController(text: formatEditValue(initial?['contract_type']));
  final startDate = TextEditingController(
      text: contractDateText(initial?['contract_start_date']));
  final durationMonths =
      TextEditingController(text: formatEditValue(initial?['duration_months']));
  final endDate = TextEditingController(
      text: contractDateText(initial?['contract_end_date']));
  final status =
      TextEditingController(text: formatEditValue(initial?['status']));
  String attachmentUrl = formatEditValue(initial?['attachment_url']);
  String attachmentFileName = attachmentUrl.isEmpty || attachmentUrl == '-'
      ? ''
      : Uri.decodeFull(attachmentUrl.split('/').last.split('?').first);
  bool uploadingAttachment = false;

  void recomputeContract() {
    final start = parseFlexibleDate(startDate.text);
    final months = int.tryParse(durationMonths.text.trim());
    if (start != null && months != null && months > 0) {
      final computedEnd = addContractMonths(
          DateTime(start.year, start.month, start.day), months);
      endDate.text = DateFormat('MM/dd/yyyy').format(computedEnd);
    }
    status.text = contractStatusFromEndDate(endDate.text);
  }

  if (endDate.text.isEmpty) {
    recomputeContract();
  } else {
    status.text = contractStatusFromEndDate(endDate.text);
  }

  final result = await showDialog<Map<String, dynamic>>(
    context: context,
    builder: (_) => StatefulBuilder(
      builder: (context, setDialogState) => AlertDialog(
        title: Text(isAdd ? 'Add Contract' : 'Edit Contract'),
        content: SizedBox(
          width: 760,
          child: Form(
            key: formKey,
            child: SingleChildScrollView(
              child: Wrap(spacing: 14, runSpacing: 14, children: [
                if (isAdd)
                  SizedBox(
                    width: 354,
                    child: Autocomplete<EditOption>(
                      displayStringForOption: (option) => option.label,
                      optionsBuilder: (textEditingValue) {
                        final sortedEmployees = uniqueOptions(employees)
                            .toList()
                          ..sort((a, b) => a.label
                              .toLowerCase()
                              .compareTo(b.label.toLowerCase()));
                        final query =
                            textEditingValue.text.trim().toLowerCase();
                        if (query.isEmpty) return sortedEmployees;
                        final normalizedQuery = normalizeName(query);
                        return sortedEmployees.where((option) {
                          final label = option.label.toLowerCase();
                          final normalizedLabel = normalizeName(option.label);
                          return label.contains(query) ||
                              normalizedLabel.contains(normalizedQuery);
                        });
                      },
                      onSelected: (option) => setDialogState(() {
                        employeeId = option.value;
                        selectedEmployeeName = option.label;
                      }),
                      fieldViewBuilder: (context, textController, focusNode,
                              onFieldSubmitted) =>
                          TextFormField(
                        controller: textController,
                        focusNode: focusNode,
                        decoration: const InputDecoration(
                          labelText: 'Employee Name',
                          hintText: 'Select or type employee name',
                          suffixIcon: Icon(Icons.search_rounded),
                        ),
                        validator: (_) =>
                            employeeId == null || employeeId!.isEmpty
                                ? 'Please select employee from the list'
                                : null,
                        onChanged: (value) => setDialogState(() {
                          final typed = value.trim().toLowerCase();
                          final exact = uniqueOptions(employees)
                              .where((option) =>
                                  option.label.toLowerCase() == typed)
                              .toList();
                          if (exact.isNotEmpty) {
                            employeeId = exact.first.value;
                            selectedEmployeeName = exact.first.label;
                          } else {
                            employeeId = null;
                            selectedEmployeeName = '';
                          }
                        }),
                      ),
                      optionsViewBuilder: (context, onSelected, options) =>
                          Align(
                        alignment: Alignment.topLeft,
                        child: Material(
                          elevation: 6,
                          borderRadius: BorderRadius.circular(14),
                          child: ConstrainedBox(
                            constraints: const BoxConstraints(
                                maxWidth: 520, maxHeight: 320),
                            child: ListView.separated(
                              padding: EdgeInsets.zero,
                              shrinkWrap: true,
                              itemCount: options.length,
                              separatorBuilder: (_, __) =>
                                  const Divider(height: 1),
                              itemBuilder: (context, index) {
                                final option = options.elementAt(index);
                                return ListTile(
                                  dense: true,
                                  title: Text(option.label,
                                      overflow: TextOverflow.ellipsis),
                                  onTap: () => onSelected(option),
                                );
                              },
                            ),
                          ),
                        ),
                      ),
                    ),
                  )
                else
                  ReadOnlyEmployeeBox(linkedEmployeeName(initial)),
                contractTypeAutocompleteBox(contractType, contractTypes),
                contractDatePickerBox(
                    context, startDate, setDialogState, recomputeContract),
                SizedBox(
                  width: 354,
                  child: TextFormField(
                    controller: durationMonths,
                    keyboardType: TextInputType.number,
                    decoration:
                        const InputDecoration(labelText: 'Duration In Months'),
                    validator: (value) {
                      final months = int.tryParse('${value ?? ''}'.trim());
                      if (months == null || months <= 0)
                        return 'Enter valid months';
                      return null;
                    },
                    onChanged: (_) => setDialogState(recomputeContract),
                  ),
                ),
                contractReadOnlyBox('End Date', endDate,
                    icon: Icons.event_available_rounded),
                contractReadOnlyBox('Status', status,
                    icon: Icons.verified_rounded),
                SizedBox(
                  width: 728,
                  child: Container(
                    padding: const EdgeInsets.all(14),
                    decoration: BoxDecoration(
                        color: Colors.white,
                        borderRadius: BorderRadius.circular(18),
                        border: Border.all(color: _line)),
                    child: Row(children: [
                      const Icon(Icons.picture_as_pdf_rounded, color: _danger),
                      const SizedBox(width: 12),
                      Expanded(
                        child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              const Text('Attach File (Upload PDF)',
                                  style: TextStyle(
                                      color: Color(0xFF1E40AF),
                                      fontWeight: FontWeight.w700,
                                      fontSize: 12)),
                              const SizedBox(height: 4),
                              Text(
                                attachmentFileName.isEmpty
                                    ? 'No PDF attached'
                                    : attachmentFileName,
                                overflow: TextOverflow.ellipsis,
                                style: TextStyle(
                                    color: attachmentFileName.isEmpty
                                        ? _muted
                                        : _ink,
                                    fontWeight: FontWeight.w800),
                              ),
                            ]),
                      ),
                      const SizedBox(width: 12),
                      OutlinedButton.icon(
                        onPressed: uploadingAttachment
                            ? null
                            : () async {
                                setDialogState(
                                    () => uploadingAttachment = true);
                                final uploaded =
                                    await pickAndUploadContractPdf(context);
                                if (!context.mounted) return;
                                setDialogState(() {
                                  if (uploaded != null) {
                                    attachmentUrl = uploaded.url;
                                    attachmentFileName = uploaded.fileName;
                                  }
                                  uploadingAttachment = false;
                                });
                              },
                        icon: uploadingAttachment
                            ? const SizedBox(
                                width: 16,
                                height: 16,
                                child:
                                    CircularProgressIndicator(strokeWidth: 2))
                            : const Icon(Icons.upload_file_rounded),
                        label: Text(uploadingAttachment
                            ? 'Uploading...'
                            : 'Upload PDF'),
                      ),
                    ]),
                  ),
                ),
                SizedBox(
                  width: 728,
                  child: Container(
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                        color: const Color(0xFFEFF6FF),
                        borderRadius: BorderRadius.circular(16)),
                    child: const Text(
                        'Select an employee, choose the contract type, pick the start date, then enter the duration in months. End Date and Status are automatically computed from those values.',
                        style: TextStyle(
                            color: Color(0xFF1E3A8A),
                            fontWeight: FontWeight.w600)),
                  ),
                ),
              ]),
            ),
          ),
        ),
        actions: [
          TextButton(
              onPressed: () => Navigator.pop(context),
              child: const Text('Cancel')),
          FilledButton(
            onPressed: uploadingAttachment
                ? null
                : () {
                    recomputeContract();
                    if (!formKey.currentState!.validate()) return;
                    FocusManager.instance.primaryFocus?.unfocus();
                    Navigator.of(context, rootNavigator: true).pop({
                      'employee_id': isAdd
                          ? emptyToNull(employeeId)
                          : initial?['employee_id'],
                      'contract_type': emptyToNull(contractType.text),
                      'contract_start_date': toIsoDateInput(startDate.text),
                      'duration_months':
                          int.tryParse(durationMonths.text.trim()),
                      'contract_end_date': toIsoDateInput(endDate.text),
                      'attachment_url': emptyToNull(attachmentUrl),
                      'status': emptyToNull(status.text),
                    });
                  },
            child: const Text('Save'),
          ),
        ],
      ),
    ),
  );

  for (final c in [contractType, startDate, durationMonths, endDate, status]) {
    c.dispose();
  }
  return result;
}

Future<void> viewContract(
    BuildContext context, Map<String, dynamic> row) async {
  final normalized = normalizeRow(row);
  await showDialog<void>(
    context: context,
    builder: (_) => AlertDialog(
      title: Text(
          'Contract Details - ${formatValue(normalized['employee_name'])}'),
      content: SizedBox(
        width: 820,
        child: SingleChildScrollView(
          child: Wrap(spacing: 10, runSpacing: 10, children: [
            DetailTile(
                'Employee Name', formatValue(normalized['employee_name'])),
            DetailTile(
                'Contract Type', formatValue(normalized['contract_type'])),
            DetailTile('Status', formatValue(normalized['status'])),
            DetailTile(
                'Start Date', formatValue(normalized['contract_start_date'])),
            DetailTile(
                'Duration Months', formatValue(normalized['duration_months'])),
            DetailTile(
                'End Date', formatValue(normalized['contract_end_date'])),
            DetailTile('Days Left', formatValue(normalized['days_left'])),
            AttachmentPdfTile('Contract PDF', normalized['attachment_url']),
          ]),
        ),
      ),
      actions: [
        TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Close')),
      ],
    ),
  );
}

Future<void> editContract(BuildContext context, Map<String, dynamic>? row,
    VoidCallback refresh) async {
  final isAdd = row == null;
  final employees = isAdd ? await employeeOptions() : const <EditOption>[];
  final types = await contractTypeOptions();
  final data = await showContractDialog(
      context, employees, types, row == null ? null : normalizeRow(row));
  if (data == null) return;
  if (isAdd &&
      !await ensureNoEmployeeDuplicate(
          context, 'employee_contracts', data['employee_id'], 'contract'))
    return;
  await saveRow(context, 'employee_contracts', row?['id'], data, refresh);
}

class SelectedLicenseInput {
  final String name;
  final TextEditingController number = TextEditingController();
  final TextEditingController expiry = TextEditingController();
  final TextEditingController attachment = TextEditingController();
  String attachmentUrl = '';
  String attachmentFileName = '';
  bool uploadingAttachment = false;
  String status = '';

  SelectedLicenseInput(this.name);

  void dispose() {
    number.dispose();
    expiry.dispose();
    attachment.dispose();
  }
}

String licenseStatusFromExpiry(String text) {
  final value = text.trim();
  if (value.isEmpty) return '';
  final parsed = parseFlexibleDate(value);
  if (parsed == null) return '';
  final todayNow = DateTime.now();
  final today = DateTime(todayNow.year, todayNow.month, todayNow.day);
  final expiry = DateTime(parsed.year, parsed.month, parsed.day);
  if (expiry.isBefore(today)) return 'Expired';
  if (expiry.difference(today).inDays <= 90) return 'For Renewal';
  return 'Active';
}

Future<void> pickAndUploadLicensePdf(BuildContext context,
    SelectedLicenseInput entry, StateSetter setDialogState) async {
  final file = await pickPdfFileOrNull();
  if (file == null) return;
  final lowerName = file.name.toLowerCase();
  if (!lowerName.endsWith('.pdf') && file.type != 'application/pdf') {
    showSnack(context, 'Only PDF files are allowed.');
    return;
  }
  setDialogState(() => entry.uploadingAttachment = true);
  try {
    final reader = html.FileReader();
    reader.readAsArrayBuffer(file);
    await reader.onLoad.first;
    final result = reader.result;
    late final Uint8List bytes;
    if (result is ByteBuffer) {
      bytes = Uint8List.view(result);
    } else if (result is Uint8List) {
      bytes = result;
    } else {
      throw Exception('Unable to read selected PDF file.');
    }
    final safeName = file.name.replaceAll(RegExp(r'[^A-Za-z0-9._-]+'), '_');
    final path = 'licenses/${DateTime.now().millisecondsSinceEpoch}_$safeName';
    await db.storage.from('hr-attachments').uploadBinary(path, bytes,
        fileOptions:
            const FileOptions(contentType: 'application/pdf', upsert: true));
    final url = db.storage.from('hr-attachments').getPublicUrl(path);
    setDialogState(() {
      entry.attachmentUrl = url;
      entry.attachmentFileName = file.name;
      entry.uploadingAttachment = false;
    });
  } catch (e) {
    setDialogState(() => entry.uploadingAttachment = false);
    showSnack(context, 'PDF upload failed: $e');
  }
}

Future<List<Map<String, dynamic>>?> showAddLicenseDialog(BuildContext context,
    List<EditOption> employees, List<String> licenses) async {
  final formKey = GlobalKey<FormState>();
  String? employeeId;
  final selected = <String, SelectedLicenseInput>{};

  final result = await showDialog<List<Map<String, dynamic>>>(
    context: context,
    builder: (_) => StatefulBuilder(
      builder: (context, setDialogState) => AlertDialog(
        title: const Text('Add License'),
        content: SizedBox(
          width: 1040,
          child: Form(
            key: formKey,
            child: SingleChildScrollView(
              child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const DialogSectionTitle('Employee Information', width: double.infinity),
                    employeeAutocompleteField(
                      employees: employees,
                      employeeId: employeeId,
                      width: 1016,
                      onEmployeeChanged: (value) =>
                          setDialogState(() => employeeId = value),
                    ),
                    const SizedBox(height: 20),
                    const DialogSectionTitle('License Checklist', width: double.infinity),
                    Wrap(
                      spacing: 10,
                      runSpacing: 10,
                      children: [
                        for (final license in licenses)
                          Container(
                            width: 328,
                            constraints: const BoxConstraints(minHeight: 72),
                            padding: const EdgeInsets.symmetric(
                                horizontal: 8, vertical: 6),
                            decoration: BoxDecoration(
                              color: _surfaceSoft,
                              borderRadius: BorderRadius.circular(14),
                              border: Border.all(color: _line),
                            ),
                            child: CheckboxListTile(
                              dense: false,
                              contentPadding:
                                  const EdgeInsets.symmetric(horizontal: 4),
                              visualDensity: VisualDensity.compact,
                              controlAffinity: ListTileControlAffinity.leading,
                              title: Text(licenseFullDescription(license),
                                  maxLines: 3,
                                  softWrap: true,
                                  style: const TextStyle(
                                      fontSize: 13,
                                      height: 1.25,
                                      fontWeight: FontWeight.w700,
                                      color: _ink)),
                              value: selected.containsKey(license),
                              onChanged: (checked) => setDialogState(() {
                                if (checked == true) {
                                  selected.putIfAbsent(license,
                                      () => SelectedLicenseInput(license));
                                } else {
                                  selected.remove(license)?.dispose();
                                }
                              }),
                            ),
                          ),
                      ],
                    ),
                    const SizedBox(height: 20),
                    const DialogSectionTitle('Selected Licenses', width: double.infinity),
                    if (selected.isEmpty)
                      Container(
                        width: double.infinity,
                        padding: const EdgeInsets.all(14),
                        decoration: BoxDecoration(
                            color: const Color(0xFFF8FAFC),
                            borderRadius: BorderRadius.circular(14),
                            border: Border.all(color: _line)),
                        child: const Text(
                            'Select one or more licenses above. The selected licenses will appear here as a table.',
                            style: TextStyle(
                                color: _muted, fontWeight: FontWeight.w700)),
                      )
                    else
                      Container(
                        width: double.infinity,
                        decoration: BoxDecoration(
                            color: Colors.white,
                            borderRadius: BorderRadius.circular(18),
                            border: Border.all(color: _line)),
                        child: Column(children: [
                          Container(
                            padding: const EdgeInsets.symmetric(
                                horizontal: 12, vertical: 10),
                            decoration: const BoxDecoration(
                                color: Color(0xFFF8FAFC),
                                borderRadius: BorderRadius.vertical(
                                    top: Radius.circular(16))),
                            child: const Row(children: [
                              Expanded(
                                  flex: 3,
                                  child: Text('License Name',
                                      style: TextStyle(
                                          fontWeight: FontWeight.w900,
                                          color: _ink))),
                              SizedBox(width: 10),
                              Expanded(
                                  flex: 2,
                                  child: Text('License Number',
                                      style: TextStyle(
                                          fontWeight: FontWeight.w900,
                                          color: _ink))),
                              SizedBox(width: 10),
                              Expanded(
                                  flex: 2,
                                  child: Text('Expiry Date',
                                      style: TextStyle(
                                          fontWeight: FontWeight.w900,
                                          color: _ink))),
                              SizedBox(width: 10),
                              Expanded(
                                  flex: 2,
                                  child: Text('Attachment (PDF)',
                                      style: TextStyle(
                                          fontWeight: FontWeight.w900,
                                          color: _ink))),
                              SizedBox(width: 10),
                              SizedBox(
                                  width: 130,
                                  child: Text('Status',
                                      style: TextStyle(
                                          fontWeight: FontWeight.w900,
                                          color: _ink))),
                            ]),
                          ),
                          for (final entry in selected.values)
                            Padding(
                              padding: const EdgeInsets.symmetric(
                                  horizontal: 12, vertical: 8),
                              child: Row(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    Expanded(
                                        flex: 3,
                                        child: Padding(
                                            padding:
                                                const EdgeInsets.only(top: 14),
                                            child: Text(entry.name,
                                                style: const TextStyle(
                                                    fontWeight: FontWeight.w800,
                                                    color: _ink)))),
                                    const SizedBox(width: 10),
                                    Expanded(
                                      flex: 2,
                                      child: TextFormField(
                                        controller: entry.number,
                                        decoration: const InputDecoration(
                                            labelText: 'License Number'),
                                        validator: (v) =>
                                            v == null || v.trim().isEmpty
                                                ? 'Required'
                                                : null,
                                      ),
                                    ),
                                    const SizedBox(width: 10),
                                    Expanded(
                                      flex: 2,
                                      child: TextFormField(
                                        controller: entry.expiry,
                                        decoration: const InputDecoration(
                                            labelText: 'Expiry Date',
                                            hintText: 'MM/DD/YYYY'),
                                        validator: (v) {
                                          if (v == null || v.trim().isEmpty)
                                            return 'Required';
                                          if (parseFlexibleDate(v.trim()) ==
                                              null)
                                            return 'Use January 02, 2026';
                                          return null;
                                        },
                                        onChanged: (v) => setDialogState(() =>
                                            entry.status =
                                                licenseStatusFromExpiry(v)),
                                      ),
                                    ),
                                    const SizedBox(width: 10),
                                    Expanded(
                                      flex: 2,
                                      child: Column(
                                          crossAxisAlignment:
                                              CrossAxisAlignment.start,
                                          children: [
                                            OutlinedButton.icon(
                                              onPressed: entry
                                                      .uploadingAttachment
                                                  ? null
                                                  : () =>
                                                      pickAndUploadLicensePdf(
                                                          context,
                                                          entry,
                                                          setDialogState),
                                              icon: entry.uploadingAttachment
                                                  ? const SizedBox(
                                                      width: 16,
                                                      height: 16,
                                                      child:
                                                          CircularProgressIndicator(
                                                              strokeWidth: 2))
                                                  : const Icon(Icons
                                                      .picture_as_pdf_rounded),
                                              label: Text(entry
                                                      .uploadingAttachment
                                                  ? 'Uploading...'
                                                  : (entry.attachmentFileName
                                                          .isEmpty
                                                      ? 'Attach PDF'
                                                      : 'Change PDF')),
                                            ),
                                            const SizedBox(height: 6),
                                            Text(
                                              entry.attachmentFileName.isEmpty
                                                  ? 'No PDF attached'
                                                  : entry.attachmentFileName,
                                              maxLines: 2,
                                              overflow: TextOverflow.ellipsis,
                                              style: TextStyle(
                                                  fontSize: 12,
                                                  color: entry
                                                          .attachmentFileName
                                                          .isEmpty
                                                      ? _muted
                                                      : _ink,
                                                  fontWeight: FontWeight.w700),
                                            ),
                                          ]),
                                    ),
                                    const SizedBox(width: 10),
                                    SizedBox(
                                        width: 130,
                                        child: Padding(
                                            padding:
                                                const EdgeInsets.only(top: 10),
                                            child: StatusChip(
                                                entry.status.isEmpty
                                                    ? '-'
                                                    : entry.status))),
                                  ]),
                            ),
                        ]),
                      ),
                  ]),
            ),
          ),
        ),
        actions: [
          TextButton(
              onPressed: () => Navigator.pop(context),
              child: const Text('Cancel')),
          FilledButton(
            onPressed: () {
              if (!formKey.currentState!.validate()) return;
              if (selected.isEmpty) {
                showSnack(context, 'Please select at least one license.');
                return;
              }
              final missingPdf = selected.values
                  .where((entry) => entry.attachmentUrl.trim().isEmpty)
                  .toList();
              if (missingPdf.isNotEmpty) {
                showSnack(context,
                    'Please attach a PDF file for every selected license.');
                return;
              }
              final now = DateTime.now().toIso8601String();
              Navigator.pop(
                  context,
                  selected.values.map((entry) {
                    final status = licenseStatusFromExpiry(entry.expiry.text);
                    return <String, dynamic>{
                      'employee_id': employeeId,
                      'license_name': entry.name,
                      'license_number': entry.number.text.trim(),
                      'expiry_date': toIsoDateInput(entry.expiry.text),
                      'attachment_url': entry.attachmentUrl.trim().isEmpty
                          ? null
                          : entry.attachmentUrl.trim(),
                      'status': status.isEmpty ? null : status,
                      'updated_at': now,
                    };
                  }).toList());
            },
            child: const Text('Save'),
          ),
        ],
      ),
    ),
  );

  for (final item in selected.values) {
    item.dispose();
  }
  return result;
}

Future<List<Map<String, dynamic>>?> showEditLicenseGroupDialog(
    BuildContext context,
    Map<String, dynamic> row,
    List<String> licenseNames) async {
  final records = (row['license_records'] is List)
      ? List<Map<String, dynamic>>.from(row['license_records'] as List)
      : <Map<String, dynamic>>[row];
  final employeeId =
      '${row['employee_id'] ?? (records.isNotEmpty ? records.first['employee_id'] : '')}';
  final employeeName = formatValue(row['employee_name']);
  final formKey = GlobalKey<FormState>();
  final selected = <String, SelectedLicenseInput>{};
  for (final rec in records) {
    final name = formatValue(rec['license_name']);
    if (name == '-' || name.trim().isEmpty) continue;
    final entry = SelectedLicenseInput(name);
    entry.number.text = formatEditValue(rec['license_number']);
    entry.expiry.text = formatEditValue(rec['expiry_date']);
    entry.attachmentUrl = formatEditValue(rec['attachment_url']);
    entry.attachmentFileName =
        entry.attachmentUrl.isEmpty ? '' : entry.attachmentUrl.split('/').last;
    entry.status = formatEditValue(rec['status']).isEmpty
        ? licenseStatusFromExpiry(entry.expiry.text)
        : formatEditValue(rec['status']);
    entry.attachment.text = entry.attachmentUrl;
    selected[name] = entry;
  }
  final allNames = <String>{...licenseNames, ...selected.keys}.toList()
    ..sort((a, b) => a.toLowerCase().compareTo(b.toLowerCase()));

  final result = await showDialog<List<Map<String, dynamic>>>(
    context: context,
    builder: (_) => StatefulBuilder(
      builder: (context, setDialogState) => AlertDialog(
        title: const Text('Edit License'),
        content: SizedBox(
          width: 790,
          child: Form(
            key: formKey,
            child: SingleChildScrollView(
              child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const DialogSectionTitle('Employee Information'),
                    ReadOnlyEmployeeBox(employeeName == '-'
                        ? linkedEmployeeName(row)
                        : employeeName),
                    const SizedBox(height: 16),
                    const DialogSectionTitle('License Information'),
                    Wrap(spacing: 10, runSpacing: 8, children: [
                      for (final license in allNames)
                        SizedBox(
                          width: 228,
                          child: CheckboxListTile(
                            dense: true,
                            contentPadding: EdgeInsets.zero,
                            controlAffinity: ListTileControlAffinity.leading,
                            title: Text(license,
                                maxLines: 2,
                                overflow: TextOverflow.ellipsis,
                                style: const TextStyle(
                                    fontSize: 13,
                                    fontWeight: FontWeight.w700,
                                    color: _ink)),
                            value: selected.containsKey(license),
                            onChanged: (checked) => setDialogState(() {
                              if (checked == true) {
                                selected.putIfAbsent(license,
                                    () => SelectedLicenseInput(license));
                              } else {
                                selected.remove(license)?.dispose();
                              }
                            }),
                          ),
                        ),
                    ]),
                    const SizedBox(height: 12),
                    if (selected.isEmpty)
                      Container(
                        width: 728,
                        padding: const EdgeInsets.all(14),
                        decoration: BoxDecoration(
                            color: const Color(0xFFF8FAFC),
                            borderRadius: BorderRadius.circular(14),
                            border: Border.all(color: _line)),
                        child: const Text('Select one or more licenses above.',
                            style: TextStyle(
                                color: _muted, fontWeight: FontWeight.w700)),
                      )
                    else
                      for (final entry in selected.values)
                        addEmployeeSelectedLicenseCard(
                            context, entry, setDialogState),
                  ]),
            ),
          ),
        ),
        actions: [
          TextButton(
              onPressed: () => Navigator.pop(context),
              child: const Text('Cancel')),
          FilledButton(
            onPressed: () {
              if (!formKey.currentState!.validate()) return;
              if (selected.isEmpty) {
                showSnack(context, 'Please select at least one license.');
                return;
              }
              final now = DateTime.now().toIso8601String();
              Navigator.pop(
                  context,
                  selected.values.map((entry) {
                    final existing = records
                        .cast<Map<String, dynamic>?>()
                        .firstWhere(
                            (rec) =>
                                formatValue(rec?['license_name']) == entry.name,
                            orElse: () => null);
                    final status = licenseStatusFromExpiry(entry.expiry.text);
                    return <String, dynamic>{
                      if (existing?['id'] != null) 'id': existing!['id'],
                      'employee_id': employeeId,
                      'license_name': entry.name,
                      'license_number': entry.number.text.trim(),
                      'expiry_date': toIsoDateInput(entry.expiry.text),
                      'attachment_url': entry.attachmentUrl.trim().isEmpty
                          ? null
                          : entry.attachmentUrl.trim(),
                      'status': entry.status.isEmpty
                          ? (status.isEmpty ? null : status)
                          : entry.status,
                      'updated_at': now,
                    };
                  }).toList());
            },
            child: const Text('Save'),
          ),
        ],
      ),
    ),
  );
  for (final entry in selected.values) {
    entry.dispose();
  }
  return result;
}

Future<List<Map<String, dynamic>>?> showEditCertificateGroupDialog(
    BuildContext context,
    Map<String, dynamic> row,
    List<String> certificateNames) async {
  final records = (row['certificate_records'] is List)
      ? List<Map<String, dynamic>>.from(row['certificate_records'] as List)
      : <Map<String, dynamic>>[row];
  final employeeId =
      '${row['employee_id'] ?? (records.isNotEmpty ? records.first['employee_id'] : '')}';
  final employeeName = formatValue(row['employee_name']);
  final formKey = GlobalKey<FormState>();
  final selected = <String, SelectedCertificateInput>{};
  for (final rec in records) {
    final name = formatValue(rec['certificate_name']);
    if (name == '-' || name.trim().isEmpty) continue;
    final entry = SelectedCertificateInput(name);
    entry.number.text = formatEditValue(rec['certificate_number']);
    entry.expiry.text = formatEditValue(rec['expiry_date']);
    entry.attachmentUrl = formatEditValue(rec['attachment_url']);
    entry.attachmentFileName =
        entry.attachmentUrl.isEmpty ? '' : entry.attachmentUrl.split('/').last;
    entry.status = formatEditValue(rec['status']).isEmpty
        ? certificateStatusFromExpiry(entry.expiry.text)
        : formatEditValue(rec['status']);
    entry.attachment.text = entry.attachmentUrl;
    selected[name] = entry;
  }
  final allNames = <String>{...certificateNames, ...selected.keys}.toList()
    ..sort((a, b) => a.toLowerCase().compareTo(b.toLowerCase()));

  final result = await showDialog<List<Map<String, dynamic>>>(
    context: context,
    builder: (_) => StatefulBuilder(
      builder: (context, setDialogState) => AlertDialog(
        title: const Text('Edit Certificate'),
        content: SizedBox(
          width: 790,
          child: Form(
            key: formKey,
            child: SingleChildScrollView(
              child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const DialogSectionTitle('Employee Information'),
                    ReadOnlyEmployeeBox(employeeName == '-'
                        ? linkedEmployeeName(row)
                        : employeeName),
                    const SizedBox(height: 16),
                    const DialogSectionTitle('Certificate Information'),
                    Wrap(spacing: 10, runSpacing: 8, children: [
                      for (final cert in allNames)
                        SizedBox(
                          width: 228,
                          child: CheckboxListTile(
                            dense: true,
                            contentPadding: EdgeInsets.zero,
                            controlAffinity: ListTileControlAffinity.leading,
                            title: Text(cert,
                                maxLines: 2,
                                overflow: TextOverflow.ellipsis,
                                style: const TextStyle(
                                    fontSize: 13,
                                    fontWeight: FontWeight.w700,
                                    color: _ink)),
                            value: selected.containsKey(cert),
                            onChanged: (checked) => setDialogState(() {
                              if (checked == true) {
                                selected.putIfAbsent(
                                    cert, () => SelectedCertificateInput(cert));
                              } else {
                                selected.remove(cert)?.dispose();
                              }
                            }),
                          ),
                        ),
                    ]),
                    const SizedBox(height: 12),
                    if (selected.isEmpty)
                      Container(
                        width: 728,
                        padding: const EdgeInsets.all(14),
                        decoration: BoxDecoration(
                            color: const Color(0xFFF8FAFC),
                            borderRadius: BorderRadius.circular(14),
                            border: Border.all(color: _line)),
                        child: const Text(
                            'Select one or more certificates above.',
                            style: TextStyle(
                                color: _muted, fontWeight: FontWeight.w700)),
                      )
                    else
                      for (final entry in selected.values)
                        addEmployeeSelectedCertificateCard(
                            context, entry, setDialogState),
                  ]),
            ),
          ),
        ),
        actions: [
          TextButton(
              onPressed: () => Navigator.pop(context),
              child: const Text('Cancel')),
          FilledButton(
            onPressed: () {
              if (!formKey.currentState!.validate()) return;
              if (selected.isEmpty) {
                showSnack(context, 'Please select at least one certificate.');
                return;
              }
              final now = DateTime.now().toIso8601String();
              Navigator.pop(
                  context,
                  selected.values.map((entry) {
                    final existing = records
                        .cast<Map<String, dynamic>?>()
                        .firstWhere(
                            (rec) =>
                                formatValue(rec?['certificate_name']) ==
                                entry.name,
                            orElse: () => null);
                    final status =
                        certificateStatusFromExpiry(entry.expiry.text);
                    return <String, dynamic>{
                      if (existing?['id'] != null) 'id': existing!['id'],
                      'employee_id': employeeId,
                      'certificate_type': 'National Certificate',
                      'certificate_name': entry.name,
                      'certificate_number': entry.number.text.trim(),
                      'expiry_date': toIsoDateInput(entry.expiry.text),
                      'attachment_url': entry.attachmentUrl.trim().isEmpty
                          ? null
                          : entry.attachmentUrl.trim(),
                      'status': entry.status.isEmpty
                          ? (status.isEmpty ? null : status)
                          : entry.status,
                      'updated_at': now,
                    };
                  }).toList());
            },
            child: const Text('Save'),
          ),
        ],
      ),
    ),
  );
  for (final entry in selected.values) {
    entry.dispose();
  }
  return result;
}

Future<void> saveCredentialRecords(
    BuildContext context,
    String tableName,
    List<Map<String, dynamic>> records,
    VoidCallback refresh,
    String label) async {
  try {
    for (final record in records) {
      final data = upperCaseDataMap(Map<String, dynamic>.from(record));
      final id = data.remove('id');
      if (id == null) {
        await db.from(tableName).insert(data);
      } else {
        await db.from(tableName).update(data).eq('id', id);
      }
    }
    refresh();
    showSnack(context, '$label information saved.');
  } catch (e) {
    showSnack(context, 'Save $label Failed: $e');
  }
}

Future<void> viewLicenseGroup(
    BuildContext context, Map<String, dynamic> row) async {
  final records = (row['license_records'] is List)
      ? List<Map<String, dynamic>>.from(row['license_records'] as List)
      : <Map<String, dynamic>>[row];
  await showDialog<void>(
    context: context,
    builder: (_) => AlertDialog(
      title: Text('License Details - ${formatValue(row['employee_name'])}'),
      content: SizedBox(
        width: 920,
        child: SingleChildScrollView(
          child:
              Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
            for (final rec in records)
              Container(
                width: double.infinity,
                margin: const EdgeInsets.only(bottom: 10),
                padding:
                    const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                decoration: BoxDecoration(
                    color: const Color(0xFFF8FAFC),
                    borderRadius: BorderRadius.circular(14),
                    border: Border.all(color: _line)),
                child: Wrap(spacing: 10, runSpacing: 10, children: [
                  DetailTile('License Name', formatValue(rec['license_name'])),
                  DetailTile(
                      'License Number', formatValue(rec['license_number'])),
                  DetailTile('Expiry Date', formatValue(rec['expiry_date'])),
                  DetailTile('Status', formatValue(rec['status'])),
                  AttachmentPdfTile('Attachment PDF', rec['attachment_url']),
                ]),
              ),
          ]),
        ),
      ),
      actions: [
        TextButton(
            onPressed: () => Navigator.pop(context), child: const Text('Close'))
      ],
    ),
  );
}

Future<Map<String, dynamic>?> pickLicenseRecordToEdit(
    BuildContext context, Map<String, dynamic> row) async {
  final records = (row['license_records'] is List)
      ? List<Map<String, dynamic>>.from(row['license_records'] as List)
      : <Map<String, dynamic>>[row];
  if (records.isEmpty) return null;
  if (records.length == 1) return records.first;
  return showDialog<Map<String, dynamic>>(
    context: context,
    builder: (_) => AlertDialog(
      title: const Text('Choose License to Edit'),
      content: SizedBox(
        width: 520,
        child: ListView.separated(
          shrinkWrap: true,
          itemCount: records.length,
          separatorBuilder: (_, __) => const Divider(height: 1),
          itemBuilder: (_, i) => ListTile(
            title: Text(formatValue(records[i]['license_name'])),
            subtitle: Text(
                'License No.: ${formatValue(records[i]['license_number'])} \u2022 Expiry: ${formatValue(records[i]['expiry_date'])}'),
            onTap: () => Navigator.pop(context, records[i]),
          ),
        ),
      ),
      actions: [
        TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancel'))
      ],
    ),
  );
}

Future<void> editLicense(BuildContext context, Map<String, dynamic>? row,
    VoidCallback refresh) async {
  final isAdd = row == null;
  if (isAdd) {
    final records = await showAddLicenseDialog(
        context, await employeeOptions(), await licenseNameOptions());
    if (records == null || records.isEmpty) return;
    await saveCredentialRecords(
        context, 'employee_licenses', records, refresh, 'License');
    return;
  }

  final records = await showEditLicenseGroupDialog(
      context, row, await licenseNameOptions());
  if (records == null || records.isEmpty) return;
  await saveCredentialRecords(
      context, 'employee_licenses', records, refresh, 'License');
}

class SelectedCertificateInput {
  final String name;
  final TextEditingController number = TextEditingController();
  final TextEditingController expiry = TextEditingController();
  final TextEditingController attachment = TextEditingController();
  String attachmentUrl = '';
  String attachmentFileName = '';
  bool uploadingAttachment = false;
  String status = '';

  SelectedCertificateInput(this.name);

  void dispose() {
    number.dispose();
    expiry.dispose();
    attachment.dispose();
  }
}

String certificateStatusFromExpiry(String text) =>
    licenseStatusFromExpiry(text);

Future<void> pickAndUploadCertificatePdf(BuildContext context,
    SelectedCertificateInput entry, StateSetter setDialogState) async {
  final file = await pickPdfFileOrNull();
  if (file == null) return;
  final lowerName = file.name.toLowerCase();
  if (!lowerName.endsWith('.pdf') && file.type != 'application/pdf') {
    showSnack(context, 'Only PDF files are allowed.');
    return;
  }
  setDialogState(() => entry.uploadingAttachment = true);
  try {
    final reader = html.FileReader();
    reader.readAsArrayBuffer(file);
    await reader.onLoad.first;
    final result = reader.result;
    late final Uint8List bytes;
    if (result is ByteBuffer) {
      bytes = Uint8List.view(result);
    } else if (result is Uint8List) {
      bytes = result;
    } else {
      throw Exception('Unable to read selected PDF file.');
    }
    final safeName = file.name.replaceAll(RegExp(r'[^A-Za-z0-9._-]+'), '_');
    final path =
        'certificates/${DateTime.now().millisecondsSinceEpoch}_$safeName';
    await db.storage.from('hr-attachments').uploadBinary(path, bytes,
        fileOptions:
            const FileOptions(contentType: 'application/pdf', upsert: true));
    final url = db.storage.from('hr-attachments').getPublicUrl(path);
    setDialogState(() {
      entry.attachmentUrl = url;
      entry.attachmentFileName = file.name;
      entry.uploadingAttachment = false;
    });
  } catch (e) {
    setDialogState(() => entry.uploadingAttachment = false);
    showSnack(context, 'PDF upload failed: $e');
  }
}

Future<List<Map<String, dynamic>>?> showAddCertificateDialog(
    BuildContext context,
    List<EditOption> employees,
    List<String> certificates) async {
  final formKey = GlobalKey<FormState>();
  String? employeeId;
  String selectedCategory = certificateCategories.first;
  final selected = <String, SelectedCertificateInput>{};

  final result = await showDialog<List<Map<String, dynamic>>>(
    context: context,
    builder: (_) => StatefulBuilder(
      builder: (context, setDialogState) => AlertDialog(
        title: const Text('Add Certificate'),
        insetPadding: const EdgeInsets.symmetric(horizontal: 24, vertical: 20),
        contentPadding: const EdgeInsets.fromLTRB(24, 12, 24, 8),
        content: SizedBox(
          width: 1040,
          height: MediaQuery.sizeOf(context).height * 0.76,
          child: Form(
            key: formKey,
            child: SingleChildScrollView(
              child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const DialogSectionTitle('Employee Information', width: 1016),
                    employeeAutocompleteField(
                      employees: employees,
                      employeeId: employeeId,
                      width: 1016,
                      onEmployeeChanged: (value) =>
                          setDialogState(() => employeeId = value),
                    ),
                    const SizedBox(height: 16),
                    const DialogSectionTitle('Certificate Category', width: 1016),
                    DropdownButtonFormField<String>(
                      value: selectedCategory,
                      isExpanded: true,
                      decoration: const InputDecoration(
                        labelText: 'Select Certificate Category',
                        prefixIcon: Icon(Icons.workspace_premium_rounded),
                      ),
                      items: [
                        for (final category in certificateCategories)
                          DropdownMenuItem<String>(
                            value: category,
                            child: Text(category),
                          ),
                      ],
                      onChanged: (value) {
                        if (value != null) {
                          setDialogState(() => selectedCategory = value);
                        }
                      },
                    ),
                    const SizedBox(height: 16),
                    DialogSectionTitle(
                      '$selectedCategory Options',
                      width: 1016,
                    ),
                    Builder(builder: (context) {
                      final visibleCertificates = certificates
                          .where((certificate) =>
                              certificateCategoryForName(certificate) ==
                              selectedCategory)
                          .toList();
                      if (visibleCertificates.isEmpty) {
                        return Container(
                          width: double.infinity,
                          padding: const EdgeInsets.all(14),
                          decoration: BoxDecoration(
                            color: const Color(0xFFF8FAFC),
                            borderRadius: BorderRadius.circular(14),
                            border: Border.all(color: _line),
                          ),
                          child: Text(
                            'No certificate options are available under $selectedCategory yet.',
                            style: const TextStyle(
                              color: _muted,
                              fontWeight: FontWeight.w700,
                            ),
                          ),
                        );
                      }
                      return Container(
                        width: double.infinity,
                        padding: const EdgeInsets.all(12),
                        decoration: BoxDecoration(
                          color: const Color(0xFFF8FAFC),
                          borderRadius: BorderRadius.circular(16),
                          border: Border.all(color: _line),
                        ),
                        child: Wrap(
                          spacing: 10,
                          runSpacing: 10,
                          children: [
                            for (final cert in visibleCertificates)
                              Container(
                                width: 320,
                                constraints: const BoxConstraints(minHeight: 68),
                                padding: const EdgeInsets.symmetric(
                                    horizontal: 6, vertical: 4),
                                decoration: BoxDecoration(
                                  color: Colors.white,
                                  borderRadius: BorderRadius.circular(14),
                                  border: Border.all(color: _line),
                                ),
                                child: CheckboxListTile(
                                  dense: false,
                                  contentPadding: EdgeInsets.zero,
                                controlAffinity:
                                    ListTileControlAffinity.leading,
                                  title: Text(
                                    cert,
                                    maxLines: 3,
                                    softWrap: true,
                                  style: const TextStyle(
                                    fontSize: 13,
                                    fontWeight: FontWeight.w700,
                                    color: _ink,
                                  ),
                                ),
                                  value: selected.containsKey(cert),
                                  onChanged: (checked) =>
                                      setDialogState(() {
                                    if (checked == true) {
                                      selected.putIfAbsent(
                                        cert,
                                        () => SelectedCertificateInput(cert),
                                      );
                                    } else {
                                      selected.remove(cert)?.dispose();
                                    }
                                  }),
                                ),
                              ),
                          ],
                        ),
                      );
                    }),
                    const SizedBox(height: 16),
                    const DialogSectionTitle('Selected Certificates', width: 1016),
                    if (selected.isEmpty)
                      Container(
                        width: double.infinity,
                        padding: const EdgeInsets.all(14),
                        decoration: BoxDecoration(
                            color: const Color(0xFFF8FAFC),
                            borderRadius: BorderRadius.circular(14),
                            border: Border.all(color: _line)),
                        child: const Text(
                            'Select one or more certificates above. The selected certificates will appear here as a table.',
                            style: TextStyle(
                                color: _muted, fontWeight: FontWeight.w700)),
                      )
                    else
                      SingleChildScrollView(
                        scrollDirection: Axis.horizontal,
                        child: Container(
                          width: 1016,
                          decoration: BoxDecoration(
                            color: Colors.white,
                            borderRadius: BorderRadius.circular(18),
                            border: Border.all(color: _line)),
                        child: Column(children: [
                          Container(
                            padding: const EdgeInsets.symmetric(
                                horizontal: 12, vertical: 10),
                            decoration: const BoxDecoration(
                                color: Color(0xFFF8FAFC),
                                borderRadius: BorderRadius.vertical(
                                    top: Radius.circular(16))),
                            child: const Row(children: [
                              Expanded(
                                  flex: 3,
                                  child: Text('Certificate Name',
                                      style: TextStyle(
                                          fontWeight: FontWeight.w900,
                                          color: _ink))),
                              SizedBox(width: 10),
                              Expanded(
                                  flex: 2,
                                  child: Text('Certificate Number',
                                      style: TextStyle(
                                          fontWeight: FontWeight.w900,
                                          color: _ink))),
                              SizedBox(width: 10),
                              Expanded(
                                  flex: 2,
                                  child: Text('Expiry Date',
                                      style: TextStyle(
                                          fontWeight: FontWeight.w900,
                                          color: _ink))),
                              SizedBox(width: 10),
                              Expanded(
                                  flex: 2,
                                  child: Text('Attachment (PDF)',
                                      style: TextStyle(
                                          fontWeight: FontWeight.w900,
                                          color: _ink))),
                              SizedBox(width: 10),
                              SizedBox(
                                  width: 130,
                                  child: Text('Status',
                                      style: TextStyle(
                                          fontWeight: FontWeight.w900,
                                          color: _ink))),
                            ]),
                          ),
                          for (final entry in selected.values)
                            Padding(
                              padding: const EdgeInsets.symmetric(
                                  horizontal: 12, vertical: 8),
                              child: Row(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    Expanded(
                                        flex: 3,
                                        child: Padding(
                                            padding:
                                                const EdgeInsets.only(top: 14),
                                            child: Text(entry.name,
                                                style: const TextStyle(
                                                    fontWeight: FontWeight.w800,
                                                    color: _ink)))),
                                    const SizedBox(width: 10),
                                    Expanded(
                                      flex: 2,
                                      child: TextFormField(
                                        controller: entry.number,
                                        decoration: const InputDecoration(
                                            labelText: 'Certificate Number'),
                                        validator: (v) =>
                                            v == null || v.trim().isEmpty
                                                ? 'Required'
                                                : null,
                                      ),
                                    ),
                                    const SizedBox(width: 10),
                                    Expanded(
                                      flex: 2,
                                      child: TextFormField(
                                        controller: entry.expiry,
                                        decoration: const InputDecoration(
                                            labelText: 'Expiry Date',
                                            hintText: 'MM/DD/YYYY'),
                                        validator: (v) {
                                          if (v == null || v.trim().isEmpty)
                                            return 'Required';
                                          if (parseFlexibleDate(v.trim()) ==
                                              null)
                                            return 'Use January 02, 2026';
                                          return null;
                                        },
                                        onChanged: (v) => setDialogState(() =>
                                            entry.status =
                                                certificateStatusFromExpiry(v)),
                                      ),
                                    ),
                                    const SizedBox(width: 10),
                                    Expanded(
                                      flex: 2,
                                      child: Column(
                                          crossAxisAlignment:
                                              CrossAxisAlignment.start,
                                          children: [
                                            OutlinedButton.icon(
                                              onPressed: entry
                                                      .uploadingAttachment
                                                  ? null
                                                  : () =>
                                                      pickAndUploadCertificatePdf(
                                                          context,
                                                          entry,
                                                          setDialogState),
                                              icon: entry.uploadingAttachment
                                                  ? const SizedBox(
                                                      width: 16,
                                                      height: 16,
                                                      child:
                                                          CircularProgressIndicator(
                                                              strokeWidth: 2))
                                                  : const Icon(Icons
                                                      .picture_as_pdf_rounded),
                                              label: Text(entry
                                                      .uploadingAttachment
                                                  ? 'Uploading...'
                                                  : (entry.attachmentFileName
                                                          .isEmpty
                                                      ? 'Attach PDF'
                                                      : 'Change PDF')),
                                            ),
                                            const SizedBox(height: 6),
                                            Text(
                                              entry.attachmentFileName.isEmpty
                                                  ? 'No PDF attached'
                                                  : entry.attachmentFileName,
                                              maxLines: 2,
                                              overflow: TextOverflow.ellipsis,
                                              style: TextStyle(
                                                  fontSize: 12,
                                                  color: entry
                                                          .attachmentFileName
                                                          .isEmpty
                                                      ? _muted
                                                      : _ink,
                                                  fontWeight: FontWeight.w700),
                                            ),
                                          ]),
                                    ),
                                    const SizedBox(width: 10),
                                    SizedBox(
                                        width: 130,
                                        child: Padding(
                                            padding:
                                                const EdgeInsets.only(top: 10),
                                            child: StatusChip(
                                                entry.status.isEmpty
                                                    ? '-'
                                                    : entry.status))),
                                  ]),
                            ),
                          ]),
                        ),
                      ),
                  ]),
            ),
          ),
        ),
        actions: [
          TextButton(
              onPressed: () => Navigator.pop(context),
              child: const Text('Cancel')),
          FilledButton(
            onPressed: () {
              if (!formKey.currentState!.validate()) return;
              if (selected.isEmpty) {
                showSnack(context, 'Please select at least one certificate.');
                return;
              }
              final missingPdf = selected.values
                  .where((entry) => entry.attachmentUrl.trim().isEmpty)
                  .toList();
              if (missingPdf.isNotEmpty) {
                showSnack(context,
                    'Please attach a PDF file for every selected certificate.');
                return;
              }
              final now = DateTime.now().toIso8601String();
              Navigator.pop(
                  context,
                  selected.values.map((entry) {
                    final status =
                        certificateStatusFromExpiry(entry.expiry.text);
                    return <String, dynamic>{
                      'employee_id': employeeId,
                      'certificate_type': 'National Certificate',
                      'certificate_name': entry.name,
                      'certificate_number': entry.number.text.trim(),
                      'expiry_date': toIsoDateInput(entry.expiry.text),
                      'attachment_url': entry.attachmentUrl.trim().isEmpty
                          ? null
                          : entry.attachmentUrl.trim(),
                      'status': status.isEmpty ? null : status,
                      'updated_at': now,
                    };
                  }).toList());
            },
            child: const Text('Save'),
          ),
        ],
      ),
    ),
  );

  for (final item in selected.values) {
    item.dispose();
  }
  return result;
}

Future<void> viewCertificateGroup(
    BuildContext context, Map<String, dynamic> row) async {
  final records = (row['certificate_records'] is List)
      ? List<Map<String, dynamic>>.from(row['certificate_records'] as List)
      : <Map<String, dynamic>>[row];
  await showDialog<void>(
    context: context,
    builder: (_) => AlertDialog(
      title: Text('Certificate Details - ${formatValue(row['employee_name'])}'),
      content: SizedBox(
        width: 920,
        child: SingleChildScrollView(
          child:
              Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
            for (final rec in records)
              Container(
                width: double.infinity,
                margin: const EdgeInsets.only(bottom: 10),
                padding:
                    const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                decoration: BoxDecoration(
                    color: const Color(0xFFF8FAFC),
                    borderRadius: BorderRadius.circular(14),
                    border: Border.all(color: _line)),
                child: Wrap(spacing: 10, runSpacing: 10, children: [
                  DetailTile(
                      'Certificate Type', formatValue(rec['certificate_type'])),
                  DetailTile(
                      'Certificate Name', formatValue(rec['certificate_name'])),
                  DetailTile('Certificate Number',
                      formatValue(rec['certificate_number'])),
                  DetailTile('Expiry Date', formatValue(rec['expiry_date'])),
                  DetailTile('Status', formatValue(rec['status'])),
                  AttachmentPdfTile('Attachment PDF', rec['attachment_url']),
                ]),
              ),
          ]),
        ),
      ),
      actions: [
        TextButton(
            onPressed: () => Navigator.pop(context), child: const Text('Close'))
      ],
    ),
  );
}

Future<Map<String, dynamic>?> pickCertificateRecordToEdit(
    BuildContext context, Map<String, dynamic> row) async {
  final records = (row['certificate_records'] is List)
      ? List<Map<String, dynamic>>.from(row['certificate_records'] as List)
      : <Map<String, dynamic>>[row];
  if (records.isEmpty) return null;
  if (records.length == 1) return records.first;
  return showDialog<Map<String, dynamic>>(
    context: context,
    builder: (_) => AlertDialog(
      title: const Text('Choose Certificate to Edit'),
      content: SizedBox(
        width: 520,
        child: ListView.separated(
          shrinkWrap: true,
          itemCount: records.length,
          separatorBuilder: (_, __) => const Divider(height: 1),
          itemBuilder: (_, i) => ListTile(
            title: Text(formatValue(records[i]['certificate_name'])),
            subtitle: Text(
                'Certificate No.: ${formatValue(records[i]['certificate_number'])} \u2022 Expiry: ${formatValue(records[i]['expiry_date'])}'),
            onTap: () => Navigator.pop(context, records[i]),
          ),
        ),
      ),
      actions: [
        TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancel'))
      ],
    ),
  );
}

Future<void> editCertificate(BuildContext context, Map<String, dynamic>? row,
    VoidCallback refresh) async {
  final isAdd = row == null;
  if (isAdd) {
    final records = await showAddCertificateDialog(
        context, await employeeOptions(), await certificateNameOptions());
    if (records == null || records.isEmpty) return;
    await saveCredentialRecords(
        context, 'employee_certificates', records, refresh, 'Certificate');
    return;
  }

  final records = await showEditCertificateGroupDialog(
      context, row, await certificateNameOptions());
  if (records == null || records.isEmpty) return;
  await saveCredentialRecords(
      context, 'employee_certificates', records, refresh, 'Certificate');
}

Future<void> approveRanking(BuildContext context, Map<String, dynamic> row,
    VoidCallback refresh) async {
  final normalized = normalizeRow(row);
  final employeeName = formatValue(normalized['employee_name']);
  final isAlreadyApproved =
      formatEditValue(normalized['approved_date']).isNotEmpty ||
          formatEditValue(normalized['approved_rank_text']).isNotEmpty;
  if (isAlreadyApproved) return;

  final confirmed = await showDialog<bool>(
    context: context,
    barrierDismissible: false,
    builder: (dialogContext) => AlertDialog(
      backgroundColor: Colors.white,
      surfaceTintColor: Colors.transparent,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(18)),
      titlePadding: const EdgeInsets.fromLTRB(24, 22, 24, 0),
      contentPadding: const EdgeInsets.fromLTRB(24, 14, 24, 10),
      actionsPadding: const EdgeInsets.fromLTRB(24, 4, 24, 18),
      title: const Text(
        'Approve Faculty Ranking?',
        style: TextStyle(
          color: _ink,
          fontSize: 19,
          fontWeight: FontWeight.w700,
        ),
      ),
      content: SizedBox(
        width: 390,
        child: Text(
          'Are you sure you want to approve the ranking for $employeeName? Ranking details will be locked.',
          style: const TextStyle(
            color: _muted,
            fontSize: 14,
            height: 1.45,
          ),
        ),
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.pop(dialogContext, false),
          child: const Text('Cancel'),
        ),
        FilledButton(
          onPressed: () => Navigator.pop(dialogContext, true),
          style: FilledButton.styleFrom(
            backgroundColor: _primary,
            foregroundColor: Colors.white,
            padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(10),
            ),
          ),
          child: const Text('Approve'),
        ),
      ],
    ),
  );
  if (confirmed != true || !context.mounted) return;

  final today = DateFormat('yyyy-MM-dd').format(DateTime.now());
  try {
    await db
        .from('ranking_applications')
        .update(upperCaseDataMap({
          'approved_rank_text': normalized['applied_rank_text'],
          'approved_salary': normalized['applied_salary'],
          'approved_date': today,
          'effective_date': today,
          'updated_at': DateTime.now().toIso8601String(),
        }))
        .eq('id', row['id']);
    refresh();
    if (context.mounted) {
      showSnack(context,
          'Ranking approved. You may edit the approval dates if needed.');
    }
  } catch (e) {
    if (context.mounted) {
      showSnack(context, 'Approve Ranking Failed: $e');
    }
  }
}

Future<void> editRanking(BuildContext context, Map<String, dynamic>? row,
    VoidCallback refresh) async {
  final isAdd = row == null;
  final data = await showRankingDialog(
      context,
      isAdd ? await employeeOptions() : const <EditOption>[],
      await cycleOptions(),
      await rankOptions(),
      row,
      isAdd ? await rankingAppointmentByEmployee() : const <String, String>{});
  if (data == null) return;
  if (isAdd &&
      !await ensureNoEmployeeDuplicate(
          context, 'ranking_applications', data['employee_id'], 'ranking'))
    return;
  try {
    data.removeWhere((key, value) => key == 'id');
    data['updated_at'] = DateTime.now().toIso8601String();
    if (row == null) {
      await db.from('ranking_applications').insert(data);
      if (context.mounted) showSnack(context, 'Record Added.');
    } else {
      await db.from('ranking_applications').update(data).eq('id', row['id']);
      if (context.mounted) showSnack(context, 'Record Updated.');
    }
    safeRefresh(refresh);
  } catch (e) {
    if (context.mounted) showSnack(context, 'Save Failed: $e');
  }
}

Future<Map<String, dynamic>?> showRankingDialog(
    BuildContext context,
    List<EditOption> employees,
    List<EditOption> cycles,
    List<EditOption> ranks,
    Map<String, dynamic>? initial,
    Map<String, String> appointmentByEmployee) async {
  final isAdd = initial == null;
  final isApproved = !isAdd &&
      (formatEditValue(initial?['approved_date']).isNotEmpty ||
          formatEditValue(initial?['approved_rank_text']).isNotEmpty);
  final formKey = GlobalKey<FormState>();
  String? employeeId = isAdd ? null : initial?['employee_id']?.toString();
  String selectedEmployeeName = isAdd ? '' : linkedEmployeeName(initial);
  String? cycleId =
      optionValueOrFirst(initial?['cycle_id']?.toString(), cycles, true);
  final appointment =
      TextEditingController(text: formatEditValue(initial?['appointment']));
  final previousRank = TextEditingController(
      text: formatEditValue(initial?['previous_rank_text']));
  final previousSalary =
      TextEditingController(text: formatMoneyEdit(initial?['previous_salary']));
  final appliedRank = TextEditingController(
      text: formatEditValue(initial?['applied_rank_text']));
  final appliedSalary =
      TextEditingController(text: formatMoneyEdit(initial?['applied_salary']));
  final points =
      TextEditingController(text: formatEditValue(initial?['points_earned']));
  final approvedDate = TextEditingController(
      text: formatEditValue(initial?['approved_date']));
  final effectiveDate = TextEditingController(
      text: formatEditValue(initial?['effective_date']));

  Future<void> pickRank(
      TextEditingController rank, TextEditingController salary) async {
    final selected = await showDialog<EditOption>(
      context: context,
      builder: (_) => AlertDialog(
        title: const Text('Choose Rank'),
        content: SizedBox(
          width: 460,
          height: 440,
          child: ranks.isEmpty
              ? const Center(
                  child:
                      Text('No rank reference found. You can type manually.'))
              : ListView.separated(
                  itemCount: ranks.length,
                  separatorBuilder: (_, __) => const Divider(height: 1),
                  itemBuilder: (_, i) => ListTile(
                      title: Text(ranks[i].label),
                      onTap: () => Navigator.pop(context, ranks[i]))),
        ),
        actions: [
          TextButton(
              onPressed: () => Navigator.pop(context),
              child: const Text('Cancel'))
        ],
      ),
    );
    if (selected == null) return;
    rank.text = selected.value;
    if (selected.salary != null) salary.text = formatMoney(selected.salary);
  }

  final result = await showDialog<Map<String, dynamic>>(
    context: context,
    builder: (_) => StatefulBuilder(
      builder: (context, setDialogState) => AlertDialog(
        title: Text(isAdd ? 'Add Ranking Record' : 'Edit Ranking Record'),
        content: SizedBox(
          width: 760,
          child: Form(
            key: formKey,
            child: SingleChildScrollView(
              child: Wrap(spacing: 14, runSpacing: 14, children: [
                if (isAdd)
                  SizedBox(
                    width: 354,
                    child: Autocomplete<EditOption>(
                      displayStringForOption: (option) => option.label,
                      optionsBuilder: (textEditingValue) {
                        final sortedEmployees = uniqueOptions(employees)
                            .toList()
                          ..sort((a, b) => a.label
                              .toLowerCase()
                              .compareTo(b.label.toLowerCase()));
                        final query =
                            textEditingValue.text.trim().toLowerCase();
                        if (query.isEmpty) return sortedEmployees;
                        final normalizedQuery = normalizeName(query);
                        return sortedEmployees.where((option) {
                          final label = option.label.toLowerCase();
                          final normalizedLabel = normalizeName(option.label);
                          return label.contains(query) ||
                              normalizedLabel.contains(normalizedQuery);
                        });
                      },
                      onSelected: (option) => setDialogState(() {
                        employeeId = option.value;
                        selectedEmployeeName = option.label;
                        appointment.text =
                            appointmentByEmployee[option.value] ?? '';
                        applyRankSalaryForEmployee(previousRank, previousSalary,
                            ranks, selectedEmployeeName);
                        applyRankSalaryForEmployee(appliedRank, appliedSalary,
                            ranks, selectedEmployeeName);
                      }),
                      fieldViewBuilder: (context, textController, focusNode,
                              onFieldSubmitted) =>
                          TextFormField(
                        controller: textController,
                        focusNode: focusNode,
                        decoration: const InputDecoration(
                          labelText: 'Employee Name',
                          hintText: 'Select or type employee name',
                          suffixIcon: Icon(Icons.search_rounded),
                        ),
                        validator: (_) =>
                            employeeId == null || employeeId!.isEmpty
                                ? 'Please select employee from the list'
                                : null,
                        onChanged: (value) => setDialogState(() {
                          final typed = value.trim().toLowerCase();
                          final exact = uniqueOptions(employees)
                              .where((option) =>
                                  option.label.toLowerCase() == typed)
                              .toList();
                          if (exact.isNotEmpty) {
                            employeeId = exact.first.value;
                            selectedEmployeeName = exact.first.label;
                            appointment.text =
                                appointmentByEmployee[exact.first.value] ?? '';
                            applyRankSalaryForEmployee(previousRank,
                                previousSalary, ranks, selectedEmployeeName);
                            applyRankSalaryForEmployee(appliedRank,
                                appliedSalary, ranks, selectedEmployeeName);
                          } else {
                            employeeId = null;
                            selectedEmployeeName = '';
                            appointment.text = '';
                          }
                        }),
                      ),
                      optionsViewBuilder: (context, onSelected, options) =>
                          Align(
                        alignment: Alignment.topLeft,
                        child: Material(
                          elevation: 6,
                          borderRadius: BorderRadius.circular(14),
                          child: ConstrainedBox(
                            constraints: const BoxConstraints(
                                maxWidth: 520, maxHeight: 320),
                            child: ListView.separated(
                              padding: EdgeInsets.zero,
                              shrinkWrap: true,
                              itemCount: options.length,
                              separatorBuilder: (_, __) =>
                                  const Divider(height: 1),
                              itemBuilder: (context, index) {
                                final option = options.elementAt(index);
                                return ListTile(
                                  dense: true,
                                  title: Text(option.label,
                                      overflow: TextOverflow.ellipsis),
                                  onTap: () => onSelected(option),
                                );
                              },
                            ),
                          ),
                        ),
                      ),
                    ),
                  )
                else
                  ReadOnlyEmployeeBox(linkedEmployeeName(initial)),
                textBox('Appointment', appointment, readOnly: true),
                if (isAdd)
                  rankAutocompleteBox('Previous Rank', previousRank,
                      previousSalary, ranks, selectedEmployeeName)
                else
                  textBox('Previous Rank', previousRank, readOnly: true),
                textBox('Previous Salary', previousSalary,
                    kind: FieldKind.number, readOnly: isApproved),
                if (!isAdd) ...[
                  textBox('Points Earned', points,
                      kind: FieldKind.number, readOnly: isApproved),
                  if (isApproved)
                    textBox('Applied Rank', appliedRank, readOnly: true)
                  else
                    rankAutocompleteBox('Applied Rank', appliedRank,
                        appliedSalary, ranks, selectedEmployeeName),
                  textBox('Applied Salary', appliedSalary,
                      kind: FieldKind.number, readOnly: isApproved),
                  if (isApproved) ...[
                    rankingDatePickerBox(
                        context, 'Approved Date', approvedDate),
                    rankingDatePickerBox(
                        context, 'Effective Date', effectiveDate),
                  ],
                ],
                SizedBox(
                    width: 728,
                    child: Container(
                        padding: const EdgeInsets.symmetric(
                            horizontal: 12, vertical: 8),
                        decoration: BoxDecoration(
                            color: const Color(0xFFEFF6FF),
                            borderRadius: BorderRadius.circular(16)),
                        child: Text(
                            isAdd
                                ? 'Select Employee, then pick the Previous Rank to auto-fill Previous Salary. You can still manually edit the Previous Salary before saving. Applied rank and points can be updated later using Edit.'
                                : isApproved
                                    ? 'This ranking is approved. Ranking details are locked; only Approved Date and Effective Date remain editable.'
                                    : 'Employee name is locked here. Use the table Approve button to approve the applied rank.',
                            style: const TextStyle(
                                color: Color(0xFF1E3A8A),
                                fontWeight: FontWeight.w600)))),
              ]),
            ),
          ),
        ),
        actions: [
          TextButton(
              onPressed: () => Navigator.pop(context),
              child: const Text('Cancel')),
          FilledButton(
            onPressed: () {
              if (!formKey.currentState!.validate()) return;
              FocusManager.instance.primaryFocus?.unfocus();
              final out = <String, dynamic>{
                'employee_id':
                    isAdd ? emptyToNull(employeeId) : initial?['employee_id'],
                'cycle_id': emptyToNull(cycleId),
                'appointment': emptyToNull(appointment.text),
                'previous_rank_text': emptyToNull(previousRank.text),
                'previous_salary': parseMoneyInput(previousSalary.text),
              };
              if (!isAdd) {
                out.addAll({
                  'applied_rank_text': emptyToNull(appliedRank.text),
                  'applied_salary': parseMoneyInput(appliedSalary.text),
                  'points_earned': num.tryParse(points.text.trim()),
                });
                if (isApproved) {
                  out.addAll({
                    'approved_date': toIsoDateInput(approvedDate.text),
                    'effective_date': toIsoDateInput(effectiveDate.text),
                  });
                }
              }
              Navigator.of(context, rootNavigator: true).pop(out);
            },
            child: const Text('Save'),
          ),
        ],
      ),
    ),
  );
  await Future<void>.delayed(Duration.zero);
  for (final c in [
    appointment,
    previousRank,
    previousSalary,
    appliedRank,
    appliedSalary,
    points,
    approvedDate,
    effectiveDate
  ]) {
    c.dispose();
  }
  return result;
}

Widget rankingDatePickerBox(BuildContext context, String label,
        TextEditingController controller) =>
    SizedBox(
      width: 354,
      child: TextFormField(
        controller: controller,
        keyboardType: TextInputType.datetime,
        inputFormatters: [DateSlashInputFormatter()],
        decoration: InputDecoration(
          labelText: label,
          hintText: 'MM/DD/YYYY',
          suffixIcon: IconButton(
            tooltip: 'Pick date',
            icon: const Icon(Icons.calendar_month_rounded),
            onPressed: () => pickDateIntoController(context, controller),
          ),
        ),
        validator: (value) {
          if (value == null || value.trim().isEmpty) return 'Required';
          if (parseFlexibleDate(value.trim()) == null) return 'Invalid date';
          return null;
        },
        onTap: () => pickDateIntoController(context, controller),
      ),
    );

Widget textBox(String label, TextEditingController controller,
        {FieldKind kind = FieldKind.text, bool readOnly = false}) =>
    SizedBox(
      width: 354,
      child: TextFormField(
        controller: controller,
        readOnly: readOnly,
        keyboardType: kind == FieldKind.number || kind == FieldKind.integer
            ? TextInputType.number
            : TextInputType.text,
        maxLines: kind == FieldKind.multiline ? 3 : 1,
        style: TextStyle(
            color: readOnly ? _muted : _ink,
            fontWeight: readOnly ? FontWeight.w800 : FontWeight.w500),
        decoration: InputDecoration(
            labelText: label,
            fillColor: readOnly ? const Color(0xFFF8FAFC) : Colors.white),
      ),
    );

Widget rankTextBox(
        String label, TextEditingController controller, VoidCallback onPick) =>
    SizedBox(
      width: 354,
      child: Row(children: [
        Expanded(
            child: TextFormField(
                controller: controller,
                decoration: InputDecoration(labelText: label))),
        const SizedBox(width: 8),
        OutlinedButton(onPressed: onPick, child: const Text('Pick')),
      ]),
    );

Widget rankAutocompleteBox(
        String label,
        TextEditingController controller,
        TextEditingController salaryController,
        List<EditOption> ranks,
        String employeeName) =>
    SizedBox(
      width: 354,
      child: Autocomplete<EditOption>(
        initialValue: TextEditingValue(text: controller.text),
        displayStringForOption: (option) => option.value,
        optionsBuilder: (textEditingValue) {
          final options = uniqueOptions(ranks).toList()
            ..sort((a, b) =>
                a.value.toLowerCase().compareTo(b.value.toLowerCase()));
          final query = textEditingValue.text.trim().toLowerCase();
          if (query.isEmpty) return options;
          final normalizedQuery = normalizeRankKey(query);
          return options.where((option) {
            final value = option.value.toLowerCase();
            final labelText = option.label.toLowerCase();
            final normalizedValue = normalizeRankKey(option.value);
            return value.contains(query) ||
                labelText.contains(query) ||
                normalizedValue.contains(normalizedQuery);
          });
        },
        onSelected: (option) {
          controller.text = option.value;
          if (option.salary != null)
            salaryController.text = formatMoney(option.salary);
        },
        fieldViewBuilder:
            (context, textController, focusNode, onFieldSubmitted) =>
                TextFormField(
          controller: textController,
          focusNode: focusNode,
          decoration: InputDecoration(
              labelText: label,
              hintText: 'Select or type rank',
              suffixIcon: const Icon(Icons.search_rounded)),
          onChanged: (value) {
            controller.text = value;
            final selectedKey = normalizeRankKey(value);
            final exact = uniqueOptions(ranks)
                .where(
                    (option) => normalizeRankKey(option.value) == selectedKey)
                .toList();
            if (exact.isNotEmpty && exact.first.salary != null)
              salaryController.text = formatMoney(exact.first.salary);
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
                    subtitle: option.salary == null
                        ? null
                        : Text(formatMoney(option.salary)),
                    onTap: () => onSelected(option),
                  );
                },
              ),
            ),
          ),
        ),
      ),
    );

const _salaryAlignmentBonusSurnames = <String>{
  'saulong',
  'epil',
  'roderos',
  'flores',
  'saligumba'
};

bool hasSalaryAlignmentBonus(Object? employeeName) {
  final normalized = normalizeName(
      '${employeeName ?? ''}'.replaceAll(RegExp(r'[^A-Za-z0-9 ]+'), ' '));
  if (normalized.isEmpty) return false;
  final parts = normalized.split(RegExp(r'\s+'));
  return parts.any(_salaryAlignmentBonusSurnames.contains);
}

num adjustedRankSalary(num salary, Object? employeeName) => salary;

EditOption? matchedRankOption(List<EditOption> ranks, String rankText) {
  final key = normalizeRankKey(rankText);
  if (key.isEmpty) return null;
  for (final option in uniqueOptions(ranks)) {
    if (normalizeRankKey(option.value) == key) return option;
  }
  return null;
}

void applyRankSalaryForEmployee(
    TextEditingController rankController,
    TextEditingController salaryController,
    List<EditOption> ranks,
    Object? employeeName) {
  final option = matchedRankOption(ranks, rankController.text);
  if (option?.salary == null) return;
  salaryController.text = formatMoney(option!.salary);
}

Future<void> saveRow(BuildContext context, String table, Object? id,
    Map<String, dynamic> data, VoidCallback refresh) async {
  try {
    final cleanData = upperCaseDataMap(data);
    cleanData.removeWhere((key, value) => key == 'id');
    cleanData['updated_at'] = DateTime.now().toIso8601String();
    if (id == null) {
      await db.from(table).insert(cleanData);
      showSnack(context, 'Record Added.');
    } else {
      await archiveOldContractBeforeUpdate(table, id);
      await db.from(table).update(cleanData).eq('id', id);
      showSnack(context, 'Record Updated.');
    }
    refresh();
  } catch (e) {
    showSnack(context, 'Save Failed: $e');
  }
}

class SummaryReportCategory {
  final String title;
  final String keyLabel;
  final Future<List<SummaryReportRow>> Function() load;
  const SummaryReportCategory(this.title, this.keyLabel, this.load);
}

class SummaryReportRow {
  final String label;
  final int total;
  final int male;
  final int female;
  const SummaryReportRow(
      {required this.label,
      required this.total,
      this.male = 0,
      this.female = 0});
}

class _SummaryBucket {
  int total = 0;
  int male = 0;
  int female = 0;

  void add(String gender) {
    total++;
    final key = gender.trim().toLowerCase();
    if (key == 'male' || key == 'm') male++;
    if (key == 'female' || key == 'f') female++;
  }
}

class ResignedEmployeesPage extends StatelessWidget {
  const ResignedEmployeesPage({super.key});

  @override
  Widget build(BuildContext context) => PageFrame(
        title: 'Resigned Employees',
        subtitle:
            'Employees marked as resigned are separated from the active Employees table.',
        child: CrudTable(
          load: () => loadResignedEmployees(),
          searchHint:
              'Search resigned employee, bio number, type, date, or status',
          addLabel: 'Add Employee',
          allowAdd: false,
          reportTitle: 'Resigned Employees Report',
          columns: const [
            GridCol('full_name', 'Employee Name', flex: 3, primary: true),
            GridCol('bio_number', 'Bio Number'),
            GridCol('gender', 'Gender'),
            GridCol('employee_type', 'Type'),
            GridCol('date_hired_display', 'Date Hired'),
            GridCol('date_resigned_display', 'Date Resigned'),
            GridCol('employment_status', 'Status', isStatus: true),
          ],
          onView: viewEmployee,
          onEdit: editEmployee,
          showDelete: false,
          onDelete: (row) async {},
        ),
      );
}

class ArchivedPage extends StatelessWidget {
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
        reportTitle:
            oldContracts ? 'Archived Old Contracts Report' : '$title Report',
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

class ReportsPage extends StatefulWidget {
  const ReportsPage({super.key});

  @override
  State<ReportsPage> createState() => _ReportsPageState();
}

class _ReportsPageState extends State<ReportsPage> {
  int selected = 0;

  List<SummaryReportCategory> get reports => [
        SummaryReportCategory('Contract Type Gender Summary Report', 'Type',
            loadContractTypeGenderSummary),
        SummaryReportCategory(
            'Gender Summary Report', 'Gender', loadGenderSummary),
        SummaryReportCategory('Ranks Summary Report', 'Rank', loadRanksSummary),
        SummaryReportCategory('Type of License Summary Report',
            'Type of License', loadLicenseTypeSummary),
        SummaryReportCategory(
            'NC/TM Summary Report', 'NC/TM', loadCertificateTypeSummary),
      ];

  Future<void> printCurrentReport(SummaryReportCategory config) async {
    final printWindow = html.window.open('about:blank', '_blank');
    try {
      final rows = await config.load();
      final markup =
          buildPrintableSummaryReportHtml(config.title, config.keyLabel, rows);
      final blob = html.Blob([markup], 'text/html');
      final url = html.Url.createObjectUrlFromBlob(blob);
      if (printWindow != null) {
        printWindow.location.href = url;
      } else {
        html.window.open(url, '_blank');
      }
    } catch (e) {
      if (mounted) showSnack(context, 'Print Failed: $e');
    }
  }

  @override
  Widget build(BuildContext context) {
    final config = reports[selected];
    return PageFrame(
      title: 'Reports',
      subtitle:
          'Print each summary category separately in two-column table format.',
      child: Column(children: [
        Card(
          child: Padding(
            padding: const EdgeInsets.all(14),
            child: Row(children: [
              SizedBox(
                width: 330,
                child: DropdownButtonFormField<int>(
                  value: selected,
                  isExpanded: true,
                  decoration:
                      const InputDecoration(labelText: 'Summary Category'),
                  items: [
                    for (var i = 0; i < reports.length; i++)
                      DropdownMenuItem(
                          value: i,
                          child: Text(reports[i].title,
                              overflow: TextOverflow.ellipsis))
                  ],
                  onChanged: (v) => setState(() => selected = v ?? 0),
                ),
              ),
              const SizedBox(width: 12),
              FilledButton.icon(
                  onPressed: () => printCurrentReport(config),
                  icon: const Icon(Icons.print_rounded),
                  label: const Text('Print Report')),
              const SizedBox(width: 12),
              const Expanded(
                  child: Text(
                      'Select one category, then print that category as a simple summary table.',
                      style: TextStyle(
                          color: _muted, fontWeight: FontWeight.w600))),
            ]),
          ),
        ),
        const SizedBox(height: 14),
        Expanded(
          child: FutureBuilder<List<SummaryReportRow>>(
            key: ValueKey(selected),
            future: config.load(),
            builder: (context, snap) {
              if (snap.connectionState != ConnectionState.done) {
                return const Center(child: CircularProgressIndicator());
              }
              if (snap.hasError) return ErrorBox('${snap.error}');
              final rows = snap.data ?? const <SummaryReportRow>[];
              return SummaryReportPreview(
                  title: config.title, keyLabel: config.keyLabel, rows: rows);
            },
          ),
        ),
      ]),
    );
  }
}

Future<Map<String, String>> employeeGenderById() async {
  final employees = await loadEmployees(limit: 5000);
  final out = <String, String>{};
  for (final item in employees) {
    final row = normalizeRow(Map<String, dynamic>.from(item as Map));
    final id = '${row['id'] ?? ''}'.trim();
    if (id.isNotEmpty) out[id] = formatValue(row['gender']);
  }
  return out;
}

String reportCleanLabel(Object? value, String fallback) {
  final text = formatValue(value).trim();
  if (text.isEmpty || text == '-') return fallback;
  return text;
}

List<SummaryReportRow> bucketRows(Map<String, _SummaryBucket> buckets,
    {List<String> preferredOrder = const [], bool includeTotalRow = false}) {
  final keys = <String>[];
  for (final item in preferredOrder) {
    if (buckets.containsKey(item)) keys.add(item);
  }
  final remaining = buckets.keys.where((key) => !keys.contains(key)).toList()
    ..sort((a, b) => a.toLowerCase().compareTo(b.toLowerCase()));
  keys.addAll(remaining);
  final rows = [
    for (final key in keys)
      SummaryReportRow(
          label: key,
          total: buckets[key]!.total,
          male: buckets[key]!.male,
          female: buckets[key]!.female),
  ];
  if (includeTotalRow) {
    rows.add(SummaryReportRow(
      label: 'TOTAL',
      total: rows.fold<int>(0, (sum, row) => sum + row.total),
      male: rows.fold<int>(0, (sum, row) => sum + row.male),
      female: rows.fold<int>(0, (sum, row) => sum + row.female),
    ));
  }
  return rows;
}

Future<List<SummaryReportRow>> loadContractTypeGenderSummary() async {
  final genderById = await employeeGenderById();
  final rows = await activeOnlyRows(loadContracts(limit: 5000));
  final buckets = <String, _SummaryBucket>{};
  for (final item in rows) {
    final row = normalizeRow(Map<String, dynamic>.from(item as Map));
    final type = reportCleanLabel(row['contract_type'], 'Unspecified');
    final gender = genderById['${row['employee_id'] ?? ''}'] ?? '';
    buckets.putIfAbsent(type, () => _SummaryBucket()).add(gender);
  }
  for (final type in const [
    'Full-time',
    'Full-time-Probationary',
    'Part-time',
    'Probationary',
    'Compliance'
  ]) {
    buckets.putIfAbsent(type, () => _SummaryBucket());
  }
  return bucketRows(buckets, preferredOrder: const [
    'Full-time',
    'Full-time-Probationary',
    'Part-time',
    'Probationary',
    'Compliance'
  ]);
}

Future<List<SummaryReportRow>> loadGenderSummary() async {
  final employees = await loadActiveEmployees(limit: 5000);
  var female = 0;
  var male = 0;
  for (final item in employees) {
    final row = normalizeRow(Map<String, dynamic>.from(item as Map));
    final gender = formatValue(row['gender']).trim().toLowerCase();
    if (gender == 'female' || gender == 'f') female++;
    if (gender == 'male' || gender == 'm') male++;
  }
  return [
    SummaryReportRow(label: 'Total Female', total: female),
    SummaryReportRow(label: 'Total Male', total: male),
    SummaryReportRow(
        label: 'Total Gender\n(Female + Male)', total: female + male),
  ];
}

Future<List<SummaryReportRow>> loadRanksSummary() async {
  final genderById = await employeeGenderById();
  final rows = await activeOnlyRows(loadRankings(limit: 5000));
  final buckets = <String, _SummaryBucket>{};
  for (final item in rows) {
    final row = normalizeRow(Map<String, dynamic>.from(item as Map));
    final rank = reportCleanLabel(
        row['approved_rank_text'] ??
            row['applied_rank_text'] ??
            row['previous_rank_text'],
        'Unspecified');
    final gender = genderById['${row['employee_id'] ?? ''}'] ?? '';
    buckets.putIfAbsent(rank, () => _SummaryBucket()).add(gender);
  }
  return bucketRows(buckets, includeTotalRow: true);
}

Future<List<SummaryReportRow>> loadLicenseTypeSummary() async {
  final genderById = await employeeGenderById();
  final rows = await activeOnlyRows(loadLicenses(limit: 5000));
  final buckets = <String, _SummaryBucket>{};
  for (final item in rows) {
    final row = normalizeRow(Map<String, dynamic>.from(item as Map));
    final type = reportCleanLabel(row['license_name'], 'Unspecified');
    final gender = genderById['${row['employee_id'] ?? ''}'] ?? '';
    buckets.putIfAbsent(type, () => _SummaryBucket()).add(gender);
  }
  return bucketRows(buckets, includeTotalRow: true);
}

Future<List<SummaryReportRow>> loadCertificateTypeSummary() async {
  final genderById = await employeeGenderById();
  final rows = await activeOnlyRows(loadCertificates(limit: 5000));
  final buckets = <String, _SummaryBucket>{};
  for (final item in rows) {
    final row = normalizeRow(Map<String, dynamic>.from(item as Map));
    final name = reportCleanLabel(
        row['certificate_name'] ?? row['certificate_type'], 'Unspecified');
    final gender = genderById['${row['employee_id'] ?? ''}'] ?? '';
    buckets.putIfAbsent(name, () => _SummaryBucket()).add(gender);
  }
  return bucketRows(buckets, includeTotalRow: true);
}

class SummaryReportPreview extends StatelessWidget {
  final String title;
  final String keyLabel;
  final List<SummaryReportRow> rows;
  const SummaryReportPreview(
      {super.key,
      required this.title,
      required this.keyLabel,
      required this.rows});

  bool get showGenderColumns => title == 'Contract Type Gender Summary Report';
  bool get isGenderSummary => title == 'Gender Summary Report';

  @override
  Widget build(BuildContext context) => Card(
        child: ClipRRect(
          borderRadius: BorderRadius.circular(22),
          child: Column(children: [
            Container(
                width: double.infinity,
                color: const Color(0xFFF8FAFC),
                padding: const EdgeInsets.all(16),
                child: Text('$title Preview',
                    style: const TextStyle(
                        fontWeight: FontWeight.w900, color: _ink))),
            const Divider(height: 1, color: _line),
            Expanded(
              child: rows.isEmpty
                  ? const EmptyBox()
                  : ListView.separated(
                      itemCount: rows.length,
                      separatorBuilder: (_, __) =>
                          const Divider(height: 1, color: _line),
                      itemBuilder: (_, i) {
                        final row = rows[i];
                        final isTotal = row.label.toUpperCase() == 'TOTAL' ||
                            row.label.startsWith('Total Gender');
                        final leftLabel = isGenderSummary
                            ? 'Gender: ${row.label}'
                            : '$keyLabel: ${row.label}';
                        return Container(
                          color:
                              isTotal ? const Color(0xFFFBFDFF) : Colors.white,
                          padding: const EdgeInsets.symmetric(
                              horizontal: 14, vertical: 16),
                          child: Row(children: [
                            Expanded(
                                flex: 2,
                                child: Text(leftLabel,
                                    style: TextStyle(
                                        fontWeight: isTotal
                                            ? FontWeight.w900
                                            : FontWeight.w800,
                                        color: _ink))),
                            Expanded(
                                child: Text('Total: ${row.total}',
                                    style: TextStyle(
                                        color: _ink,
                                        fontWeight: isTotal
                                            ? FontWeight.w900
                                            : FontWeight.w500))),
                            if (showGenderColumns)
                              Expanded(
                                  child: Text('Male: ${row.male}',
                                      style: const TextStyle(
                                          color: _ink,
                                          fontWeight: FontWeight.w500))),
                            if (showGenderColumns)
                              Expanded(
                                  child: Text('Female: ${row.female}',
                                      style: const TextStyle(
                                          color: _ink,
                                          fontWeight: FontWeight.w500))),
                          ]),
                        );
                      },
                    ),
            ),
          ]),
        ),
      );
}

String buildPrintableReportHtml(
    String title, List<GridCol> columns, List<Map<String, dynamic>> rows) {
  final cols = columns.map((c) => '<th>${escapeHtml(c.label)}</th>').join();
  final body = rows.map((r) {
    final cells = columns.map((c) {
      final raw = valueFor(r, c.key);
      final value = c.isMoney ? formatMoney(raw) : formatValue(raw);
      return '<td>${escapeHtml(value)}</td>';
    }).join();
    return '<tr>$cells</tr>';
  }).join();
  return '''<!doctype html><html><head><meta charset="utf-8"><title>${escapeHtml(title)}</title><style>@page{size:A4 landscape;margin:12mm}body{font-family:Arial,sans-serif;color:#0f172a}h1{font-size:18px}table{width:100%;border-collapse:collapse;font-size:11px}th,td{border:1px solid #cbd5e1;padding:6px;text-align:left;vertical-align:top}th{background:#eff6ff}</style></head><body><h1>${escapeHtml(title)}</h1><table><thead><tr>$cols</tr></thead><tbody>$body</tbody></table><script>window.print();</script></body></html>''';
}

String buildPrintableSummaryReportHtml(
    String title, String keyLabel, List<SummaryReportRow> rows) {
  final showGenderColumns = title == 'Contract Type Gender Summary Report';
  final isGenderSummary = title == 'Gender Summary Report';
  final body = rows.map((r) {
    final isTotal =
        r.label.toUpperCase() == 'TOTAL' || r.label.startsWith('Total Gender');
    final leftLabel =
        isGenderSummary ? 'Gender: ${r.label}' : '$keyLabel: ${r.label}';
    final cells = showGenderColumns
        ? '<td>${escapeHtml(leftLabel)}</td><td>${escapeHtml('Total: ${r.total}')}</td><td>${escapeHtml('Male: ${r.male}')}</td><td>${escapeHtml('Female: ${r.female}')}</td>'
        : '<td>${escapeHtml(leftLabel)}</td><td>${escapeHtml('Total: ${r.total}')}</td>';
    return '<tr${isTotal ? ' class="total-row"' : ''}>$cells</tr>';
  }).join();
  return '''<!doctype html><html><head><meta charset="utf-8"><title>${escapeHtml(title)}</title><style>@page{size:A4 portrait;margin:14mm}body{font-family:Arial,sans-serif;color:#0f172a}h1{font-size:18px;margin:0 0 12px}table{width:100%;border-collapse:collapse;font-size:12px}td{border:1px solid #cbd5e1;padding:8px;text-align:left;vertical-align:top}td:first-child{font-weight:700;background:#f8fafc}.total-row td{font-weight:800;background:#eff6ff}</style></head><body><h1>${escapeHtml(title)}</h1><table><tbody>$body</tbody></table><script>window.print();</script></body></html>''';
}

List<EditField> employeeEditFields() => const [
      EditField('full_name', 'Full Name', required: true),
      EditField('bio_number', 'Bio Number', required: true),
      EditField('gender', 'Gender',
          kind: FieldKind.dropdown,
          required: true,
          options: [
            EditOption('Male', 'Male'),
            EditOption('Female', 'Female')
          ]),
      EditField('civil_status', 'Civil Status',
          kind: FieldKind.dropdown,
          required: true,
          options: [
            EditOption('Single', 'Single'),
            EditOption('Married', 'Married'),
            EditOption('Widowed', 'Widowed'),
            EditOption('Separated', 'Separated')
          ]),
      EditField('birth_date', 'Birth Date',
          kind: FieldKind.date, required: true),
      EditField('address', 'Address',
          kind: FieldKind.multiline, lines: 2, required: true),
      EditField('contact_number', 'Contact Number', required: true),
      EditField('email', 'Email'),
      EditField('education_level', 'Educational Attainment', required: true),
      EditField('school_graduated', 'School Graduated', required: true),
      EditField('degree_course', 'Degree / Course', required: true),
      EditField('guardian_name', 'Guardian Name', required: true),
      EditField('guardian_relationship', 'Guardian Relationship',
          required: true),
      EditField('guardian_contact', 'Guardian Contact', required: true),
      EditField('guardian_address', 'Guardian Address',
          kind: FieldKind.multiline, lines: 2, required: true),
      EditField('designation', 'Designation', required: true),
      EditField('employee_type', 'Employee Type',
          kind: FieldKind.dropdown,
          required: true,
          options: [
            EditOption('full_time', 'Full Time'),
            EditOption('probationary', 'Probationary'),
            EditOption('part_time', 'Part Time'),
            EditOption('staff', 'Staff'),
            EditOption('faculty_staff', 'Faculty / Staff')
          ]),
      EditField('teaching_status', 'Teaching Status',
          kind: FieldKind.dropdown,
          required: true,
          options: [
            EditOption('Teaching', 'Teaching'),
            EditOption('Non-Teaching', 'Non-Teaching')
          ]),
      EditField('date_resigned', 'Date Resigned', kind: FieldKind.date),
      EditField('employment_status', 'Employee Status',
          kind: FieldKind.dropdown,
          required: true,
          options: [
            EditOption('active', 'Active'),
            EditOption('inactive', 'Inactive'),
            EditOption('separated', 'Separated'),
            EditOption('resigned', 'Resigned')
          ]),
      EditField('date_hired', 'Date Hired',
          kind: FieldKind.date, required: true),
    ];

List<EditField> addEmployeeFields() => const [
      EditField('full_name', 'Full Name', required: true),
      EditField('bio_number', 'Bio Number', required: true),
      EditField('gender', 'Gender',
          kind: FieldKind.dropdown,
          required: true,
          options: [
            EditOption('Male', 'Male'),
            EditOption('Female', 'Female')
          ]),
      EditField('civil_status', 'Civil Status',
          kind: FieldKind.dropdown,
          required: true,
          options: [
            EditOption('Single', 'Single'),
            EditOption('Married', 'Married'),
            EditOption('Widowed', 'Widowed'),
            EditOption('Separated', 'Separated')
          ]),
      EditField('birth_date', 'Birth Date',
          kind: FieldKind.date, required: true),
      EditField('address', 'Address',
          kind: FieldKind.multiline, lines: 2, required: true),
      EditField('contact_number', 'Contact Number', required: true),
      EditField('email', 'Email'),
      EditField('education_level', 'Educational Attainment', required: true),
      EditField('school_graduated', 'School Graduated', required: true),
      EditField('degree_course', 'Degree / Course', required: true),
      EditField('guardian_name', 'Guardian Name', required: true),
      EditField('guardian_relationship', 'Guardian Relationship',
          required: true),
      EditField('guardian_contact', 'Guardian Contact', required: true),
      EditField('guardian_address', 'Guardian Address',
          kind: FieldKind.multiline, lines: 2, required: true),
      EditField('designation', 'Designation', required: true),
      EditField('employee_type', 'Employee Type',
          kind: FieldKind.dropdown,
          required: true,
          options: [
            EditOption('full_time', 'Full Time'),
            EditOption('probationary', 'Probationary'),
            EditOption('part_time', 'Part Time'),
            EditOption('staff', 'Staff'),
            EditOption('faculty_staff', 'Faculty / Staff')
          ]),
      EditField('teaching_status', 'Teaching Status',
          kind: FieldKind.dropdown,
          required: true,
          options: [
            EditOption('Teaching', 'Teaching'),
            EditOption('Non-Teaching', 'Non-Teaching')
          ]),
      EditField('employment_status', 'Employee Status',
          kind: FieldKind.dropdown,
          required: true,
          options: [
            EditOption('active', 'Active'),
            EditOption('inactive', 'Inactive'),
            EditOption('separated', 'Separated'),
            EditOption('resigned', 'Resigned')
          ]),
      EditField('date_hired', 'Date Hired',
          kind: FieldKind.date, required: true),
    ];

const employeeKeys = [
  'full_name',
  'bio_number',
  'gender',
  'civil_status',
  'birth_date',
  'address',
  'contact_number',
  'email',
  'education_level',
  'school_graduated',
  'degree_course',
  'guardian_name',
  'guardian_relationship',
  'guardian_contact',
  'guardian_address',
  'designation',
  'employee_type',
  'teaching_status',
  'employment_status',
  'date_hired',
  'starting_date',
  'date_resigned',
  'current_salary',
  'license_summary',
  'notes'
];
const contractKeys = [
  'contract_type',
  'contract_start_date',
  'duration_months',
  'contract_end_date',
  'status',
  'attachment_url'
];
const licenseKeys = [
  'license_name',
  'license_number',
  'issued_date',
  'expiry_date',
  'status',
  'attachment_url'
];
const certificateKeys = [
  'certificate_type',
  'certificate_name',
  'certificate_number',
  'issued_date',
  'expiry_date',
  'status',
  'attachment_url'
];

Map<String, dynamic> extractKeys(Map<String, dynamic> data, List<String> keys) {
  final out = <String, dynamic>{};
  for (final key in keys) {
    Object? value;
    if (data.containsKey(key)) value = data[key];
    final isContract = keys.contains('contract_type');
    final isLicense = keys.contains('license_name');
    final isCertificate = keys.contains('certificate_name');
    if (key == 'status') {
      value = isContract
          ? data['contract_status']
          : isLicense
              ? data['license_status']
              : isCertificate
                  ? data['certificate_status']
                  : data[key];
    }
    if (key == 'attachment_url') {
      value = isContract
          ? data['contract_attachment_url']
          : isLicense
              ? data['license_attachment_url']
              : isCertificate
                  ? data['certificate_attachment_url']
                  : data[key];
    }
    if (key == 'issued_date')
      value = isLicense
          ? data['license_issued_date']
          : isCertificate
              ? data['certificate_issued_date']
              : data[key];
    if (key == 'expiry_date')
      value = isLicense
          ? data['license_expiry_date']
          : isCertificate
              ? data['certificate_expiry_date']
              : data[key];
    if (value != null && value.toString().trim().isNotEmpty) out[key] = value;
  }
  return out;
}

bool hasUsefulValue(Map<String, dynamic> data, List<String> keys) =>
    keys.any((k) => data[k] != null && data[k].toString().trim().isNotEmpty);

Object? parseFieldValue(String text, FieldKind kind) {
  final value = text.trim();
  if (value.isEmpty) return null;
  if (kind == FieldKind.number)
    return num.tryParse(value.replaceAll(RegExp(r'[^0-9.\-]'), ''));
  if (kind == FieldKind.integer)
    return int.tryParse(value.replaceAll(RegExp(r'[^0-9\-]'), ''));
  if (kind == FieldKind.date) return toIsoDateInput(value);
  return value;
}

Object? emptyToNull(Object? value) {
  if (value == null) return null;
  final text = value.toString().trim();
  return text.isEmpty ? null : value;
}

String? optionValueOrFirst(
    String? raw, List<EditOption> options, bool required) {
  final values = options.map((o) => o.value).toSet();
  if (raw != null && raw.isNotEmpty && values.contains(raw)) return raw;
  if (required && options.isNotEmpty) return options.first.value;
  if (!required && raw != null && raw.isNotEmpty && values.contains(raw))
    return raw;
  return null;
}

List<EditOption> uniqueOptions(List<EditOption> options) {
  final seen = <String>{};
  final out = <EditOption>[];
  for (final o in options) {
    if (seen.add(o.value)) out.add(o);
  }
  return out;
}

Map<String, dynamic> normalizeRow(Map<String, dynamic> row) {
  final out = Map<String, dynamic>.from(row);
  if (out['employees'] is Map)
    out['employee_name'] = out['employees']['full_name'];
  if (out['ranking_cycles'] is Map)
    out['cycle_name'] = out['ranking_cycles']['name'];
  if (out.containsKey('appointment')) {
    final appointmentText = '${out['appointment'] ?? ''}'.trim();
    final parts = appointmentText.split(RegExp(r'\s+-\s+'));
    if (parts.length >= 2 &&
        (parts.first.toLowerCase().contains('full') ||
            parts.first.toLowerCase().contains('probationary'))) {
      out['appointment_category'] = parts.first;
      out['appointment_title'] = parts.skip(1).join(' - ');
    } else {
      out['appointment_category'] = '-';
      out['appointment_title'] =
          appointmentText.isEmpty ? '-' : appointmentText;
    }
  }
  if (out['date_hired'] == null || out['date_hired'].toString().isEmpty)
    out['date_hired'] = out['starting_date'];
  out['date_hired_display'] = out['date_hired'] ?? out['starting_date'];
  out['date_resigned_display'] = out['date_resigned'];
  if (out.containsKey('contract_end_date'))
    out['days_left'] = daysLeft(out['contract_end_date']);
  return out;
}

Object? valueFor(Map<String, dynamic> row, String key) =>
    normalizeRow(row)[key];

String searchableText(Map<String, dynamic> row) => row.values
    .map((v) {
      if (v is Map) return v.values.join(' ');
      return '$v';
    })
    .join(' ')
    .toLowerCase();

int compareRows(
    Map<String, dynamic> a, Map<String, dynamic> b, String key, bool asc) {
  final av = valueFor(a, key);
  final bv = valueFor(b, key);
  final an = num.tryParse('${av ?? ''}');
  final bn = num.tryParse('${bv ?? ''}');
  int result;
  if (an != null && bn != null) {
    result = an.compareTo(bn);
  } else {
    result =
        formatValue(av).toLowerCase().compareTo(formatValue(bv).toLowerCase());
  }
  return asc ? result : -result;
}

bool looksLikeDateText(String text) =>
    RegExp(r'^\d{4}-\d{2}-\d{2}').hasMatch(text.trim()) ||
    RegExp(r'^[A-Za-z]+\s+\d{1,2},\s*\d{4}$').hasMatch(text.trim()) ||
    RegExp(r'^\d{1,2}[-/]\d{1,2}[-/]\d{4}$').hasMatch(text.trim());

DateTime? parseFlexibleDate(Object? value) {
  if (value == null) return null;
  final text = value.toString().trim();
  if (text.isEmpty || text == '-') return null;

  final compact = RegExp(r'^(\d{2})(\d{2})(\d{4})$').firstMatch(text);
  if (compact != null) {
    try {
      return DateFormat('MM/dd/yyyy').parseStrict(
          '${compact.group(1)!}/${compact.group(2)!}/${compact.group(3)!}');
    } catch (_) {}
  }

  final iso = RegExp(r'^(\d{4})-(\d{2})-(\d{2})').firstMatch(text);
  if (iso != null) {
    return DateTime.tryParse('${iso.group(1)}-${iso.group(2)}-${iso.group(3)}');
  }
  for (final pattern in const [
    'MM/dd/yyyy',
    'M/d/yyyy',
    'MM-dd-yyyy',
    'M-d-yyyy',
    'MMMM dd, yyyy',
    'MMMM d, yyyy',
    'MMM dd, yyyy',
    'MMM d, yyyy',
  ]) {
    try {
      return DateFormat(pattern).parseStrict(text);
    } catch (_) {}
  }
  return null;
}

String formatDateLong(Object? value) {
  final parsed = parseFlexibleDate(value);
  if (parsed == null) return formatValueRaw(value);
  return DateFormat('MMMM dd, yyyy').format(parsed);
}

String? toIsoDateInput(Object? value) {
  final parsed = parseFlexibleDate(value);
  if (parsed == null)
    return value == null || value.toString().trim().isEmpty
        ? null
        : value.toString().trim();
  return DateFormat('yyyy-MM-dd').format(parsed);
}

String formatValueRaw(Object? value) {
  if (value == null) return '-';
  final text = value.toString();
  if (text.trim().isEmpty) return '-';
  return text;
}

String formatValue(Object? value) {
  if (value == null) return '-';
  final text = value.toString();
  if (text.trim().isEmpty) return '-';
  if (looksLikeDateText(text)) return formatDateLong(text);
  return text;
}

String formatEditValue(Object? value) {
  if (value == null) return '';
  final raw = formatValueRaw(value);
  if (raw == '-') return '';
  return looksLikeDateText(raw) ? formatDateLong(raw) : raw;
}

String formatMoneyEdit(Object? value) {
  final text = formatMoney(value);
  return text == '-' ? '' : text;
}

num? parseMoneyInput(String text) {
  final cleaned = text.replaceAll(RegExp(r'[^0-9.\-]'), '');
  if (cleaned.trim().isEmpty) return null;
  return num.tryParse(cleaned);
}

String formatDetailValue(Object? value, String key) {
  if (key.contains('salary')) return formatMoney(value);
  if (key.contains('date')) return formatDateLong(value);
  return formatValue(value);
}

String formatMoney(Object? value) {
  final n = num.tryParse('${value ?? ''}');
  if (n == null) return formatValue(value);
  return NumberFormat.currency(symbol: 'PHP ', decimalDigits: 2).format(n);
}

String formatNumber(Object? value) {
  final n = num.tryParse('${value ?? ''}');
  if (n == null) return formatValue(value);
  return n % 1 == 0 ? n.toInt().toString() : n.toStringAsFixed(2);
}

int? daysLeft(Object? date) {
  if (date == null) return null;
  final parsed = parseFlexibleDate(date);
  if (parsed == null) return null;
  final today = DateTime.now();
  final base = DateTime(today.year, today.month, today.day);
  return DateTime(parsed.year, parsed.month, parsed.day)
      .difference(base)
      .inDays;
}

String normalizeName(String input) =>
    input.trim().toLowerCase().replaceAll(RegExp(r'\s+'), ' ');
String normalizeRankKey(String input) =>
    input.toLowerCase().replaceAll(RegExp(r'[^a-z0-9]+'), '');
String titleCase(String input) => input
    .split('_')
    .map((w) => w.isEmpty ? w : '${w[0].toUpperCase()}${w.substring(1)}')
    .join(' ');
String escapeHtml(String input) => input
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#39;');

void showSnack(BuildContext context, String message) {
  ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(message)));
}

const incidentResponseStatuses = <String>[
  'Waiting for Response',
  'Responded On Time',
  'Responded Late',
  'Waive the Right',
];

const incidentNodStatuses = <String>[
  'Pending',
  'Resolved',
  '1st Warning',
  '2nd Warning',
  '3rd Warning',
  'For Conference',
  'Non-Renewal',
  'Dismissal',
];

String incidentStatusValue(Object? raw, List<String> options, String fallback) {
  final value = '${raw ?? ''}'.trim();
  return options.contains(value) ? value : fallback;
}

Widget incidentStatusDropdown({
  required BuildContext context,
  required Map<String, dynamic> row,
  required String field,
  required List<String> options,
  required String fallback,
  required VoidCallback refresh,
}) {
  final value = incidentStatusValue(row[field], options, fallback);
  return DropdownButtonHideUnderline(
    child: DropdownButton<String>(
      value: value,
      isExpanded: true,
      icon: const Icon(Icons.arrow_drop_down_rounded, size: 18),
      borderRadius: BorderRadius.circular(14),
      selectedItemBuilder: (_) => [
        for (final option in options)
          Align(alignment: Alignment.centerLeft, child: StatusChip(option)),
      ],
      items: [
        for (final option in options)
          DropdownMenuItem<String>(
            value: option,
            child: Text(option,
                overflow: TextOverflow.ellipsis,
                style: const TextStyle(fontSize: 12.5)),
          ),
      ],
      onChanged: (next) async {
        if (next == null || next == value) return;
        try {
          await db.from('incident_reports').update({field: next}).eq('id', row['id']);
          refresh();
          if (context.mounted) showSnack(context, '${titleCase(field)} Updated.');
        } catch (e) {
          if (context.mounted) showSnack(context, 'Update Failed: $e');
        }
      },
    ),
  );
}

Future<List<dynamic>> loadIncidentReports({int limit = 1500}) => db
    .from('incident_reports')
    .select(
        'id, employee_id, ir, date_submitted, nte_date_received, explanation_date_submitted, response_status, nod, date_received, employees(full_name)')
    .order('date_submitted', ascending: false)
    .limit(limit);

class IncidentReportPage extends StatelessWidget {
  const IncidentReportPage({super.key});

  @override
  Widget build(BuildContext context) => PageFrame(
        title: 'Incident Report',
        subtitle:
            'Track employee IR, NTE, explanation deadline, NOD, and received dates.',
        child: CrudTable(
          load: () => activeOnlyRows(loadIncidentReports()),
          searchHint: 'Search employee, IR, NTE, explanation, or NOD',
          addLabel: 'Add Incident Report',
          reportTitle: 'Incident Report',
          archiveTableName: 'incident_reports',
          archiveModuleName: 'Incident Report',
          columns: const [
            GridCol('employee_name', 'Employee', flex: 3, primary: true),
            GridCol('ir', 'IR', flex: 2),
            GridCol('date_submitted', 'Date Submitted', flex: 2),
            GridCol('nte_date_received', 'NTE Date Received', flex: 2),
            GridCol('explanation_date_submitted', 'Explanation Date Submitted',
                flex: 2),
            GridCol('response_status', 'Response Status',
                flex: 2, isStatus: true),
            GridCol('nod', 'NOD', flex: 2, isStatus: true),
            GridCol('date_received', 'Date Received', flex: 2),
          ],
          onAdd: (ctx, refresh) => editIncidentReport(ctx, null, refresh),
          cellBuilder: (ctx, row, column, refresh) {
            if (column.key == 'response_status') {
              return incidentStatusDropdown(
                context: ctx,
                row: row,
                field: 'response_status',
                options: incidentResponseStatuses,
                fallback: 'Waiting for Response',
                refresh: refresh,
              );
            }
            if (column.key == 'nod') {
              return incidentStatusDropdown(
                context: ctx,
                row: row,
                field: 'nod',
                options: incidentNodStatuses,
                fallback: 'Pending',
                refresh: refresh,
              );
            }
            return null;
          },
          onView: viewIncidentReport,
          onEdit: editIncidentReport,
          onDelete: (row) =>
              db.from('incident_reports').delete().eq('id', row['id']),
        ),
      );
}

String? incidentReportComputedExplanationDate(String nteText) {
  final parsed = parseFlexibleDate(nteText);
  if (parsed == null) return null;
  return DateFormat('yyyy-MM-dd').format(parsed.add(const Duration(days: 3)));
}

String incidentReportDateEditText(dynamic value) {
  final text = formatEditValue(value);
  if (text.trim().isEmpty) return '';
  final parsed = parseFlexibleDate(text);
  return parsed == null ? text : DateFormat('MM/dd/yyyy').format(parsed);
}

Widget incidentReportDateBox({
  required BuildContext context,
  required String label,
  required TextEditingController controller,
  bool readOnly = false,
  bool required = false,
  String? helperText,
  ValueChanged<String>? onChanged,
}) =>
    SizedBox(
      width: 354,
      child: TextFormField(
        controller: controller,
        readOnly: true,
        enableInteractiveSelection: false,
        decoration: InputDecoration(
          labelText: label,
          hintText: readOnly ? null : 'MM/DD/YYYY',
          helperText: helperText,
          suffixIcon: const Icon(Icons.calendar_month_rounded),
          fillColor: readOnly ? _surfaceSoft : null,
        ),
        validator: readOnly
            ? null
            : (value) {
                final text = value?.trim() ?? '';
                if (required && text.isEmpty) return 'Required';
                if (text.isNotEmpty && parseFlexibleDate(text) == null) {
                  return 'Invalid date';
                }
                return null;
              },
        onTap: readOnly
            ? null
            : () => pickDateIntoController(
                  context,
                  controller,
                  afterPick: () => onChanged?.call(controller.text),
                ),
      ),
    );

Future<Map<String, dynamic>?> showIncidentReportDialog(
    BuildContext context, Map<String, dynamic>? row) async {
  final isAdd = row == null;
  final source = normalizeRow(row ?? {});
  final employees = await employeeOptions();
  String? employeeId = isAdd ? null : source['employee_id']?.toString();

  final ir = TextEditingController(text: formatEditValue(source['ir']));
  final dateSubmitted = TextEditingController(
      text: incidentReportDateEditText(source['date_submitted']));
  final nteDateReceived = TextEditingController(
      text: incidentReportDateEditText(source['nte_date_received']));
  final explanationDate = TextEditingController(
      text: incidentReportDateEditText(
          source['explanation_date_submitted']));
  final dateReceived = TextEditingController(
      text: incidentReportDateEditText(source['date_received']));

  final formKey = GlobalKey<FormState>();

  void recomputeExplanationDate() {
    final computed =
        incidentReportComputedExplanationDate(nteDateReceived.text);
    explanationDate.text = computed == null
        ? ''
        : DateFormat('MM/dd/yyyy').format(parseFlexibleDate(computed)!);
  }

  if (explanationDate.text.trim().isEmpty &&
      nteDateReceived.text.trim().isNotEmpty) {
    recomputeExplanationDate();
  }

  final result = await showDialog<Map<String, dynamic>>(
    context: context,
    builder: (_) => StatefulBuilder(
      builder: (context, setDialogState) => AlertDialog(
        title: Text(isAdd ? 'Add Incident Report' : 'Edit Incident Report'),
        content: SizedBox(
          width: 820,
          child: Form(
            key: formKey,
            child: SingleChildScrollView(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const DialogSectionTitle('Employee Information'),
                  if (isAdd)
                    employeeAutocompleteField(
                      employees: employees,
                      employeeId: employeeId,
                      width: 728,
                      onEmployeeChanged: (value) =>
                          setDialogState(() => employeeId = value),
                    )
                  else
                    ReadOnlyEmployeeBox(linkedEmployeeName(source)),
                  const SizedBox(height: 16),
                  const DialogSectionTitle('Incident Report Information'),
                  Wrap(spacing: 14, runSpacing: 14, children: [
                    SizedBox(
                      width: 354,
                      child: TextFormField(
                        controller: ir,
                        decoration: const InputDecoration(labelText: 'Incident Report'),
                        validator: (value) =>
                            value == null || value.trim().isEmpty
                                ? 'Required'
                                : null,
                      ),
                    ),
                    incidentReportDateBox(
                      context: context,
                      label: 'Date Submitted',
                      controller: dateSubmitted,
                    ),
                    incidentReportDateBox(
                      context: context,
                      label: 'NTE Date Received',
                      controller: nteDateReceived,
                      onChanged: (_) =>
                          setDialogState(recomputeExplanationDate),
                    ),
                    if (!isAdd)
                      incidentReportDateBox(
                        context: context,
                        label: 'Explanation Date Submitted',
                        controller: explanationDate,
                        readOnly: true,
                        helperText: 'Auto-computed: 3 days after NTE date',
                      ),
                    if (!isAdd)
                      incidentReportDateBox(
                        context: context,
                        label: 'Date Received',
                        controller: dateReceived,
                      ),
                  ]),
                ],
              ),
            ),
          ),
        ),
        actions: [
          TextButton(
              onPressed: () => Navigator.pop(context),
              child: const Text('Cancel')),
          FilledButton(
            onPressed: () {
              recomputeExplanationDate();
              if (!formKey.currentState!.validate()) return;
              Navigator.pop(
                  context,
                  <String, dynamic>{
                    if (isAdd) 'employee_id': employeeId,
                    'ir': ir.text.trim(),
                    'date_submitted': toIsoDateInput(dateSubmitted.text),
                    'nte_date_received': toIsoDateInput(nteDateReceived.text),
                    'explanation_date_submitted':
                        incidentReportComputedExplanationDate(
                            nteDateReceived.text),
                    if (isAdd) 'response_status': 'Waiting for Response',
                    if (isAdd) 'nod': 'Pending',
                    'date_received': toIsoDateInput(dateReceived.text),
                  }..removeWhere((_, value) =>
                      value == null || value.toString().trim().isEmpty));
            },
            child: const Text('Save'),
          ),
        ],
      ),
    ),
  );

  // Navigator.pop completes the dialog future before the route's reverse
  // transition has necessarily finished. Keep these controllers alive until
  // the closing widgets have been fully removed from the tree; disposing them
  // immediately can trigger Flutter's _dependents.isEmpty assertion on web.
  await Future<void>.delayed(const Duration(milliseconds: 300));
  for (final controller in [
    ir,
    dateSubmitted,
    nteDateReceived,
    explanationDate,
    dateReceived,
  ]) {
    controller.dispose();
  }

  return result;
}

Future<void> editIncidentReport(BuildContext context, Map<String, dynamic>? row,
    VoidCallback refresh) async {
  final data = await showIncidentReportDialog(context, row);
  if (data == null) return;
  await saveRow(context, 'incident_reports', row == null ? null : row['id'],
      data, refresh);
}

Future<void> viewIncidentReport(
    BuildContext context, Map<String, dynamic> row) async {
  final normalized = normalizeRow(row);
  await showDialog<void>(
    context: context,
    builder: (_) => AlertDialog(
      title:
          Text('Incident Report - ${formatValue(normalized['employee_name'])}'),
      content: SizedBox(
        width: 820,
        child: SingleChildScrollView(
          child:
              Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
            detailSection('Incident Report Information', normalized, const {
              'Employee': 'employee_name',
              'IR': 'ir',
              'Date Submitted': 'date_submitted',
              'NTE Date Received': 'nte_date_received',
              'Explanation Date Submitted': 'explanation_date_submitted',
              'Response Status': 'response_status',
              'NOD': 'nod',
              'Date Received': 'date_received',
            }),
          ]),
        ),
      ),
      actions: [
        TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Close')),
      ],
    ),
  );
}
