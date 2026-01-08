# Copyright 2022, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    client_location = fields.Selection(
        related="partner_id.client_location",
        store=True,
    )
