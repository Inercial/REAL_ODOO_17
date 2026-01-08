# Copyright 2021, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).


from odoo import api, fields, models


class MrpRequest(models.Model):
    _inherit = "mrp.request"

    available_qty = fields.Float(compute="_compute_available_qty", store=True)
    product_max_qty = fields.Float(compute="_compute_orderpoint", store=True)
    product_min_qty = fields.Float(compute="_compute_orderpoint", store=True)
    qty_multiple = fields.Float(compute="_compute_orderpoint")
    qty_ordered = fields.Float(compute="_compute_qty_ordered")
    qty_in_production = fields.Float(compute="_compute_qty_in_production", store=True)
    local = fields.Float(compute="_compute_local", store=True)
    foreigner = fields.Float(compute="_compute_foreigner", store=True)
    qty_to_max = fields.Float(compute="_compute_qty_to_max", string="Pending Max Inv", store=True)
    forecasted_qty = fields.Float(compute="_compute_forecasted_qty", store=True)
    parent_category_id = fields.Many2one(
        related="product_id.categ_id.parent_id",
        store=True,
    )

    @api.depends("product_id")
    def _compute_available_qty(self):
        for rec in self:
            quantity = 0
            quant = self.env["stock.quant"].search(
                [
                    ("product_id", "=", rec.product_id.id),
                    ("location_id", "in", [8, 19, 11]),
                    # 8 Stock ID, 19 Quality ID, 11 Preparación
                ]
            )
            if quant:
                quantity = sum(quant.mapped("quantity"))
            rec.available_qty = quantity

    @api.depends("product_id")
    def _compute_orderpoint(self):
        for rec in self:
            min_qty, max_qty, qty_multiple = 0, 0, 0
            orderpoint = self.env["stock.warehouse.orderpoint"].search(
                [
                    ("location_id", "=", 8),
                    ("product_id", "=", rec.product_id.id),
                ],
                limit=1,
            )
            if orderpoint:
                min_qty = orderpoint.qty_min
                max_qty = orderpoint.product_max_qty
                qty_multiple = orderpoint.qty_multiple
            rec.product_min_qty = min_qty
            rec.product_max_qty = max_qty
            rec.qty_multiple = qty_multiple

    @api.depends("product_id")
    def _compute_qty_ordered(self):
        for rec in self:
            qty_ordered = 0
            # Customer ID = 5
            # Muestras ID = 24
            # Instalación de muestras ID = 38
            # Quejas = 39
            moves = self.env["stock.move"].search(
                [
                    ("product_id", "=", rec.product_id.id),
                    ("state", "not in", ["cancel", "done"]),
                    ("location_dest_id", "in", [5, 24, 38, 39]),
                ]
            )
            if moves:
                qty_ordered = sum(moves.mapped("product_uom_qty"))
            rec.qty_ordered = qty_ordered

    @api.depends("product_id")
    def _compute_qty_in_production(self):
        for rec in self:
            qty_in_production = 0
            moves = self.env["stock.move"].search(
                [
                    ("product_id", "=", rec.product_id.id),
                    ("location_id", "=", 15),  # Production ID
                    ("location_dest_id", "=", 19),  # Quality ID
                    ("state", "not in", ["cancel", "done"]),
                ]
            )
            if moves:
                qty_in_production = sum(moves.mapped("product_uom_qty"))
            rec.qty_in_production = qty_in_production

    @api.depends("product_id")
    def _compute_qty_to_max(self):
        for rec in self:
            rec.qty_to_max = rec.product_max_qty - (rec.available_qty + rec.qty_in_production)

    @api.depends("product_id", "available_qty", "qty_ordered", "qty_in_production")
    def _compute_forecasted_qty(self):
        for rec in self:
            total_forecasted_qty = 0
            moves = self.env["stock.move"].search(
                [
                    "&",
                    "&",
                    ("product_id", "=", rec.product_id.id),
                    ("state", "in", ["assigned", "waiting", "confirmed", "partially_available"]),
                    "|",
                    ("location_id", "=", 11),  # Preparacion
                    ("location_dest_id", "=", 24),  # Muestras
                ]
            )
            if moves:
                total_forecasted_qty = sum(moves.mapped("product_uom_qty"))
            rec.forecasted_qty = rec.available_qty + rec.qty_in_production - total_forecasted_qty

    @api.depends("product_id")
    def _compute_local(self):
        for rec in self:
            local_qty = 0
            moves = self.env["stock.move"].search(
                [
                    "&",
                    "&",
                    "&",
                    ("state", "in", ["assigned", "waiting", "confirmed", "partially_available"]),
                    ("product_id", "=", rec.product_id.id),
                    ("picking_id.client_location", "in", ["local", False]),  # Clientes locales y no establecidos
                    "|",
                    ("location_id", "=", 11),  # Preparacion
                    ("location_dest_id", "=", 24),  # Muestras
                ]
            )
            if moves:
                local_qty = sum(moves.mapped("product_uom_qty"))
            rec.local = local_qty

    @api.depends("product_id")
    def _compute_foreigner(self):
        for rec in self:
            foreigner_qty = 0
            moves = self.env["stock.move"].search(
                [
                    "&",
                    "&",
                    "&",
                    ("product_id", "=", rec.product_id.id),
                    ("state", "in", ["assigned", "waiting", "confirmed", "partially_available"]),
                    ("picking_id.client_location", "=", "foreigner"),
                    "|",
                    ("location_id", "=", 11),  # Preparacion
                    ("location_dest_id", "=", 24),  # Muestras
                ]
            )
            if moves:
                foreigner_qty = sum(moves.mapped("product_uom_qty"))
            rec.foreigner = foreigner_qty
