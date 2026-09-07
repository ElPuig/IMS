# What's new

## Choice of whether an Esfera import may overwrite existing data:

The "Import from Esfera" wizard now asks upfront, through an "Overwrite existing data" checkbox
on its own form, what should happen to a student EMS already knows about. Left unticked (the
default), EMS's own data always wins: only fields that are currently empty get filled in from the
file, and students missing from EMS are created. Ticked, the file's values replace EMS's ones.
The same policy governs the family contacts (tutors/guardians) each row carries, which until now
followed a different and inconsistent one of their own.

# Fixes

## Esfera import no longer erases data when a column comes empty in the file:

Updating an existing student wrote the whole value dictionary with `existing.write(data)`, so any
column the export left empty overwrote whatever EMS held with a blank. Measured on a real CFGM
export of 247 students, all of them already in EMS: 31 would have silently lost the email address
on file. Family contacts were only half-protected (phone/mobile/email were guarded, but address
fields and notes were not). An empty cell now never blanks an existing value, in either mode.

## Esfera import reads every sheet of the workbook, not just the active one:

Only `wb.active` was read, so every other sheet was silently ignored. The same real CFGM export
splits its students across two sheets with no overlap whatsoever between them - 106 students in the
active one, 141 in the other - meaning 141 students would have been dropped without any error,
warning or hint in the result summary. Every sheet holding data is now imported; a sheet with no
recognisable header row (an empty or auxiliary tab) is skipped instead of aborting the file.

## Rows are no longer discarded in silence when the group column is empty:

A row whose "Grup Classe" cell was empty hit a bare `return` before anything was read, so it
vanished with no error, no warning and no log entry. The same real export has that column present
but empty in all 247 rows, so the whole import would have reported "0 created, 0 updated" with no
indication of why. The group is now optional: the row is imported without one, exactly as already
happened for a group code with no matching `ems.group`.

# Changes

## The student identifier is the only mandatory column in an Esfera file:

The wizard demanded 37 specific headers and aborted with a `UserError` listing whatever was
missing. The real CFGM export lacks two of them ("Tipus de via" and "Tutor 1 - país", both absent
from that particular Esfera column selection), so it could not be imported at all. Only
`Identificador de l'alumne/a` (IDALU/RALC) is required now - it is what matches a row to a student,
so it also doubles as the marker used to locate each sheet's header row. A row without it is
skipped and reported as a warning in the result summary rather than dropped silently.

## Imported notes are stacked on top of existing ones instead of replacing them:

The student's and tutor's notes field was overwritten wholesale on every import, discarding
anything a tutor had written by hand - 241 of the 247 students in the real export have notes in EMS
today. Each import now adds its own block on top of what is already there, stamped with the import
date and closed by a horizontal rule, so it stays visible when each block arrived and nothing is
ever lost.
