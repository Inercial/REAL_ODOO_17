# Copyright 2021, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class AccountBankReportReal(models.Model):
    _name = "account.bank.report.real"
    _description = "Account Bank Report for Real"
    _auto = False
    _order = "date desc"
    _rec_name = "date"

    move_name = fields.Char(
        readonly=True,
    )
    date = fields.Date(
        readonly=True,
    )
    partner_id = fields.Many2one(
        comodel_name="res.partner",
        readonly=True,
    )
    partner_category_ids = fields.Many2many(
        comodel_name='res.partner.category',
        compute='_compute_partner_category_ids',
        string='Tags',
        readonly=True,
    )
    move_id = fields.Many2one(
        comodel_name="account.move",
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
    journal_id = fields.Many2one(
        comodel_name="account.journal",
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
        readonly=True,
    )
    check_number = fields.Char(
        readonly=True,
    )
    l10n_mx_edi_payment_method_id = fields.Many2one(
        comodel_name="l10n_mx_edi.payment.method",
        readonly=True,
        string="Payment Method",
    )
    l10n_edi_employee_id = fields.Many2one(
        comodel_name="hr.employee",
        readonly=True,
        string="Employee",
    )
    state = fields.Char(
        readonly=True,
    )

    def _compute_partner_category_ids(self):
        for rec in self:
            rec.partner_category_ids = rec.partner_id.category_id.filtered(lambda c: c.parent_path.startswith('398'))

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
        "account.journal": [
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
            SELECT
                aml.id,
                am.name AS move_name,
                am.date,
                am.id AS move_id,
                am.l10n_mx_edi_payment_method_id,
                am.ref AS reference,
                aml.name AS description,
                CASE
                WHEN am.state = 'cancel' THEN 0
                ELSE aml.balance END AS amount,
                aml.currency_id,
                aml.partner_id,
                aa.name ->> 'en_US' AS account_name,
                aa.id AS account_id,
                am.state,
                aj.id AS journal_id,
                ap.check_number,
                ap.l10n_edi_employee_id
            FROM account_move_line AS aml
                LEFT JOIN account_journal AS aj ON aj.id = aml.journal_id
                LEFT JOIN account_account AS aa ON aa.id = aml.account_id
                LEFT JOIN account_move AS am ON am.id = aml.move_id
                LEFT JOIN account_payment AS ap ON ap.move_id = am.id
            WHERE
                aj.id NOT IN (19)
                AND aa.id IN (
                    SELECT apml.payment_account_id
                    FROM account_payment_method_line AS apml
                    WHERE apml.payment_method_id IN (
                        SELECT apm.id
                        FROM account_payment_method AS apm
                        WHERE apm.payment_type = 'outbound'
                    )
                    AND apml.journal_id IN (
                        SELECT aj2.id
                        FROM account_journal AS aj2
                        WHERE aj2.type = 'bank'
                    )
                )
        """
