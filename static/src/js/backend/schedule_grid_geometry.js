/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";

// Pure display/geometry helpers shared by every weekly schedule grid widget (the teacher's
// editable 'schedule_grid' and the read-only 'readonly_schedule_grid', reused as-is for both a
// group's and a student's own schedule) — day/hour layout math with no OWL state of its own, so
// it's a plain module rather than a shared component: the teacher's own editable widget's
// interactive surface (an edit buffer, none of which the read-only one needs) differs enough that
// forcing them through one component would leave a lot of dead code active in the read-only case.

export const PX_PER_HOUR = 64;
export const DEFAULT_START = 8;
export const DEFAULT_END = 20;
export const WEEKDAYS = [0, 1, 2, 3, 4];
// A short period (e.g. a 20-30min patio break) still needs room for a wrapped subject/reason
// label plus its time and room lines without visually spilling into the next period below it.
export const MIN_ENTRY_HEIGHT = 44;

// Mirrors ems.schedule_report_mixin.HOUR_EPSILON (Python) exactly, for the exact same reason: two
// hour_from/hour_to values meant to represent the same moment can differ by a tiny float remainder
// depending on how each was computed/entered (a framework's break stored as the literal
// '11.416667' vs a real period's own hour_from computed as '11 + 25/60' == 11.416666666666666).
// Without this tolerance, 'layoutOverlappingBlocks' below reads that hair's-width gap as a real
// overlap and needlessly splits the break block into columns - confirmed on GA1A's own morning
// break (2026-09-11), whose stored 11.416667 is a hair larger than the very next period's
// 11.416666666666666, even though the two are meant to be back-to-back, not overlapping.
const HOUR_EPSILON = 1 / 120;

export function dayLabels() {
    return [_t("Monday"), _t("Tuesday"), _t("Wednesday"), _t("Thursday"), _t("Friday")];
}

// 'hourPairs' is any iterable of {hour_from, hour_to} — callers pass their own entries so this
// stays free of any dependency on how those entries are stored (plain records, grouped blocks...).
// Fits tightly to whatever hours are actually present (an afternoon-only teacher, 14h-22h, sees
// exactly that — not a wider range padded out to a generic default) — DEFAULT_START/DEFAULT_END
// only apply as a fallback canvas when there's nothing to fit yet (an empty/new schedule).
export function computeBounds(hourPairs) {
    let start = null;
    let end = null;
    for (const { hour_from, hour_to } of hourPairs) {
        start = start === null ? Math.floor(hour_from) : Math.min(start, Math.floor(hour_from));
        end = end === null ? Math.ceil(hour_to) : Math.max(end, Math.ceil(hour_to));
    }
    return { start: start ?? DEFAULT_START, end: end ?? DEFAULT_END };
}

export function formatHour(hour) {
    return `${String(hour).padStart(2, "0")}:00`;
}

export function formatHourMinutes(value) {
    const hour = Math.floor(value);
    const minutes = Math.round((value - hour) * 60);
    return `${String(hour).padStart(2, "0")}:${String(minutes).padStart(2, "0")}`;
}

// Mirrors ems.schedule_report_mixin.REPORT_COLOR_PALETTE on the Python side (kept in sync by
// hand — different languages can't literally share one constant) — so a subject/activity tends
// to land on the same colour in the widget as it does in the PDF.
export const REPORT_COLOR_PALETTE = [
    "#5b8def", "#f4a261", "#2a9d8f", "#e76f51", "#8ecae6", "#ffb703",
    "#c77dff", "#06d6a0", "#ef476f", "#118ab2", "#bc6c25", "#9d4edd",
];

// Assigns each distinct 'key' its own colour, reused every time that key reappears, in
// first-seen (day, hour) order — the same "same subject/activity always gets the same colour"
// rule the PDF's own REPORT_COLOR_PALETTE/_report_color_key already follows. Only distinguishes
// colours *within* the entries actually passed in (a schedule's own subjects/activities), not
// across every subject that exists — there's no reason to reserve a colour for one this
// particular schedule never uses. 'items' is [{key, dayofweek, hour_from}, ...]; returns a
// Map<key, hexColor>.
export function buildColorMap(items) {
    const sorted = [...items].sort((a, b) => a.dayofweek - b.dayofweek || a.hour_from - b.hour_from);
    const colorByKey = new Map();
    for (const item of sorted) {
        if (!colorByKey.has(item.key)) {
            colorByKey.set(item.key, REPORT_COLOR_PALETTE[colorByKey.size % REPORT_COLOR_PALETTE.length]);
        }
    }
    return colorByKey;
}

// Assigns each block in 'blocks' (any objects carrying 'hour_from'/'hour_to') a '_column'/
// '_columnCount' pair so genuinely overlapping (not just identical-slot) blocks can be laid out
// side by side instead of silently stacking on top of each other — needed for a student's own
// schedule (unlike a single teacher's or one group's own aggregated view, several of a student's
// enrollments can be scheduled at truly different, partially-overlapping times: e.g. their main
// group's 9:00-10:00 class and a 9:30-10:15 elective through a different group). A single teacher
// or group's timeline structurally can't produce this (see the two callers below), but the
// algorithm is generic and harmless when it never finds a real overlap: every block just gets
// '_columnCount' 1 (the CSS default full-width layout, unchanged).
//
// Standard calendar-app "collision clustering" approach (the same shape Google/Outlook-style day
// views use): sort by start time, group into maximal runs of transitively-overlapping blocks
// ('flushCluster' below), then greedily assign each block in a cluster the leftmost column whose
// previous occupant has already ended — the cluster's own column count becomes every one of its
// blocks' shared '_columnCount' width divisor. Not guaranteed to be the mathematically optimal
// packing in every pathological case, but neither is any real calendar UI's — legible and correct
// (no block ever hides another) is the actual requirement here, not minimal column count.
export function layoutOverlappingBlocks(blocks) {
    const sorted = [...blocks].sort((a, b) => a.hour_from - b.hour_from || a.hour_to - b.hour_to);
    const layoutByBlock = new Map();
    let cluster = [];
    let clusterEnd = -Infinity;

    const flushCluster = () => {
        const columnEnds = [];
        for (const block of cluster) {
            let column = columnEnds.findIndex((end) => end <= block.hour_from);
            if (column === -1) {
                column = columnEnds.length;
                columnEnds.push(block.hour_to);
            } else {
                columnEnds[column] = block.hour_to;
            }
            layoutByBlock.set(block, column);
        }
        for (const block of cluster) {
            layoutByBlock.set(block, { column: layoutByBlock.get(block), columnCount: columnEnds.length });
        }
        cluster = [];
        clusterEnd = -Infinity;
    };

    for (const block of sorted) {
        if (cluster.length && block.hour_from >= clusterEnd - HOUR_EPSILON) {
            flushCluster();
        }
        cluster.push(block);
        clusterEnd = Math.max(clusterEnd, block.hour_to);
    }
    if (cluster.length) {
        flushCluster();
    }

    return sorted.map((block) => Object.assign(block, layoutByBlock.get(block)));
}
