# Copyright 2020, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).


from markupsafe import Markup
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

    @api.model_create_multi
    def create(self, vals_list):
        lines = super(StockMove, self).create(vals_list)
        for picking in lines.mapped('picking_id'):
            relevant_lines = lines.filtered(lambda l: l.picking_id == picking)
            items_html = "".join([
                f"<li>Producto: <b>{l.product_id.display_name}</b> - Cantidad: <b>{l.quantity}</b></li>"
                for l in relevant_lines
            ])
            body = Markup("<b>Notificación de sistema:</b> Registro de nuevos productos:<ul>{}</ul>").format(
                Markup(items_html)
            )
            picking.message_post(body=body)
        return lines

    def write(self, vals):
        if 'quantity' in vals:
            previous_data = {line.id: line.quantity for line in self}
            result = super(StockMove, self).write(vals)
            for picking in self.mapped('picking_id'):
                relevant_lines = self.filtered(lambda l: l.picking_id == picking)
                changes_html = ""
                for line in relevant_lines:
                    old_qty = previous_data.get(line.id)
                    new_qty = vals.get('quantity')
                    if old_qty != new_qty:
                        changes_html += f"<li>Producto: <b>{line.product_id.display_name}</b> - Demanda anterior: <b>{old_qty}</b> | Nueva Demanda: <b>{new_qty}</b></li>"
                
                if changes_html:
                    body = Markup("<b>Ajuste de inventario:</b> Se han modificado las cantidades en las siguientes líneas:<ul>{}</ul>").format(
                        Markup(changes_html)
                    )
                    picking.message_post(body=body)
            return result
        return super(StockMove, self).write(vals)

    def unlink(self):
        logs_by_picking = {}
        for line in self:
            if line.picking_id:
                if line.picking_id not in logs_by_picking:
                    logs_by_picking[line.picking_id] = ""
                logs_by_picking[line.picking_id] += f"<li>Producto: <b>{line.product_id.display_name}</b> - Cantidad removida: <b>{line.quantity}</b></li>"
        for picking, items_html in logs_by_picking.items():
            body = Markup("<b>Registro de eliminación:</b> Se han removido los siguientes elementos del documento:<ul>{}</ul>").format(
                Markup(items_html)
            )
            picking.message_post(body=body)
            
        return super(StockMove, self).unlink()


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    equipment_id = fields.Many2one(
        related="move_id.equipment_id",
    )
    parent_category_id = fields.Many2one(
        related="product_id.categ_id.parent_id",
        store=True,
    )
