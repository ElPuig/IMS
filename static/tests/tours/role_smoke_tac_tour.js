/** @odoo-module **/

import { registry } from "@web/core/registry";
import { roleSmokeSteps } from "./role_smoke_common";

// See role_smoke_common.js for the crawler itself and CLAUDE.md's "Per-role smoke tours".
// Deliberate negative control: unlike the other 4 roles in this roster, `tac` DOES imply
// hr.group_hr_user, so it should surface materially fewer (ideally zero) findings - confirming
// the crawler isn't simply noisy everywhere.
registry.category("web_tour.tours").add("ems_role_smoke_tac", {
    test: true,
    url: "/odoo",
    steps: () => roleSmokeSteps("Crawl every menu/action reachable by a TAC user"),
});
