# Copyright 2021, Jarsa
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, models


class ReportAccountAgedPartner(models.AbstractModel):
    _inherit = "account.aged.partner.balance.report.handler"

    @api.model
    def _get_sql(self):
        res = super()._get_sql()
        res = res.replace(
            "move.name AS move_name,",
            "move.name || ' (' || move.ref || ')' AS move_name,",
        )
        return res
