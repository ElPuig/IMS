# -*- coding: utf-8 -*-
import logging

_logger = logging.getLogger(__name__)

OLD_EXPRESSION = 't-field="status.attendance_status"'
NEW_EXPRESSION = 't-field="status.attendance_status_id"'


def _fix_tutor_template_stale_translations(cr):
    """'ems.attendance_issue_status.attendance_status' (Selection) became 'attendance_status_id'
    (Many2one) in 18.0.0.22.0. That version updated the English source of
    'mails/attendance/attendance_issue_tutor.xml', but not the 'ca_ES'/'es_ES' blocks of the .po
    files (fixed in this same version), so every non-English value of that template's 'body_html'
    kept referencing a field that no longer exists and blew up at render time with
    "KeyError: 'attendance_status'" - confirmed on the production dump of 2026-09-09, where the
    daily tutor report had never once been delivered.

    Why it never self-healed, and why the .po fix alone is not enough: a .po block for a whole
    translatable field (as opposed to a term inside an arch) is applied by matching its '#:'
    xmlid reference - the 'msgid' is discarded outright (odoo/tools/translate.py's
    TranslationImporter.load, 'model_translations[...][xmlid][lang] = row["value"]'). So the stale
    'msgstr' kept being written straight back over the translations on every upgrade run with
    '--i18n-overwrite' (upgrade.sh), while deploy.sh, which runs without it, falls into the
    'merged.noupdate_value || merged.update_value || m.<field>' branch of the same importer - the
    existing database value comes last in that jsonb merge and therefore wins, so an already-broken
    production value is never replaced no matter how many times the corrected .po is loaded.
    Hence this script: the .po correction repairs development, this repairs production.

    The guard deliberately looks inside each language's value rather than at 'body_html::text':
    the jsonb text representation escapes the expression's own double quotes, so a LIKE against it
    never matches (found while rehearsing this script on a copy of the production database).

    Replacing the expression in place (rather than dropping the language keys and relying on the
    corrected .po to repopulate them) keeps the Catalan/Spanish wording and behaves identically
    whether or not '--i18n-overwrite' is in play. Runs in pre-migrate: raw SQL throughout, on a
    column that has existed for versions, and it must happen before the data files reload.
    """
    cr.execute(
        """
        UPDATE mail_template t
           SET body_html = (
               SELECT jsonb_object_agg(lang, to_jsonb(replace(value, %(old)s, %(new)s)))
                 FROM jsonb_each_text(t.body_html) AS translation(lang, value)
           )
          FROM ir_model_data d
         WHERE d.module = 'ems'
           AND d.model = 'mail.template'
           AND d.name = 'mail_attendance_issue_tutor'
           AND d.res_id = t.id
           AND EXISTS (
               SELECT 1 FROM jsonb_each_text(t.body_html) AS existing(lang, value)
                WHERE existing.value LIKE %(pattern)s
           )
        """,
        {
            'old': OLD_EXPRESSION,
            'new': NEW_EXPRESSION,
            'pattern': f'%{OLD_EXPRESSION}%',
        },
    )
    if cr.rowcount:
        _logger.info(
            "Migration 18.0.0.23.6: repaired the stale '%s' reference in the tutor notification "
            "template's translations.", OLD_EXPRESSION,
        )


def migrate(cr, _version):
    _fix_tutor_template_stale_translations(cr)
