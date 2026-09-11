# Changes:

## Employee Attendances menu reorganized:
- Overview, Correction Requests and Management are now grouped under a new "Attendance" submenu instead of sitting loose at the root, so the root menu reads as a short, ordered list (Attendance / Time off / Guard schedule / Reporting / Kiosk mode / Configuration) instead of a flat mix of unrelated screens.
- "Guard duty schedule" was renamed to "Guard schedule" (menu entry and screen title only; the two internal view-toggle buttons on that screen keep their original "Guard duty schedule"/"Guard duty table" labels).
- No permission changes: every screen keeps exactly the same visibility (`groups_id`) it had before, only its position in the menu tree moved.

## Calendar app menu hidden:
- The native "Calendar" root menu is deactivated for every user (not currently used at the centre), same pattern already used for other unused native menus (Contacts, To-do, Discuss, etc.).
