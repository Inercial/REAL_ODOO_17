# Copyright 2021, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class Stockpicking(models.Model):
    _inherit = "stock.picking"

    tons_display = fields.Float(
        digits="Product Unit of Measure",
        compute="_compute_tons",
        store=True,
        string="Tons",
    )

    @api.depends("move_ids_without_package")
    def _compute_tons(self):
        for rec in self:
            rec.tons_display = sum(rec.move_ids_without_package.mapped("tons_display"))
