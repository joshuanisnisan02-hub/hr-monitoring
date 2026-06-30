from pathlib import Path
import re
import textwrap

p = Path('lib/main.dart')
s = p.read_text()

reference_block = """const Set<String> rankingFullTimeReferenceNames = <String>{
  "advincula, jezel c., lpt",
  "avenido jr., restituto., mbm, lpt",
  "villegas, beverly joy b., lpt",
  "bañes-ofiaza, maria sheena p., lpt",
  "beatingo, dave bryan j.",
  "behiga-semilla, charissa mae g., maed, lpt",
  "bernardo, julius m., lpt",
  "besonia, kwin y., mba",
  "bioco, aijelon g.",
  "borro, enarcisa p., maed, lpt",
  "cabidog, mary monica r., lpt",
  "cabrera, kristine j., mbm, lpt",
  "cabrera, princess kaye",
  "calle, reycart",
  "campilan, gremae",
  "cañales, janine hope",
  "caparoso, marie claire, lpt",
  "casi, irene w., rcrim",
  "castardo, mary dorothy yrenee, lpt",
  "cauntao karen grace, lpt",
  "celo, lisa l., rl",
  "cocjin, charry j., rn",
  "colipano, tessie r., phd, lpt",
  "cuyos, marites mbm",
  "cuyos, rosso, mbm, mit, lpt",
  "dapsan, eldie john, lpt",
  "david, elenito g.",
  "de vera, freden s. mbm, chra",
  "doña, cris d., lpt",
  "doyac, adrian lpt",
  "duran, leomil jay b., dbm-is, lpt",
  "duro, rogelio p. jr. dbm-hsm, lpt",
  "estrada, mark louie v.",
  "gabitan, raul a., lpt",
  "guarte, alnor g., mscrim",
  "gumalos, vladimir dave, rcrim",
  "honey maya maira d. bayucot, lpt",
  "jabonero, charles b., mm-hm",
  "lagura, jolly mae g., lpt",
  "lerog, chad angelo, mbm",
  "lerog, jeffrey, mbm, lpt",
  "lim, patricia abby m., lpt",
  "lupogan, andrea acerin, lpt",
  "macawile, flora mae, rcrim",
  "malla, jumbelyn",
  "malone, felcris maed lpt",
  "mamalinta, jehanie",
  "marey, melchor a., mscrim",
  "mijares, sheila mae",
  "miranda, kenneth r., maed, lpt",
  "molina, jonar m., mbm",
  "moreno, christopher ryan lpt",
  "nabua, john paul, lpt",
  "navarro, joevy j., maed, lpt",
  "navarro, jonarie",
  "nocete, richelle m., rcrim",
  "oliasa, razel y., lpt",
  "omega, egay",
  "pacatang, jennifer, lpt",
  "pacatang, joan, lpt",
  "pacheco, rodel, maed, lpt",
  "padayhag, nheco, dbm-hsm, lpt",
  "palasigue, sweetzel ann lpt",
  "palo, raevelyn magandam, lpt",
  "panelo, john paul, lpt",
  "pavillar, aiza b., lpt",
  "perez, joseph r",
  "petate, edward b., lpt",
  "quizon, katrina",
  "rodriguez, cerie joy m, lpt",
  "romarez, cindy",
  "rubinos, genesis joyce m., lpt",
  "sarona, arielle",
  "secretaria, stephen",
  "soriano, april joy lpt",
  "soriano, joanna lpt",
  "sumaylo, eddie, lpt",
  "tabanera, dodie m., lpt",
  "tabiliran, john michael lpt",
  "taguines, gene",
  "tagupa, marychell n., lpt",
  "tampos, carvin paul g.",
  "tobato, may maeh v., phd, lpt",
  "tomampos, ellah jessa g. dbm, lpt",
  "torcuator, dennis oliver g.",
  "tubiano, queen heart v.",
  "umadhay, juluis czar, lpt",
  "utay, honey babe erica b.",
  "venancio, daniuel p., lpt",
  "villanuea, rey, lpt",
};

const Set<String> rankingProbationaryReferenceNames = <String>{
  "abatayo, geoffrey ian p., lpt",
  "alonzo, beayonce miles m., lpt",
  "araza, alejandro roygbiv a., lpt",
  "del corro, ronalyn a., lpt",
  "delos santos, lawrence james p.",
  "emolaga, dianne t., lpt",
  "laurente iii, anastacio, lpt",
  "mediodia, kyan m.",
  "nanali, joanne b.",
  "palces, gemma b., lpt",
  "quiachon, jennifer m., lpt",
  "rivera, jeremie r.",
  "sese, amapil",
  "toribio, mary joy l., rsw",
  "yusof, saidah l., lpt",
};"""

start_existing = s.find('const Set<String> rankingFullTimeReferenceNames')
if start_existing != -1:
    end_existing = s.find('\n\nclass RankingPage extends StatefulWidget', start_existing)
    if end_existing == -1:
        raise SystemExit('Could not find end of existing ranking reference block')
    s = s[:start_existing] + reference_block + s[end_existing:]
else:
    marker = 'class RankingPage extends StatefulWidget'
    idx = s.find(marker)
    if idx == -1:
        raise SystemExit('RankingPage marker not found')
    s = s[:idx] + reference_block + "\n\n" + s[idx:]

old_filter = """  bool _matchesRankingFilter(Map<String, dynamic> row, String selected) {
    final text = '${row['appointment'] ?? ''}'.toLowerCase().replaceAll('_', ' ').replaceAll('-', ' ');
    final isFullTime = text.contains('full') && text.contains('time');
    final isProbationary = text.contains('probationary');
    if (selected == 'Full-time') return isFullTime;
    if (selected == 'Probationary') return isProbationary;
    return isFullTime || isProbationary;
  }"""

new_filter = """  bool _matchesRankingFilter(Map<String, dynamic> row, String selected) {
    final nameKey = normalizeName('${row['employee_name'] ?? ''}');
    final isFullTime = rankingFullTimeReferenceNames.contains(nameKey);
    final isProbationary = rankingProbationaryReferenceNames.contains(nameKey);
    if (selected == 'Full-time') return isFullTime;
    if (selected == 'Probationary') return isProbationary;
    return isFullTime || isProbationary;
  }"""

if old_filter in s:
    s = s.replace(old_filter, new_filter, 1)
else:
    start = s.find('  bool _matchesRankingFilter(Map<String, dynamic> row, String selected) {')
    if start == -1:
        raise SystemExit('Ranking filter start not found')
    end = s.find('\n\n  Future<List<dynamic>> _loadRankings()', start)
    if end == -1:
        raise SystemExit('Ranking filter end not found')
    s = s[:start] + new_filter + s[end:]

p.write_text(s)
