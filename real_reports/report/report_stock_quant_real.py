# Copyright 2022, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).


from odoo import api, fields, models


class ReportStockQuantReal(models.Model):
    _name = "report.stock.quant.real"
    _description = "Report quant real"

    product_id = fields.Many2one(
        comodel_name="product.product",
        store=True,
    )
    pending_qty_foreign = fields.Float(
        store=True,
    )
    pending_qty_local = fields.Float(
        store=True,
    )
    product_uom_qty_local = fields.Float(
        readonly=True,
    )
    reserved_availability_local = fields.Float(
        readonly=True,
    )
    product_uom_qty_foreign = fields.Float(
        readonly=True,
    )
    reserved_availability_foreign = fields.Float(
        readonly=True,
    )
    pending_total = fields.Float(
        compute="_compute_quantities",
        readonly=True,
    )
    available_space = fields.Float(
        readonly=True,
    )
    excess = fields.Float(
        compute="_compute_quantities",
        readonly=True,
    )
    batch_size = fields.Float(
        readonly=True,
    )
    batch_number = fields.Float(compute="_compute_quantities", readonly=True)

    @api.depends(
        "product_uom_qty_foreign",
        "product_uom_qty_local",
        "pending_qty_foreign",
        "pending_qty_local",
        "available_space",
        "batch_size",
    )
    def _compute_quantities(self):
        for rec in self:
            pending_qty_local = rec.product_uom_qty_local - rec.reserved_availability_local
            pending_qty_foreign = rec.product_uom_qty_foreign - rec.reserved_availability_foreign
            pending_total = rec.pending_qty_foreign + rec.pending_qty_local
            rec.update(
                {
                    "pending_qty_foreign": abs(pending_qty_foreign),
                    "pending_qty_local": abs(pending_qty_local),
                    "pending_total": pending_total,
                    "excess": rec.available_space - pending_total,
                    "batch_number": pending_total / rec.batch_size or 1,
                }
            )
