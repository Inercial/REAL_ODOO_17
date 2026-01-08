# Copyright 2025 Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import datetime
import logging

from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)


modules_to_remove = [
    "account_aged_by_currency_report",
    "account_analytic_required",
    "account_financial_report",
    "account_mass_reconcile",
    "om_hr_payroll",
    "mis_builder",
    "account_xunnel",
    "l10n_mx_edi_partner_defaults",
    "l10n_mx_edi_uuid",
    "l10n_mx_import_taxes",
    "stock_move_line_auto_fill",
    "nomina_cfdi_bancos",
    "nomina_cfdi_ee",
    "nomina_cfdi_extras_ee",
    "nomina_realsa",
    "om_hr_payroll_account_ee",
    "payroll_real",
    "purchase_order_line_price_history",
    "account_menu",
    "l10n_mx_edi_reports",
    "l10n_mx_edi_document",
    "l10n_edi_document",
    "account_payment_paired_internal_transfer",
    "account_partner_reconcile",
    "stock_reserve_rule",
]


# List of strings with XML ID.
records_to_remove = []

# List of tuples with the follwing format
# ('old_module_name', 'new_module_name'),
modules_to_rename = [
    ("mass_editing", "server_action_mass_edit"),
]

modules_to_install = []

modules_to_upgrade = []

models_to_remove = [
    "attach.document.invoice.wizard",
    "mass.reconcile.advanced.name",
    "account.age.report.configuration.line",
    "open.items.report.wizard",
    "mass.reconcile.history",
    "account.age.report.configuration",
    "mass.reconcile.simple.reference",
    "stock.reserve.rule",
    "journal.ledger.report.wizard",
    "general.ledger.report.wizard",
    "aged.partner.balance.report.wizard",
    "mass.reconcile.simple.partner",
    "stock.reserve.rule.removal",
    "trial.balance.report.wizard",
    "mass.reconcile.advanced.ref",
    "vat.report.wizard",
    "account.mass.reconcile.method",
    "mass.reconcile.simple.name",
]

views_to_activate = [
    "product_packaging_level.view_product_packaging_add_type_form",
    "google_spreadsheet_import.google_spreadsheet_form",
    "stock_request.view_stock_request_form",
    "stock_request.stock_request_order_form",
    "stock_request.res_config_settings_view_form",
    "stock_request_purchase.view_stock_request_form",
    "stock_request_purchase.stock_request_order_form",
    "account_payment_mode.account_payment_method_tree",
    "account_payment_partner.view_move_line_form",
    "account_payment_order.account_payment_order_tree",
    "account_payment_order.account_payment_order_graph",
    "account_payment_order.account_payment_order_pivot",
    "account_payment_order.account_payment_line_form",
    "server_action_mass_edit.view_server_action_form",
    "stock_request_analytic.view_stock_request_form",
    "stock_request_analytic.stock_request_order_form",
    "account_payment.portal_my_invoices_payment",
    "account_payment.portal_invoice_page_inherit_payment",
    "l10n_mx_edi_related_documents.view_move_form",
    "purchase.portal_my_home_purchase",
    "helpdesk.portal_my_home_helpdesk_ticket",
]

views_to_remove = [
    "studio_customization.odoo_studio_res_part_6625f9d7-19a4-4232-b015-96e2882745b5",
    "studio_customization.odoo_studio_report_s_2df581e9-06f6-4e6c-a2ba-3721828a42cd",
    "studio_customization.odoo_studio_report_s_b0a7bc98-76dc-4fd2-8fed-5231fe5cfe69",
    "studio_customization.odoo_studio_sale_ord_78d595e4-00a1-41b6-a259-f3008b6fa102",
    "studio_customization.pedido_30ea78e0-475f-49c0-9a79-7e74b7327e32",
    "studio_customization.report_saleorder_doc_e0a144f6-b2e8-4580-9a8f-4d94f63c1ee6",
    "studio_customization.report_saleorder_76096750-6acb-43cd-bfb5-00b33ae5a7a8",
    "studio_customization.report_saleorder_doc_9c564c1a-0760-43d0-84c4-7840c83767b5",
    "studio_customization.report_saleorder_cab10367-0b36-4079-8430-0636e2227d46",
    "studio_customization.report_saleorder_doc_6442beb5-58b4-40e1-b779-618181734556",
    "studio_customization.report_saleorder_e17a0190-7282-4d04-8fc2-2e069dad70e8",
    "studio_customization.studio_main_report_2c88ec34-9ca8-46c4-98ac-b5a5f1b2aa2d",
    "studio_customization.studio_customization_e4361107-749d-4890-8761-c8c927952a97",
    "studio_customization.odoo_studio_studio_c_b75d333a-6010-4e24-9da1-74791a78bebd",
    "studio_customization.odoo_studio_studio_c_913a4573-ee23-4acd-b60e-5c6783241de7",
    "studio_customization.studio_main_report_9e38f0d4-1372-479b-bf6e-1dce0410a386",
    "studio_customization.studio_customization_ef22883f-b62a-4966-9bd0-d6d59b7b1cd3",
    "studio_customization.studio_customization_648adeff-a7e0-4988-bd65-8b79435d9ce3",
    "studio_customization.studio_customization_6e830e4c-5dea-4b88-95c7-539d6ce70a9c",
    "studio_customization.studio_customization_0c01c883-2743-4ac7-a07c-7ff14a410795",
    "studio_customization.odoo_studio_studio_c_8f675394-ca88-4d46-897f-826991b6e225",
    "studio_customization.odoo_studio_studio_c_92252e3f-4a24-4971-a309-cdbc5d015319",
    "studio_customization.odoo_studio_studio_c_0f477b8c-abc8-4726-bede-c4a86602c5f6",
    "studio_customization.studio_main_report_91da2994-503a-429c-92ee-a600d6342b4a",
    "studio_customization.odoo_studio_studio_c_6d81adea-b157-4550-8a3c-66a6ac9e9993",
    "studio_customization.odoo_studio_studio_c_e0e59f26-b699-4f56-8ecb-0cb3f02afbee",
    "studio_customization.odoo_studio_studio_c_a3c40ccc-fc31-4925-8625-a672267e35fc",
    "studio_customization.studio_main_report_c9b649ae-e2ae-445a-acd1-199d71f6ef9f",
    "studio_customization.odoo_studio_studio_c_f3625c07-d932-4eed-adbf-e8c7f7d9973f",
    "studio_customization.studio_customization_8c2c2edf-0741-4452-831b-7318e8488267",
    "studio_customization.odoo_studio_studio_c_00f1fb0c-a9fd-4c33-9d0f-8dce8b57cd42",
    "studio_customization.odoo_studio_studio_c_24ef62fc-1796-46bc-b749-360c02985c2a",
    "studio_customization.odoo_studio_studio_c_52797be8-d33e-4bed-a368-f8b2d9661f1b",
    "studio_customization.studio_main_report_6c3d5286-3e3e-4fde-8567-9e89cd9ab1da",
    "studio_customization.studio_customization_a9dfa733-521e-4b0c-ac0c-e0bc1a53d866",
    "studio_customization.odoo_studio_studio_c_b6ce840c-a76f-45c1-b852-5d7e9bf73954",
    "studio_customization.odoo_studio_studio_c_4836434f-b8ee-4f94-a083-dcd4e2d3f16f",
    "studio_customization.studio_report_docume_7cb6be0e-8320-4272-88ce-bc6e72abb707",
    "studio_customization.studio_customization_09808387-759c-41ea-9523-3d8941d0421a",
    "studio_customization.studio_report_docume_b8938187-2816-4b04-8474-673d69e0cf7d",
    "studio_customization.studio_customization_cf1a8035-4c12-4251-882c-2428f78b0730",
    "studio_customization.studio_customization_05abfe75-168d-42b7-b2d0-3b472bb02a06",
    "studio_customization.studio_report_docume_b78a967e-0936-4669-b4ec-29f9ed5c4d48",
    "studio_customization.studio_main_report_af1b886c-7537-44e2-8b47-ababf9a41cb2",
    "studio_customization.studio_report_docume_a108cb35-235c-4081-ae64-ad9568efe2fa",
    "studio_customization.studio_report_docume_82fc8cb3-9040-4409-a3b3-0402d6a0e745",
    "studio_customization.studio_main_report_5d10fd03-ec8f-45cb-aea7-cc5c852ced32",
    "studio_customization.studio_report_docume_d8149de0-1d42-405c-b8ac-2558b162c57e",
    "studio_customization.studio_customization_e189b780-91db-48b3-a99a-fe6a0861fd2e",
    "studio_customization.studio_report_docume_726631dd-e487-448d-b787-9f8e4ff225d4",
    "studio_customization.studio_customization_fd218716-ba65-4015-ab2e-02f6b56cec6e",
    "studio_customization.asiento_contable_rep_0180117a-cf05-425e-bf92-ee6e951b1e2e",
    "studio_customization.ventas_nota_de_credi_c590d7f5-c020-4da5-8a1e-334b13ef95dd",
    "studio_customization.asiento_contable_rep_c1cf1a16-ebc3-4ba7-8c62-3d8e91123f51",
    "studio_customization.diario_de_ventas_4f7bfb19-c9b9-41c5-a2fc-97199c457caf",
    "studio_customization.diario_de_ventas_1205dc43-3e0f-46ba-af69-a2649d62890a",
    "studio_customization.diario_de_ventas_33f92a0a-f5b9-4300-820c-3be9760839f6",
    "studio_customization.asiento_contable_rep_5415deb6-3174-4d89-8375-f8b1d59fb7b4",
    "studio_customization.asiento_contable_rep_83fbce5c-909e-4aa1-9469-222d2b28d2da",
    "studio_customization.asiento_contable_rep_ae5d4083-f0f8-4fcc-87bc-0b22feb38995",
    "studio_customization.asiento_contable_rep_86a96b14-43a0-44bd-9cde-7d04652b1553",
    "studio_customization.compras_factura_de_p_b2bdc239-1a49-4be8-aa62-ee162da43243",
    "studio_customization.ventas_factura_origi_504a7fcb-b370-4ef5-abb2-d8ad5d019185",
    "studio_customization.asiento_contable_rep_2342229c-383f-4add-a498-bd69c1fa1d14",
    "studio_customization.odoo_studio_studio_c_107cf183-630c-4181-a550-64f59455514a",
    "studio_customization.studio_report_docume_4a79ab82-1d19-4b1e-a011-3b2803d5e0d0",
    "studio_customization.studio_main_report_67e1f2f2-b418-46e4-95c0-194397577e43",
    "studio_customization.studio_report_docume_cc80542c-9cdf-4ec2-8aac-08097f28e403",
    "studio_customization.studio_main_report_8303f64f-6220-457a-92a7-343256eed35f",
    "studio_customization.odoo_studio_studio_c_61e97c25-8941-4cb9-9027-34ab370dd549",
    "studio_customization.studio_report_docume_9da94b26-9d85-4923-990d-74d1024997e4",
    "studio_customization.studio_main_report_b6aa8b7a-2762-48d6-a605-2df4f5180865",
    "studio_customization.odoo_studio_studio_c_ad127d73-4f78-456d-a1b3-59f0d0d1a721",
    "studio_customization.odoo_studio_studio_c_0764dba6-9702-4049-9d7f-613872d4ed5a",
    "studio_customization.odoo_studio_studio_c_403149cc-8f9e-4844-a216-0dca97f00f1d",
    "studio_customization.odoo_studio_studio_c_7057bb76-6562-41e4-92bd-d9c95c252462",
    "studio_customization.studio_report_docume_a209fa7c-5b17-427c-a905-cb176e5f3c60",
    "studio_customization.studio_main_report_5de57baf-c5f5-487d-aede-6ce3fcb3518a",
    "studio_customization.studio_customization_a90c1509-5c57-4d0c-aada-f7abfbfe68c2",
    "studio_customization.studio_customization_0efc5563-18d4-4b99-8760-bfe6b3c98b23",
    "studio_customization.studio_customization_d84887e5-f155-4ae2-9c23-2dfe69e6ee8c",
    "studio_customization.studio_customization_9382f22e-5ed4-4366-8c3d-01350d5a7169",
    "studio_customization.studio_customization_13ca7ae3-7465-4b00-8d6b-20bc23e851d4",
    "studio_customization.studio_customization_a2b39c88-f191-4be1-8771-0988cb4339a9",
    "studio_customization.studio_customization_dff5702c-c858-4517-b5ad-c2454b741536",
    "studio_customization.studio_customization_558c7edd-3762-4f75-8a5c-baab75bb27c9",
    "studio_customization.odoo_studio_studio_c_3d91240b-f1c9-45c7-8291-17664ed59a6f",
    "studio_customization.studio_report_docume_ed98e4a2-dcb3-44cf-84eb-8f04e4a55ece",
    "studio_customization.studio_main_report_59a41a7d-8510-429e-b854-f9b828e9df4f",
]


def rename_modules(env, old, new):
    env["ir.module.module"].update_list()
    _logger.warning("Rename module %s -> %s", old, new)
    module = env["ir.module.module"].search([("name", "=", new)])
    old_module = env["ir.module.module"].search([("name", "=", old)])
    module.invalidate_recordset()
    if module and old_module:
        env.cr.execute("DELETE FROM ir_model_data WHERE name = %(new)s", {"new": f"module_{new}"})
        env.cr.execute("DELETE FROM ir_module_module WHERE id = %(id)s", {"id": module.id})
        openupgrade.update_module_names(env.cr, [(old, new)])


def _process_edi_files(env):
    _logger.warning("Processing EDI files")
    edi_documents = env["l10n_mx_edi.document"].search([])
    attachments = env["ir.attachment"].search(
        [
            ("res_model", "=", "account.move"),
            ("name", "=ilike", "%.xml"),
            ("res_id", "not in", edi_documents.mapped("move_id").ids),
            ("res_id", "!=", False),
        ]
    )
    _logger.warning("Found %s attachments to process", len(attachments))
    count = 0
    for attachment in attachments:
        count += 1
        attachment_id = attachment.id
        res_id = attachment.res_id
        if not count % 100:
            _logger.warning("Processing attachment %s/%s", count, len(attachments))
        try:
            env["l10n_mx_edi.document"].create(
                {
                    "move_id": attachment.res_id,
                    "invoice_ids": [(4, attachment.res_id)],
                    "state": "invoice_sent",
                    "sat_state": "not_defined",
                    "attachment_id": attachment.id,
                    "datetime": datetime.datetime.now(),
                }
            )
        except Exception as e:
            _logger.warning("Error processing attachment %s for move %s: %s", attachment_id, res_id, e)


def _add_security_groups(env):
    if env.ref("real.res_users_role_seller_res_groups"):
        env.ref("real.res_users_role_seller_res_groups").write(
            {
                "implied_ids": [
                    (4, env.ref("account_financial_risk.group_account_financial_risk_user").id),
                ]
            }
        )
    if env.ref("real.res_users_role_collection_res_groups"):
        env.ref("real.res_users_role_collection_res_groups").write(
            {
                "implied_ids": [
                    (4, env.ref("account_financial_risk.group_account_financial_risk_manager").id),
                ]
            }
        )
    if env.ref("real.res_users_role_marketing_res_groups"):
        env.ref("real.res_users_role_marketing_res_groups").write(
            {
                "implied_ids": [
                    (4, env.ref("account_financial_risk.group_account_financial_risk_user").id),
                ]
            }
        )
    if env.ref("real.res_users_role_sales_manager_res_groups"):
        env.ref("real.res_users_role_sales_manager_res_groups").write(
            {
                "implied_ids": [
                    (4, env.ref("account_financial_risk.group_account_financial_risk_user").id),
                ]
            }
        )
    if env.ref("account_financial_risk.group_account_financial_risk_manager"):
        env.ref("account_financial_risk.group_account_financial_risk_manager").write(
            {
                "users": [
                    (4, env.ref("base.user_admin").id),
                    (4, 45),
                    (4, 46),
                ]
            }
        )
    if env.ref("__export__.res_users_role_13_52167506"):
        env.ref("__export__.res_users_role_13_52167506").write(
            {
                "implied_ids": [
                    (4, env.ref("l10n_edi_hr_expense.allow_to_accrue_expenses").id),
                    (4, env.ref("l10n_mx_edi_hr_expense.allow_to_approve_exp_wo_being_responsible").id),
                    (4, env.ref("l10n_mx_edi_hr_expense.allow_to_generate_expenses_2b_checked").id),
                    (4, env.ref("l10n_mx_edi_hr_expense.allow_to_revert_expenses").id),
                    (4, env.ref("l10n_mx_edi_hr_expense.allow_to_see_employee_payments").id),
                    (4, env.ref("l10n_mx_edi_hr_expense.force_expense").id),
                    (4, env.ref("l10n_mx_edi_hr_expense.reclassify_journal_entries_expense").id),
                ]
            }
        )
        l10n_edi_groups = [
            "l10n_edi_hr_expense.allow_to_accrue_expenses",
            "l10n_edi_hr_expense.allow_to_approve_exp_wo_being_responsible",
            "l10n_edi_hr_expense.allow_to_generate_expenses_2b_checked",
            "l10n_edi_hr_expense.allow_to_revert_expenses",
            "l10n_edi_hr_expense.allow_to_see_employee_payments",
            "l10n_edi_hr_expense.force_expense",
            "l10n_edi_hr_expense.reclassify_journal_entries_expense",
        ]
        for group_xml_id in l10n_edi_groups:
            group = env.ref(group_xml_id)
            group.write(
                {
                    "users": [
                        (4, 2),
                        (4, 45),
                        (4, 46),
                    ]
                }
            )


def _delete_unused_journals(env):
    all_journals = env["account.journal"].search([])
    journals_to_delete = env["account.journal"]
    for journal in all_journals:
        move_count = env["account.move"].search_count([("journal_id", "=", journal.id)])
        if not move_count:
            journals_to_delete |= journal
    try:
        journals_to_delete.unlink()
    except Exception:
        _logger.warning("Error deleting journals")


# pylint: disable=too-complex
@openupgrade.migrate()
def migrate(env, installed_version):
    if records_to_remove:
        _logger.warning("Delete records from XML ID")
        openupgrade.delete_records_safely_by_xml_id(env, records_to_remove)
    if modules_to_rename:
        _logger.warning("Modules to rename")
        for module in modules_to_rename:
            rename_modules(env, module[0], module[1])
    if modules_to_remove:
        _logger.warning("Uninstalling not required modules")
        to_remove = env["ir.module.module"].search([("name", "in", modules_to_remove)])
        to_remove += to_remove.downstream_dependencies()
        to_remove.module_uninstall()
        to_remove.unlink()
    if views_to_activate:
        _logger.warning("Activating views")
        for view in views_to_activate:
            view_record = env.ref(view, raise_if_not_found=False)
            if view_record:
                try:
                    view_record.active = True
                except Exception as e:
                    _logger.warning("Error activating view %s: %s", view, e)
            else:
                _logger.warning("View %s not found", view)
    if views_to_remove:
        _logger.warning("removing views")
        for view in views_to_remove:
            view_record = env.ref(view, raise_if_not_found=False)
            if view_record:
                try:
                    view_record.unlink()
                except Exception as e:
                    _logger.warning("Error Removing view %s: %s", view, e)
            else:
                _logger.warning("View %s not found", view)
    if modules_to_install:
        env["ir.module.module"].update_list()
        _logger.warning("Installing new modules")
        to_install = env["ir.module.module"].search([("name", "in", modules_to_install)])
        to_install.button_install()
    if modules_to_upgrade:
        _logger.warning("Upgrading required modules")
        env["ir.module.module"].update_list()
        to_upgrade = env["ir.module.module"].search([("name", "in", modules_to_upgrade)])
        to_upgrade.button_upgrade()
    if models_to_remove:
        _logger.warning("Removing models")
        for model_name in models_to_remove:
            _logger.warning("Removing model %s", model_name)
            env.cr.execute("DELETE FROM ir_model_fields WHERE model = %(model)s;", {"model": model_name})
            env.cr.execute(
                "DELETE FROM ir_model_constraint WHERE model = (SELECT id FROM ir_model WHERE model = %(model)s);",
                {"model": model_name},
            )
            env.cr.execute(
                "DELETE FROM ir_model_relation WHERE model = (SELECT id FROM ir_model WHERE model = %(model)s);",
                {"model": model_name},
            )
            env.cr.execute("DELETE FROM ir_model WHERE model = %(model)s;", {"model": model_name})
    _logger.warning("Delete payment term lines with 0 amount")
    env.cr.execute("DELETE FROM account_payment_term_line WHERE value_amount = 0 AND value = 'fixed' AND nb_days = 0;")
    _add_security_groups(env)
    _process_edi_files(env)
    _delete_unused_journals(env)
