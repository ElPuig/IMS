# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class EmsGroupClassroomChangeWizard(models.TransientModel):
	_name = "ems.group_classroom_change_wizard"
	_description = "Resolve a group's schedule blocks left pending after a classroom change (issue #405)."

	group_id = fields.Many2one(string="Group", comodel_name="ems.group", required=True, readonly=True)
	conflict_line_ids = fields.One2many(
		string="Pending conflicts", comodel_name="ems.group_classroom_change_wizard_conflict_line", inverse_name="wizard_id")
	# NOTE: same "two mutually-exclusive buttons" pattern as the import wizard's own
	# 'continue_disabled' (views/community/working_schedules/import_wizard.xml) - Odoo's button
	# widget has no direct way to render a computed boolean as a literal HTML 'disabled' attribute,
	# so the view shows either the real 'action_confirm' button or an inert decoy depending on this.
	confirm_disabled = fields.Boolean(compute="_compute_confirm_disabled")

	@api.depends('conflict_line_ids.resolution', 'conflict_line_ids.left_space_id', 'conflict_line_ids.right_space_id')
	def _compute_confirm_disabled(self):
		for wizard in self:
			wizard.confirm_disabled = bool(wizard.conflict_line_ids.filtered(lambda line: not line._resolution_is_valid()))

	@api.model_create_multi
	def create(self, vals_list):
		"""Populates 'conflict_line_ids' server-side, from 'group_id', for any vals that doesn't
		already supply it - rather than a 'default_get' override. This wizard's whole record must
		already be PERSISTED (a real id) by the time its conflict-line pickers are edited in the
		browser: those edits go through onchange round-trips that, for a still-virtual (not yet
		created) parent's o2m children, only preserve the fields the list view itself declares -
		this line model's own required 'left_attendance_id'/'right_schedule_id' aren't among them
		(kept out of the view on purpose, same as the import wizard's own equivalent fields), so a
		virtual line would silently lose them the moment a room picker changes. Reached both by
		'ems.group.action_open_classroom_change_wizard()' (creates before ever opening the form)
		and directly in tests."""
		wizards = super().create(vals_list)
		for wizard in wizards:
			if not wizard.conflict_line_ids and wizard.group_id:
				wizard.conflict_line_ids = wizard._build_conflict_lines(wizard.group_id)
		return wizards

	def action_confirm(self):
		self.ensure_one()
		for line in self.conflict_line_ids:
			if not line._resolution_is_valid():
				raise ValidationError(_(
					"The resolution chosen for \"%(left)s\" is not valid yet - pick a room for both "
					"sides (different from each other) when reassigning, or a different resolution."
				) % {'left': line.left_label})
		for line in self.conflict_line_ids:
			line._apply_resolution()
		return {"type": "ir.actions.act_window_close"}

	def _build_conflict_lines(self, group):
		"""One (0, 0, {...}) command per still-unresolved pending block. Re-checks every pending
		block against 'group's CURRENT classroom rather than trusting the flag alone - the
		collision it was flagged for may have resolved itself since (e.g. the other session was
		independently archived), in which case '_resolve_or_flag_pending_block' moves it straight
		away and it never becomes a line here at all."""
		pending_blocks = self.env['resource.calendar.attendance'].search([
			('group_ids', '=', group.id),
			('space_pending_group_sync', '=', True),
		])
		commands = []
		for block in pending_blocks:
			for other, _same_teacher in group._resolve_or_flag_pending_block(block, group.space_id):
				commands.append((0, 0, {
					'left_attendance_id': block.id,
					'right_schedule_id': other.id,
					'kind': 'plain_conflict',
					'resolution': 'reassign_rooms',
					'left_label': self._block_label(block),
					'right_label': other.display_name,
					'left_group_key': "%s - %s" % (block.employee_id.display_name, block.subject_id.display_name),
					'left_space_id': group.space_id.id,
					'right_space_id': group.space_id.id,
				}))
		return commands

	def _block_label(self, block):
		weekday_label = dict(block._fields['dayofweek'].selection).get(block.dayofweek)
		return "%s - %s - %s (%s %s)" % (
			block.employee_id.display_name, block.subject_id.display_name,
			", ".join(block.group_ids.mapped('display_name')), weekday_label, self._format_hour_range(block))

	def _format_hour_range(self, block):
		return "%s-%s" % (self._format_hour(block.hour_from), self._format_hour(block.hour_to))

	def _format_hour(self, hour):
		return "%02d:%02d" % (int(hour), round((hour % 1) * 60))


class EmsGroupClassroomChangeWizardConflictLine(models.TransientModel):
	_name = "ems.group_classroom_change_wizard_conflict_line"
	_inherit = ["ems.working_schedules_import_wizard.conflict_mixin"]
	_description = "Group classroom-change wizard: room-conflict line for one pending teaching block."

	wizard_id = fields.Many2one(
		string="Wizard", comodel_name="ems.group_classroom_change_wizard", required=True, ondelete="cascade")
	# NOTE: 'left' is always the pending block belonging to the group whose classroom just changed;
	# 'right' is always the already-active 'ems.attendance_schedule' line it collides with - same
	# "left = the side that moved, right = the side that was already there" convention as the import
	# wizard's own 'external_conflict_line' (models/employees/working_schedule.py).
	left_attendance_id = fields.Many2one(
		string="Pending block", comodel_name="resource.calendar.attendance", required=True, readonly=True)
	right_schedule_id = fields.Many2one(
		string="Existing session", comodel_name="ems.attendance_schedule", required=True, readonly=True)

	def _apply_resolution(self):
		"""Applies this line's chosen 'resolution', then clears 'space_pending_group_sync' on
		'left_attendance_id' regardless of which one was picked - either way the admin has now made
		an explicit, informed decision about this block, so it stops being "pending".

		Bottom-up sync redesign, Phase 6 (2026-09-08): both sides now write ONLY
		'resource.calendar.attendance' (the pending block directly here; the existing session via
		'ems.attendance_schedule._relocate_via_calendar_blocks'/'_archive_via_calendar_blocks') and let
		the automatic hook keep 'ems.attendance_schedule'/'ems.attendance_template' correctly in
		sync as a consequence - this is exactly what fixes the real bug found on SMX1D/SMX2D
		(writing the schedule directly left the teacher's own calendar silently pointing at the old
		room), now fixed at the source instead of patched here."""
		self.ensure_one()
		block = self.left_attendance_id
		existing = self.right_schedule_id
		new_space = self.wizard_id.group_id.space_id
		if self.resolution == 'reassign_rooms':
			# NOTE: 'existing' moves FIRST - unlike the import wizard's own 'reassign_rooms' (whose
			# left side is still an unsaved node_cache entry, so only the right side ever touches the
			# DB), here BOTH sides are already real, active records: moving 'block' into
			# 'left_space_id' before 'existing' has vacated it would trip 'check_overlap' on a purely
			# transient state, even though the end result (both moved) is perfectly valid.
			if existing.space_id != self.right_space_id:
				existing._relocate_via_calendar_blocks(self.right_space_id)
			block.space_id = self.left_space_id.id
		elif self.resolution == 'prevail_left':
			# The pending block takes the group's new classroom; the session it collided with is
			# archived - same handling as the import wizard's own 'prevail_left' on an external
			# conflict (models/employees/working_schedule.py's '_continue_from_db_conflicts').
			existing._archive_via_calendar_blocks()
			block.space_id = new_space.id
		# 'prevail_right': the pending block keeps its current classroom for this slot - a deliberate,
		# accepted divergence from the group's own room from now on. Nothing to write on either side.
		block.space_pending_group_sync = False
