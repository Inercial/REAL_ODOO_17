# Copyright 2021, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).


from odoo import fields, models


class ExpenseReportReal(models.Model):
    _name = "expense.report.real"
    _description = "Expense Report for Real"

    name = fields.Char(
        readonly=True,
        string="Expenses",
    )
    debit = fields.Float(
        readonly=True,
    )
    credit = fields.Float(
        readonly=True,
    )
    journal_id = fields.Many2one(
        comodel_name="account.journal",
    )
    ref = fields.Char(
        readonly=True,
        string="Reference",
    )
    balance = fields.Float(
        readonly=True,
    )
    account_id = fields.Many2one(
        comodel_name="account.account",
        readonly=True,
    )
    date = fields.Date()
