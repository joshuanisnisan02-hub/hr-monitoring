from pathlib import Path

p = Path('lib/main.dart')
s = p.read_text()
s = s.replace(
    """const publicClientKey = String.fromEnvironment('SUPABASE_PUBLIC_CLIENT_KEY');""",
    """const publicClientKey = String.fromEnvironment(
  'SUPABASE_PUBLIC_CLIENT_KEY',
  defaultValue: 'sb_publishable_QJuRm0RkkQfbgAnBPPxbYw_AtG0BK3o',
);""",
    1,
)
p.write_text(s)
