/** @odoo-module **/

import { registry } from "@web/core/registry";
import { roleSmokeSteps } from "./role_smoke_common";

// See role_smoke_common.js for the crawler itself and CLAUDE.md's "Per-role smoke tours".
// `teacher` is the actual role from issue #434 and the spike this mechanism was first
// validated against.
registry.category("web_tour.tours").add("ems_role_smoke_teacher", {
    test: true,
    url: "/odoo",
    steps: () => roleSmokeSteps("Crawl every menu/action reachable by a plain teacher"),
});
