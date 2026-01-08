# Copyright 2021, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class AccountInvoiceReportReal(models.Model):
    _name = "account.invoice.report.real"
    _description = "Account Invoice Report for Real"
    _auto = False
    _rec_name = "date"
    _order = "date desc"

    move_name = fields.Char(
        readonly=True,
    )
    date = fields.Date(
        readonly=True,
    )
    move_id = fields.Many2one(
        comodel_name="account.move",
        readonly=True,
    )
    partner_id = fields.Many2one(
        comodel_name="res.partner",
        readonly=True,
    )
    description = fields.Char(
        readonly=True,
    )
    account_name = fields.Char(
        readonly=True,
    )
    account_id = fields.Many2one(
        comodel_name="account.account",
        readonly=True,
    )
    l10n_mx_edi_payment_method_id = fields.Many2one(
        comodel_name="l10n_mx_edi.payment.method",
        readonly=True,
    )
    reference = fields.Char(
        readonly=True,
    )
    amount = fields.Monetary(
        readonly=True,
    )
    currency_id = fields.Many2one(
        comodel_name="res.currency",
    )

    _depends = {
        "account.move.line": [
            "name",
        ],
        "account.move": [
            "id",
            "name",
            "move_type",
            "amount_untaxed",
            "amount_total",
        ],
        "account.bank.statement.line": [
            "name",
        ],
        "l10n_mx_edi.payment.method": [
            "id",
            "name",
        ],
        "account.account": [
            "id",
            "name",
        ],
    }

    @property
    def _table_query(self):
        return """
            SELECT aml.id,
                am.name AS move_name,
                am.date,
                am.id AS move_id,
                am.ref AS reference,
                aml.name AS description,
                aml.balance AS amount,
                aml.currency_id,
                aml.partner_id,
                aa.name ->> 'en_US' AS account_name,
                aa.id AS account_id,
                ln10.id AS l10n_mx_edi_payment_method_id
            FROM account_move_line AS aml
                LEFT JOIN account_move AS am ON am.id = aml.move_id
                LEFT JOIN account_bank_statement_line AS absl ON absl.id = aml.statement_line_id
                LEFT JOIN l10n_mx_edi_payment_method AS ln10 ON ln10.id = am.l10n_mx_edi_payment_method_id
                LEFT JOIN account_account AS aa ON aa.id = aml.account_id
            WHERE aml.statement_line_id IS NOT NULL
            AND aa.account_type = 'asset_cash'
            AND aml.debit > 0
        """
