# Fixes:

## Guard duty board title always rendered in English regardless of the viewer's own language:
- The header above the weekday tabs ("Guard duty schedule (<course>)") was built as a plain JS
  string concatenation in the OWL template, which the i18n extractor never sees - it always
  showed English text no matter what language the viewer's account was set to. Moved to a
  translated `_t()` getter instead, so it now follows the account's own language like every
  other label on the screen.

## "Absences table" tab mislabelled as "Guard duty table":
- The second tab (who's missing and who's covering for them, one row per time block) was
  labelled "Guard duty table", which read as a duplicate of the schedule tab's own name rather
  than describing what that tab actually shows. Renamed to "Absences table" (and its Catalan/
  Spanish translations updated to match).

## PDF export always printed the timetable, even with the absences table on screen:
- Clicking "PDF" always exported the plain schedule/timetable view, regardless of which of the
  two tabs (schedule or absences table) was actually being looked at. The export now prints
  whichever tab is active: the timetable, or the absences table (who's missing, what needs
  covering, who's on guard) - built from the very same board data, no extra request.

# Related with:
- Closes #442
