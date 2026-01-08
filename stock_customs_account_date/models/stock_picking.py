# Copyright 2019, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).


from odoo import api, fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    accounting_date = fields.Date(copy=False)
    exchange_rate = fields.Float(compute="_compute_exchange_rate", digits=(12, 4))

    @api.depends("accounting_date")
    def _compute_exchange_rate(self):
        usd = self.env.ref("base.USD")
        mxn = self.env.ref("base.MXN")
        for rec in self:
            date = rec.accounting_date
            if not date:
                date = fields.Date.context_today(rec)
            rec.exchange_rate = self.env["res.currency"]._get_conversion_rate(usd, mxn, rec.company_id, date)
