# Fixes:

## Guard (WC) and Guard (Break) schedule labels not translated:
- `ems.non_teaching_type` records `ems.non_teaching_gb` ("Guard (Break)") and `ems.non_teaching_gwc`
  ("Guard (WC)") had no `msgid` block at all in `i18n/ca_ES.po`/`i18n/es_ES.po` - unlike the plain
  "Guard" and "Break" types, which were already translated. Added the missing blocks (Catalan
  "Guàrdia (Pati)"/"Guàrdia (WC)", Spanish "Guardia (Patio)"/"Guardia (WC)"); verified in the DB
  that both records' `name` jsonb now carries `ca_ES`/`es_ES` keys after `./upgrade.sh`.
