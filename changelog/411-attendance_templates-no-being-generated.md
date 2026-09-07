# Fixes

## Attendance templates silently disappearing when a teacher solo-teaches one subject to several groups:

Fixed a bug in the shared calendar → attendance-template sync used by both the working-schedules
importer and a live edit on a teacher's own Schedule tab. A solo teacher who teaches the same
subject to two or more different groups (no co-teaching involved) could see every one of their
attendance templates for that subject archived and never recreated on the next resync, even
though their calendar was completely correct and unchanged. Root cause: the reconciliation step
that decides which existing templates to keep matched by subject and teacher only, not by group,
so each group's own resync pass ended up treating the other group's still-valid template as
stale. Added a regression test reproducing the exact scenario, plus a migration that repairs any
existing production data left behind by this bug by rebuilding every attendance template fresh
from each teacher's current (correct) calendar - the same full-rebuild mechanism already used once
before for the original calendar-driven-templates rollout.

## Archived attendance templates now get deleted instead of piling up forever:

Every time a teacher's working schedule is re-imported (or edited live), any of their now-superseded
attendance templates used to be archived and kept forever, even when nothing was ever actually
recorded against them - repeatedly re-importing schedules to fix small details left hundreds of
dead, never-used records behind. A superseded template with no real attendance history anywhere in
its lines (checked including already-archived lines, not just active ones) is now deleted outright
instead; one with real history is still archived exactly as before, and the underlying safety check
that prevents ever deleting real attendance history got broadened to close a small gap (it used to
only check a template's active lines). A one-off migration cleans up the existing backlog of
already-archived, never-used templates the same way.
