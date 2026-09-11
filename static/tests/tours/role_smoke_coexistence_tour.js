/** @odoo-module **/

import { registry } from "@web/core/registry";
import { roleSmokeSteps } from "./role_smoke_common";

// See role_smoke_common.js for the crawler itself and CLAUDE.md's "Per-role smoke tours".
// `coexistence` implies the same ems.group_teacher + ems.group_student_data_reader shape as
// orientation, but with write access rather than read-only.
registry.category("web_tour.tours").add("ems_role_smoke_coexistence", {
    test: true,
    url: "/odoo",
    steps: () => roleSmokeSteps("Crawl every menu/action reachable by a coexistence user"),
});
