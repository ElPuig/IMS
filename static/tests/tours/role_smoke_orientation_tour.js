/** @odoo-module **/

import { registry } from "@web/core/registry";
import { roleSmokeSteps } from "./role_smoke_common";

// See role_smoke_common.js for the crawler itself and CLAUDE.md's "Per-role smoke tours".
// `orientation` has zero direct ir.model.access.csv rows of its own - it relies entirely on
// implied groups (ems.group_teacher + ems.group_student_data_reader), making it the most
// fragile role on paper.
registry.category("web_tour.tours").add("ems_role_smoke_orientation", {
    test: true,
    url: "/odoo",
    steps: () => roleSmokeSteps("Crawl every menu/action reachable by an orientation/guidance user"),
});
