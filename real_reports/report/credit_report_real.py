# Copyright 2021, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class CreditReportReal(models.Model):
    _name = "credit.report.real"
    _description = "Credit Report for Real"
    _auto = False
    _order = "name desc"
    _rec_name = "invoice_date"

    _depends = {
        "account.move.line": [
            "name",
            "partner_id",
            "date",
            "move_id",
            "credit",
            "account_id",
        ],
        "account.move": ["id", "invoice_user_id", "invoice_date_due", "move_type", "state"],
        "account.partial.reconcile": [
            "id",
            "amount",
            "credit_move_id",
            "debit_move_id",
        ],
        "account.account": [
            "id",
        ],
    }

    credit_note_date = fields.Date(
        readonly=True,
    )
    invoice_date = fields.Date(
        readonly=True,
    )
    payment_date = fields.Date(
        readonly=True,
    )
    rectified_invoices = fields.Selection(
        selection=[
            ("unassigned", "Unassigned"),
            ("application_of_advance", "Application of Advance"),
            ("uncollectible_account", "Uncollectible account"),
            ("Special_discounts", "Special discounts"),
            ("discounts_promp_payment", "Discounts for prompt payment"),
            ("advance_refund", "Advance refund"),
            ("Seller_error", "Seller error"),
            ("custom_err", "Customer error"),
            ("shipment_delivery_mistake", "Shipment delivery mistake"),
            ("logistics_err", "Logistics error"),
            ("wet_shipping_material", "Wet shipping material"),
            ("broken_shipping_material", "Broken shipping material"),
            ("non_rotating_material", "Non-rotating material"),
            ("material_exit_sample", "Material exit as sample"),
            ("return_invoice_paid", "Return invoice paid"),
            ("physical_retur", "Physical return"),
            ("different_prices", "Different prices"),
            ("damaged_material", "Damaged Material"),
            ("customer_not_received", "Customer not received"),
            ("did_not_leave_plant", "Did not leave the plant"),
            ("rebilling_others", "Rebilling Others"),
            ("rebilling_date", "Rebilling by date"),
            ("rebilling_type_payment", "Rebilling by type of payment"),
            ("transfer_other_client", "Transfer to other client"),
        ],
        readonly=True,
    )
    name = fields.Char(
        readonly=True,
    )
    partner_id = fields.Many2one(
        comodel_name="res.partner",
        readonly=True,
    )
    total = fields.Monetary(
        readonly=True,
    )
    currency_id = fields.Many2one(
        comodel_name="res.currency",
        readonly=True,
    )
    days_invoice = fields.Integer(
        readonly=True,
    )

    @property
    def _table_query(self):
        """Modificación: El reporte considera 3 escenarios posibles:
        1) Una nota de crédito aplicada en su totalidad a una o más facturas
        2) Una nota de crédito aplicada parcialmente a una o más facturas
        3) Una nota de crédito no aplicada
        Los escenarios 2 y 3 se consideran en la segunda parte de la consulta.
        """
        return """
        SELECT
            apr.id,
            credit_move.rectified_invoices,
            credit_move.date AS credit_note_date,
            credit_move.name AS name,
            invoice_move_line.partner_id AS partner_id,
            invoice_move.invoice_date,
            bm.date - invoice_move_line.date AS days_invoice,
            apr.amount AS total,
            credit_move_line.currency_id,
            bm.date AS payment_date
        FROM account_move_line AS credit_move_line
        LEFT JOIN account_move AS credit_move ON credit_move_line.move_id = credit_move.id
        LEFT JOIN account_partial_reconcile AS apr ON apr.credit_move_id = credit_move_line.id
        LEFT JOIN account_move_line AS invoice_move_line ON apr.debit_move_id = invoice_move_line.id
        LEFT JOIN account_move AS invoice_move ON invoice_move_line.move_id = invoice_move.id
        LEFT JOIN LATERAL (
            SELECT
                bank_move.date
            FROM account_partial_reconcile AS apr2
            LEFT JOIN account_move_line AS bank_move_line ON bank_move_line.id = apr2.credit_move_id
            LEFT JOIN account_move AS bank_move ON bank_move.id = bank_move_line.move_id
            WHERE
                apr2.debit_move_id = invoice_move_line.id AND
                apr2.id != apr.id AND
                bank_move.move_type = 'entry'
            ORDER BY bank_move.date DESC LIMIT 1
        ) bm ON TRUE
        WHERE
            (
                apr.credit_move_id IN (
                    SELECT aml.id
                    FROM account_move_line AS aml
                    LEFT JOIN account_move AS am ON am.id = aml.move_id
                    WHERE aml.account_id = 3 AND aml.credit > 0 AND am.move_type = 'out_refund' AND am.state != 'cancel'
                )
                OR apr.debit_move_id IN (
                    SELECT aml.id
                    FROM account_move_line AS aml
                    LEFT JOIN account_move AS am ON am.id = aml.move_id
                    WHERE aml.account_id = 3 AND aml.credit > 0 AND am.move_type = 'out_refund' AND am.state != 'cancel'
                )
            )
        UNION ALL
        SELECT DISTINCT ON (credit_move.id)
            ROW_NUMBER() OVER (ORDER BY 1) AS id,
            credit_move.rectified_invoices,
            credit_move.date AS credit_note_date,
            credit_move.name AS name,
            credit_move.partner_id AS partner_id,
            NULL AS invoice_date,
            0 AS days_invoice,
            credit_move.amount_residual AS total,
            credit_move_line.currency_id,
            NULL AS payment_date
        FROM account_move_line AS credit_move_line
        LEFT JOIN account_move AS credit_move ON credit_move_line.move_id = credit_move.id
        WHERE
            (
                credit_move_line.id IN (SELECT apr.credit_move_id FROM account_partial_reconcile apr)
                OR credit_move.payment_state = 'not_paid'
            )
            AND credit_move_line.account_id = 3
            AND credit_move_line.credit > 0
            AND credit_move.move_type = 'out_refund'
            AND credit_move.state != 'cancel'
            AND credit_move.amount_residual > 0
        """


class ReportCreditNote(models.AbstractModel):
    _name = "report.real_reports.credit_note_report"
    _description = "Report For Credit Notes"

    def _get_report_values(self, docids, data=None):
        docs = self.env["credit.report.real"].browse(docids)
        dates = [x.credit_note_date for x in docs]
        grouped_dict = {}
        for doc in docs:
            grouped_dict.setdefault(doc.rectified_invoices, []).append(doc)
        return {
            "grouped_dict": grouped_dict,
            "min_date": min(dates).strftime("%d/%m/%Y"),
            "max_date": max(dates).strftime("%d/%m/%Y"),
        }
