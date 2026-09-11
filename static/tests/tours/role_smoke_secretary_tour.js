/** @odoo-module **/

import { registry } from "@web/core/registry";
import { roleSmokeSteps } from "./role_smoke_common";

// See role_smoke_common.js for the crawler itself and CLAUDE.md's "Per-role smoke tours".
// `secretary` has the heaviest ir.model.access.csv footprint of any EMS role (70 rows) and
// does not imply hr.group_hr_user either.
registry.category("web_tour.tours").add("ems_role_smoke_secretary", {
    test: true,
    url: "/odoo",
    steps: () => roleSmokeSteps("Crawl every menu/action reachable by a secretary user"),
});
