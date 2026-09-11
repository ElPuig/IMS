# Changes:

## Guard duty board: patio and WC guard duties are now visually distinct:
- A guard duty whose time block is a break period, with no class running for anyone then, now
  gets a small "Break" label (translating to "Patio"/"Pati" in Spanish/Catalan, same as the rest
  of this label's own wording elsewhere) and a left-border accent (matching the colour already
  used for a break on the teacher's own weekly schedule) - and this now shows under "All levels"
  too, not only once a level filter narrows the board down, as it used to.
- A "Guard (WC)" duty specifically now shows a "(WC)" tag next to the teacher's name in the
  guard column, since - unlike a break-time guard - it can fall at any time of day and had no
  other way to be told apart from a plain guard duty.
- Caught during manual verification (developer report, 2026-09-11): an early version of this
  same label returned the Catalan/Spanish word directly from the source code ("Patio" instead of
  "Break"), so English readers saw "Patio" too - invisible from the Spanish/Catalan side, which
  is exactly why it wasn't caught by translation review alone. Fixed by keeping the source
  string in English and letting the existing `ca_ES`/`es_ES` translation do the rest, verified
  against the live `/web/webclient/translations/...` endpoint in all three languages.

# Fixes:

## Guard (WC) and Guard (Break) schedule labels not translated:
- `ems.non_teaching_type` records `ems.non_teaching_gb` ("Guard (Break)") and `ems.non_teaching_gwc`
  ("Guard (WC)") had no `msgid` block at all in `i18n/ca_ES.po`/`i18n/es_ES.po` - unlike the plain
  "Guard" and "Break" types, which were already translated. Added the missing blocks (Catalan
  "Guàrdia (Pati)"/"Guàrdia (WC)", Spanish "Guardia (Patio)"/"Guardia (WC)"); verified in the DB
  that both records' `name` jsonb now carries `ca_ES`/`es_ES` keys after `./upgrade.sh`.

# Internal changes:

## Guard duty board tour now logs in as a plain teacher, not admin:
- The feature-specific tour for the guard duty board was still logging in as `admin`, predating
  the Development workflow's "least-privileged role" rule (issue #434). Retrofitted to log in as
  a plain teacher - the actual least-privileged role that already has full read access to this
  screen - while extending the same tour with coverage for the two items above.
