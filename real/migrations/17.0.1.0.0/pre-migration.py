# Copyright 2025 Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import logging

_logger = logging.getLogger(__name__)

modules_views_to_remove = [
    "real",
    "l10n_mx_edi_hr_expense",
    "sale_stock",
]

modules_views_to_not_remove = [
    "sale",
]

fields_in_views_to_remove = [
    "analytic_account_id",
    "datamatrix_pack_date",
]

views_to_activate = [
    "stock_request.stock_request_order_form",
    "stock_request_analytic.view_stock_request_form",
    "stock_request_analytic.stock_request_order_form",
    "stock_request_partner.stock_request_order_form",
]

assets_to_remove = [
    "/account_financial_report/static/src/css/report.css",
    "/account_financial_report/static/src/js/account_financial_report_backend.js",
    "/account_financial_report/static/src/js/account_financial_report_widgets.js",
    "/l10n_mx_edi_document/static/src/sass/widget.scss",
    "/l10n_mx_edi_document/static/src/js/checks_widget.js",
    "/l10n_mx_edi_document/static/src/js/checklist_animation.js",
    "/l10n_mx_edi_document/static/src/js/documents_inspector.js",
    "/l10n_mx_edi_document/static/src/js/documents_dashboard.js",
    "/l10n_edi_document/static/src/sass/widget.scss",
    "/l10n_edi_document/static/src/js/checks_widget.js",
    "/l10n_edi_document/static/src/js/checklist_animation.js",
    "/mis_builder/static/src/css/custom.css",
    "/mis_builder/static/src/js/mis_report_widget.js",
    "/date_range/static/src/js/date_range.js",
    "/account_xunnel/static/src/js/synchronized_account.js",
    "/report_xlsx/static/src/js/report/action_manager_report.js",
    "/l10n_mx_edi_hr_expense/static/src/js/checks_widget.js",
    "/l10n_mx_edi_hr_expense/static/src/js/checklist_animation.js",
    "/google_spreadsheet_import/static/src/js/drive_sheet.js",
    "/web_m2x_options/static/src/js/form.js",
    "/stock_card_report/static/src/js/stock_card_report_backend.js",
    "/l10n_mx_edi_reports/static/src/js/account_reports.js",
    "/l10n_mx_edi_hr_expense/static/src/sass/widget.scss",
]


def _get_all_views_with_inherit(cr, view_ids):
    def _find_inherited_views(parent_ids):
        if not parent_ids:
            return
        _logger.info("Executing query: SELECT id FROM ir_ui_view WHERE inherit_id IN %s;", (tuple(parent_ids),))
        cr.execute("SELECT id FROM ir_ui_view WHERE inherit_id IN %s;", (tuple(parent_ids),))
        inherited_ids = {row[0] for row in cr.fetchall()}
        new_ids = inherited_ids - all_view_ids  # evitamos procesar repetidos
        if new_ids:
            all_view_ids.update(new_ids)
            _find_inherited_views(new_ids)

    all_view_ids = set(view_ids)
    _find_inherited_views(all_view_ids)
    return list(all_view_ids)


def _get_module_view_ids(cr, module_list):
    view_ids = []
    for module_name in module_list:
        _logger.info(
            "Executing query: SELECT id FROM ir_ui_view WHERE arch_fs ILIKE %s;", {"pattern": f"%{module_name}/%"}
        )
        cr.execute("SELECT id FROM ir_ui_view WHERE arch_fs ILIKE %(pattern)s;", {"pattern": f"%{module_name}/%"})
        view_ids.extend(row[0] for row in cr.fetchall())
    return view_ids


def _get_views_ids_with_field(cr):
    view_ids = []
    for field in fields_in_views_to_remove:
        _logger.info(
            "Executing query: SELECT id FROM ir_ui_view WHERE EXISTS (SELECT 1 FROM jsonb_each_text(arch_db) AS "
            "langs(lang, xml) WHERE xml ILIKE %s);",
            (f"%{field}%",),
        )
        cr.execute(
            """
            SELECT id
            FROM ir_ui_view
            WHERE EXISTS (
                SELECT 1
                FROM jsonb_each_text(arch_db) AS langs(lang, xml)
                WHERE xml ILIKE %(field)s
            );
        """,
            {"field": f"%{field}%"},
        )
        view_ids.extend(row[0] for row in cr.fetchall())
    return view_ids


def _views_to_activate(cr, views):
    for view_ref in views:
        cr.execute(
            "SELECT res_id FROM ir_model_data WHERE model = 'ir.ui.view' AND module || '.' || name = %s;", (view_ref,)
        )
        view_id = cr.fetchone()
        if not view_id:
            _logger.warning("View %s not found in ir_model_data", view_ref)
            continue
        _logger.warning("Activating view %s", view_ref)
        cr.execute("UPDATE ir_ui_view SET active = TRUE WHERE id = %s;", (view_id[0],))


def _fix_analytic_account_stock_request_order(cr):
    _logger.info("Fixing analytic_distribution in stock_request_order")
    cr.execute(
        """
        update stock_request_order set analytic_distribution =
        json_build_object(analytic_account_id::varchar, 100.0)
        where analytic_account_id is not null;
        """
    )


def _assign_auto_validate_tag_to_partner(cr):
    """Assign the auto-validation tag (ID 361) to the
    global expense partner (ID 2828).
    """
    _logger.info("Assigning auto-validate tag to global partner")
    partner_id = 2828
    category_id = 361

    cr.execute(
        """
        INSERT INTO res_partner_res_partner_category_rel (partner_id, category_id)
        VALUES (%s, %s);
        """,
        (partner_id, category_id),
    )


def migrate(cr, installed_version):
    view_ids = _get_module_view_ids(cr, modules_views_to_remove)
    view_ids.extend(_get_views_ids_with_field(cr))
    view_ids = _get_all_views_with_inherit(cr, view_ids)
    to_not_remove = _get_module_view_ids(cr, modules_views_to_not_remove)
    view_ids = [vid for vid in view_ids if vid not in to_not_remove]
    _logger.info("Executing query: DELETE FROM ir_ui_view WHERE id IN %s;", (tuple(view_ids),))
    cr.execute("DELETE FROM ir_ui_view WHERE id IN %(ids)s;", {"ids": tuple(view_ids)})
    _logger.warning("Removing ir_assets")
    for asset in assets_to_remove:
        _logger.warning("Removing ir_asset for %s", asset)
        cr.execute("DELETE FROM ir_asset WHERE path = %(asset)s;", {"asset": asset})
    _logger.warning("Updating res_partner P01 to G01")
    cr.execute("UPDATE res_partner SET l10n_mx_edi_usage = 'G01' WHERE l10n_mx_edi_usage = 'P01';")
    cr.execute(
        """
        UPDATE ir_config_parameter
        SET key = 'l10n_edi_hr_expense.global_partner'
        WHERE key = 'l10n_mx_edi_hr_expense.global_partner';
        """
    )
    _assign_auto_validate_tag_to_partner(cr)
    _views_to_activate(cr, views_to_activate)
    _fix_analytic_account_stock_request_order(cr)
