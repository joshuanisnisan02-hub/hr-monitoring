class HrLoginAccount {
  final String role;
  final String email;

  const HrLoginAccount({required this.role, required this.email});
}

const hrLoginAccounts = <HrLoginAccount>[
  HrLoginAccount(role: 'Admin', email: 'admin@hr-monitoring.local'),
  HrLoginAccount(role: 'HR', email: 'hr@hr-monitoring.local'),
];

bool isAllowedHrEmail(String? email) {
  if (email == null) return false;
  return hrLoginAccounts.any((account) => account.email.toLowerCase() == email.toLowerCase());
}

HrLoginAccount hrAccountForEmail(String? email) {
  return hrLoginAccounts.firstWhere(
    (account) => account.email.toLowerCase() == (email ?? '').toLowerCase(),
    orElse: () => hrLoginAccounts.first,
  );
}
