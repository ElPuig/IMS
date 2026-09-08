# Technical Reference: `ems.teaching_reduction_type`

## Overview

`ems.teaching_reduction_type` catalogues entitlements that add extra weekly teaching hours to a
teacher's schedule summary without occupying a real schedule slot — e.g. an age-based reduction
("Reduction for teachers aged 55 and over", 2h). Unlike [`ems.non_teaching_type`](non_teaching_type.md),
which represents a real period on the weekly grid (a guard duty, a break), a reduction type is
never scheduled on a calendar block: it is picked directly on the teacher's own `hr.employee`
record (`teaching_reduction_ids`, a Many2many) and simply added, as extra rows, to the "Weekly
teaching hours" column of [`get_schedule_hours_summary()`](working_schedule.md) — a teacher with
16h of real classes and a 2h reduction shows 18h total (developer's own call: the reduction is
counted as positive hours added to the total, not subtracted from a requirement).

**Module file:** `models/employees/teaching_reduction_type.py`

---

## Data Model

### Fields

| Field | Type | Required | Stored | Description |
|-------|------|----------|--------|-------------|
| `code` | `Char` | Yes | Yes | Unique code |
| `name` | `Char` (`translate=True`) | Yes | Yes | Display name |
| `reduction_hours` | `Integer` | Yes | Yes | Extra weekly teaching hours this entitlement adds |
| `active` | `Boolean` (`default=True`) | No | Yes | Standard archive flag |

`_order = "name"`; `unique_code` SQL constraint. Deliberately no `sequence` field (unlike
`ems.non_teaching_type`) — with no consuming code needing a custom manual order, alphabetical by
`name` is enough (developer feedback, 2026-09-07).

---

## Access Control

Defined in `security/ir.model.access.csv` (lines 102–104).

| Role | Create | Read | Write | Delete | Group XML ID |
|------|:------:|:----:|:-----:|:------:|--------------|
| Department Chief | ✓ | ✓ | ✓ | ✓ | `ems.group_department_chief` |
| Teacher | — | ✓ | — | — | `ems.group_teacher` |
| Secretary | — | ✓ | — | — | `ems.group_secretary` |

Same convention as `ems.non_teaching_type`: the admin group here is `group_department_chief`, not
`group_academic_admin`, since this is a scheduling concept department chiefs manage directly.

---

## Integration Map

| Model | Field | Relation | Description |
|-------|-------|----------|--------------|
| `hr.employee` (`ems_employee_base`) | `teaching_reduction_ids` | Many2many (`hr_employee_public_ems_teaching_reduction_type_rel`) | The reduction types assigned to this teacher — several can apply at once |
| `resource.calendar` (`ems_working_schedule`) | `get_schedule_hours_summary()` | — | Folds each of the employee's `teaching_reduction_ids` into the "teaching" bucket as an extra row (`label`, `hours`), summed into the column's total |

`teaching_reduction_ids` is declared on `ems_employee_base` (an `AbstractModel` inherit of
`hr.employee.base`), the same way `role_ids` is — with an explicit `relation`/`column1`/`column2`,
since Odoo would otherwise create two separate relation tables (one for `hr.employee.public`, one
for `hr.employee.base`).

See [Working schedules](working_schedule.md) for the full `get_schedule_hours_summary()` computation.

---

## Views

| View | File | Notes |
|------|------|-------|
| List | `views/community/teaching_reduction_type/list.xml` | — |
| Form | `views/community/teaching_reduction_type/form.xml` | — |
| Action + Menu | `views/community/teaching_reduction_type/menu.xml` | Sibling of `menu_non_teaching_types`, under `menu_community_config_schedules` |
| `hr.employee` form | `views/community/employee/form.xml` | `teaching_reduction_ids` shown as `many2many_tags` in a new "Teaching hour reductions" group on the "Human Resources" tab (`hr_settings`), visible only for `employee_type == 'teacher'` |

---

## Seed Data

`data/main/ems.teaching_reduction_type.csv` seeds one record: `R55` / "Reduction for teachers aged
55 and over" / 2 hours.
