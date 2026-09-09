import os
import re

from odoo.tests.common import TransactionCase, tagged

MODULE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
SCANNED_EXTENSIONS = ('.py', '.xml', '.csv')
# 'temp' is the gitignored scratch folder: it holds raw centre exports (latin-1
# csv) that are not module source and blow up the utf-8 read below.
EXCLUDED_DIRS = {'docs', '.git', 'temp'}
# Suffix must start with a letter so this doesn't also match ems.group_<N>
# xmlids, which are demo records of the unrelated ems.group (class group) model.
GROUP_REF_RE = re.compile(r'ems\.group_[A-Za-z][A-Za-z0-9_]*')
# .py/.xml files can mention an ems.group_* TOKEN without it being a security-group reference
# at all - e.g. a model literally named 'ems.group_classroom_change_wizard' (an unrelated
# collision with this convention: it's about ems.group the CLASS-GROUP model, not a res.groups
# ACCESS group), mentioned in a docstring, a '_name' declaration, or a view's own 'name' field.
# Only trust a match in one of those two extensions when the same LINE also looks like one of
# this test's own documented reference shapes: 'groups="..."'/'groups_id' (XML), 'has_group(',
# or a '.ref(' call (Python's 'env.ref(...)'/'self.env.ref(...)', or XML's 'ref(...)' inside an
# eval). A .csv row's 'group_id:id' column is trusted unconditionally - a CSV data row IS the
# reference, by construction, never free-text prose that could coincidentally match.
REFERENCE_CONTEXT_RE = re.compile(r'groups\s*=|groups_id|has_group\(|\bref\(')


@tagged('post_install', '-at_install')
class TestSecurityGroupReferences(TransactionCase):
    """Every ems.group_* referenced from security/ir.model.access.csv,
    security/rules/*.xml, view/menu groups="..." attributes, groups_id
    eval="[(4, ref('...'))]" and has_group()/env.ref() calls in Python must
    resolve to a res.groups record that actually exists (CLAUDE.md's Coding
    standards). This catches stale group names left over from a rename (e.g.
    ems.group_admin -> ems.group_academic_admin) that would otherwise only
    surface as a broken upgrade after merging an old branch."""

    def test_group_refs_resolve(self):
        violations = []
        seen_tokens = {}
        for dirpath, dirnames, filenames in os.walk(MODULE_ROOT):
            dirnames[:] = [d for d in dirnames if d not in EXCLUDED_DIRS and not d.startswith('.')]
            for filename in filenames:
                if not filename.endswith(SCANNED_EXTENSIONS):
                    continue
                path = os.path.join(dirpath, filename)
                if os.path.abspath(path) == os.path.abspath(__file__):
                    continue
                trust_any_match = filename.endswith('.csv')
                with open(path, encoding='utf-8') as source_file:
                    for lineno, line in enumerate(source_file, start=1):
                        if not trust_any_match and not REFERENCE_CONTEXT_RE.search(line):
                            continue
                        for token in GROUP_REF_RE.findall(line):
                            seen_tokens.setdefault(token, '%s:%d' % (os.path.relpath(path, MODULE_ROOT), lineno))

        for token, location in seen_tokens.items():
            record = self.env.ref(token, raise_if_not_found=False)
            if record is None:
                violations.append('%s: %s (not found)' % (location, token))
            elif record._name != 'res.groups':
                violations.append('%s: %s (resolves to %s, not res.groups)' % (location, token, record._name))

        self.assertFalse(
            violations,
            "Every ems.group_* reference must resolve to an existing res.groups "
            "record (see CLAUDE.md's Coding standards) so a stale/renamed group "
            "name doesn't silently break the module on upgrade:\n" + "\n".join(violations),
        )
