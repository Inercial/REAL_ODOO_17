# Copyright 2020, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).


from odoo import _, api, fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    equipment_id = fields.Many2one(
        "mrp.equipment",
        readonly=True,
    )
    parent_category_id = fields.Many2one(
        related="product_category_id.parent_id",
        store=True,
    )
    sale_order_id = fields.Many2one(
        related="picking_id.sale_id",
        string="Sale Order",
        store=True,
    )
    product_category_id = fields.Many2one(
        related="product_id.categ_id",
        store=True,
    )
    way_of_shipment_id = fields.Many2one(
        related="picking_id.way_of_shipment_id",
        store=True,
    )
    way_of_shipment_type_id = fields.Many2one(
        related="way_of_shipment_id.way_shipment_type_id",
        store=True,
    )
    picking_note = fields.Html(
        "Picking Notes",
        related="picking_id.note",
        store=True,
    )
    salesman_id = fields.Many2one(
        related="sale_order_id.user_id",
        store=True,
    )

    def _get_new_picking_values(self):
        values = super()._get_new_picking_values()
        sale = self.group_id.sale_id
        sro = self.env["stock.request.order"].search([("procurement_group_id", "=", self.group_id.id)])
        if sale and sale.way_of_shipment_id:
            values["way_of_shipment_id"] = sale.way_of_shipment_id.id
        if sro:
            values["way_of_shipment_id"] = sro.way_of_shipment_id.id
        return values

    @api.depends("raw_material_production_id.qty_producing", "product_uom_qty")
    def _compute_should_consume_qty(self):
        for move in self:
            mo = move.raw_material_production_id
            if not mo:
                move.should_consume_qty = 0
                continue
            if mo.qty_producing <= mo.product_qty:
                return super()._compute_should_consume_qty()
            move.should_consume_qty = mo.product_uom_id._compute_quantity(
                (mo.product_qty - mo.qty_produced) * move.unit_factor, mo.product_uom_id, rounding_method="HALF-UP"
            )

    def _set_quantity_done_prepare_vals(self, qty):
        mo = self.raw_material_production_id
        if mo:
            qty = mo.product_uom_id._compute_quantity(
                (mo.product_qty - mo.qty_produced) * self.unit_factor, mo.product_uom_id, rounding_method="HALF-UP"
            )
        return super()._set_quantity_done_prepare_vals(qty)

    def action_view_picking(self):
        self.ensure_one()
        return {
            "name": _("Picking"),
            "view_mode": "form",
            "res_model": "stock.picking",
            "type": "ir.actions.act_window",
            "res_id": self.picking_id.id,
        }

    def action_view_sale(self):
        self.ensure_one()
        return {
            "name": _("Sale Order"),
            "view_mode": "form",
            "res_model": "sale.order",
            "type": "ir.actions.act_window",
            "res_id": self.sale_order_id.id,
        }


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    equipment_id = fields.Many2one(
        related="move_id.equipment_id",
    )
    parent_category_id = fields.Many2one(
        related="product_id.categ_id.parent_id",
        store=True,
    )
