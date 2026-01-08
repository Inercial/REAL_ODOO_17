# Copyright 2021, Jarsa Sistemas
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class CollectionReportReal(models.Model):
    _name = "collection.report.real"
    _description = "Collection by salesman"
    _auto = False
    _rec_name = "payment_date"
    _order = "payment_date desc, invoice_user_id desc"

    invoice_name = fields.Char(
        readonly=True,
    )
    invoice_user_id = fields.Many2one(comodel_name="res.users", readonly=True, string="Salesman")
    payment_date = fields.Date(
        readonly=True,
    )
    max_date = fields.Date(
        readonly=True,
    )
    partner_id = fields.Many2one(
        comodel_name="res.partner",
        readonly=True,
    )
    days_invoice = fields.Integer(
        readonly=True,
    )
    total = fields.Monetary(
        readonly=True,
    )
    total_0_60 = fields.Monetary(
        readonly=True,
    )
    total_more_60 = fields.Monetary(
        readonly=True,
    )
    currency_id = fields.Many2one(
        comodel_name="res.currency",
        readonly=True,
    )

    _depends = {
        "account.move": ["id", "invoice_user_id", "invoice_date_due", "move_type", "state"],
        "account.move.line": [
            "name",
            "partner_id",
            "date",
            "move_id",
            "credit",
            "account_id",
        ],
        "account.account": [
            "id",
        ],
        "account.partial.reconcile": [
            "id",
            "amount",
            "credit_move_id",
            "debit_move_id",
        ],
    }

    @property
    def _table_query(self):
        return """
        SELECT
            apr.id,
            apr.max_date,
            invoice_move.invoice_user_id,
            invoice_move_line.name AS invoice_name,
            invoice_move_line.partner_id AS partner_id,
            bank_move_line.date AS payment_date,
            invoice_move.invoice_date_due,
            bank_move_line.date - invoice_move.invoice_date_due AS days_invoice,
            apr.amount as total,
            bank_move_line.currency_id,
            CASE
                WHEN bank_move_line.date - invoice_move.invoice_date_due <= 60
                THEN apr.amount
                ELSE 0
                END AS total_0_60,
            CASE
                WHEN bank_move_line.date - invoice_move.invoice_date_due > 60
                THEN apr.amount
                ELSE 0
                END AS total_more_60
        FROM account_partial_reconcile AS apr
            LEFT JOIN account_move_line AS bank_move_line ON apr.credit_move_id = bank_move_line.id
            LEFT JOIN account_move_line AS invoice_move_line ON apr.debit_move_id = invoice_move_line.id
            LEFT JOIN account_move AS invoice_move ON invoice_move_line.move_id = invoice_move.id
        WHERE
        apr.credit_move_id IN (
            SELECT aml.id
            FROM account_move_line AS aml
            LEFT JOIN account_move AS am ON am.id = aml.move_id
            WHERE
            aml.account_id = 3 AND
            aml.credit > 0 AND
            am.move_type = 'entry' AND
            am.state != 'cancel') OR
        apr.debit_move_id IN (
            SELECT aml.id
            FROM account_move_line AS aml
            LEFT JOIN account_move AS am ON am.id = aml.move_id
            WHERE
            aml.account_id = 3 AND
            aml.credit > 0 AND
            am.move_type = 'entry' AND
            am.state != 'cancel')
        UNION
        SELECT
            am.id,
            am.date,
            am.invoice_user_id,
            am.name AS invoice_name,
            am.partner_id,
            NULL AS payment_date,
            am.invoice_date_due,
            0 AS days_invoice,
            am.amount_total AS total,
            am.currency_id,
            0 AS total_0_60,
            0 AS total_more_60
        FROM account_move AS am
        WHERE
            am.move_type = 'out_refund'
            AND am.payment_state = 'not_paid'
            AND am.state = 'posted'
        """
