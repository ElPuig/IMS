import re

from odoo.tests.common import TransactionCase

# QWeb expressions inside a translated body, and the {{ }} placeholders used by the header
# fields (subject, recipients). Both are code, not prose - a translator never has a reason to
# change them, so any divergence from the English source is a stale translation.
QWEB_EXPRESSION = re.compile(r't-(?:field|out|esc|raw|foreach)="([^"]+)"')
PLACEHOLDER_EXPRESSION = re.compile(r'\{\{([^}]+)\}\}')

CHECKED_FIELDS = (
    ('body_html', QWEB_EXPRESSION),
    ('subject', PLACEHOLDER_EXPRESSION),
    ('email_to', PLACEHOLDER_EXPRESSION),
    ('email_from', PLACEHOLDER_EXPRESSION),
)


class TestMailTemplateTranslations(TransactionCase):
    """Every EMS mail template's translated values must reference exactly the same fields and
    expressions as their English source.

    A field renamed in the code reaches the English source through the template's own XML data
    file, but the ca_ES/es_ES values only ever change through i18n/*.po. A .po block for a whole
    translatable field is applied by its '#:' xmlid reference alone - the msgid is discarded - so
    when a rename updates the source and forgets the .po, nothing complains about the mismatch:
    the stale msgstr simply keeps overwriting the translation with markup pointing at a field that
    no longer exists. Nothing catches it either: ./upgrade.sh
    succeeds, the backend tests pass, and the template only blows up at render time, in the one
    language nobody develops in.

    That is exactly how 'ems.mail_attendance_issue_tutor' shipped a body_html still pointing at
    'status.attendance_status' after 18.0.0.22.0 renamed it to 'attendance_status_id', leaving the
    daily tutor report failing with "KeyError: 'attendance_status'" for every single recipient in
    production (repaired by migrations/18.0.0.24.0/pre-migrate.py). This test compares the
    expressions rather than the prose, so it guards the whole class instead of that one instance.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        template_ids = cls.env['ir.model.data'].search([
            ('module', '=', 'ems'),
            ('model', '=', 'mail.template'),
        ]).mapped('res_id')
        cls.templates = cls.env['mail.template'].browse(template_ids).exists()
        cls.languages = cls.env['res.lang'].search([]).mapped('code')

    def _stale_expressions(self, template):
        """Returns [(field, lang, sorted expressions)] for every translated value of 'template'
        using an expression its English source does not have."""
        stale = []
        source = template.with_context(lang='en_US')
        for field_name, expression in CHECKED_FIELDS:
            expected = set(expression.findall(source[field_name] or ''))
            for lang in self.languages:
                if lang == 'en_US':
                    continue
                translated = template.with_context(lang=lang)[field_name] or ''
                extra = set(expression.findall(translated)) - expected
                if extra:
                    stale.append((field_name, lang, sorted(extra)))
        return stale

    def test_translations_reference_the_same_expressions_as_the_english_source(self):
        self.assertTrue(self.templates, "No EMS mail template found to check.")

        for template in self.templates:
            with self.subTest(template=template.name):
                self.assertFalse(
                    self._stale_expressions(template),
                    f"'{template.name}' has a translation using expressions absent from its "
                    f"English source - a stale translation left behind by a rename, which will "
                    f"fail at render time in that language. Update the matching block in "
                    f"i18n/<lang>.po (both its msgid and its msgstr), and repair already-existing "
                    f"databases from a migration script.",
                )

    def test_a_stale_translation_is_detected(self):
        """Proves the check above actually bites, by reproducing the original bug: a translation
        left pointing at a field the English source no longer references."""
        template = self.templates[0]
        template.with_context(lang='ca_ES').body_html = (
            '<span t-field="object.a_field_removed_by_a_rename"/>'
        )

        self.assertIn(
            ('body_html', 'ca_ES', ['object.a_field_removed_by_a_rename']),
            self._stale_expressions(template),
        )
