# Copyright 2020, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def _domain_way_of_shipment(self):
        category = self.env.ref("real.res_partner_category_supplier_freight", False)
        category_id = False
        if category:
            category_id = category.id
        return [("category_id", "=", category_id)]

    way_of_shipment_id = fields.Many2one(
        "res.partner", domain=lambda self: self._domain_way_of_shipment(), tracking=True
    )
    salesman_id = fields.Many2one(related="sale_id.user_id", store=True)
    way_shipment_type_id = fields.Many2one(related="partner_id.way_shipment_type_id", store=True)
    hide_picking_block = fields.Boolean(compute="_compute_hide_picking_block", store=False)
    machine_id = fields.Many2one("mrp.equipment", ondelete="restrict", compute="_compute_machine_name")

    @api.model
    def _compute_machine_name(self):
        for record in self:
            record.machine_id = self.env["mrp.production"].search([("name", "=", self.origin)]).equipment_id

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for rec in records:
            ubication = rec.client_location
            location_id = rec.location_id.id
            if ubication == "local" and location_id == 8:
                rec.update(
                    {
                        "priority": "1",
                    }
                )
        return records

    def _compute_hide_picking_block(self):
        self.hide_picking_block = self.user_has_groups("real.res_groups_hide_picking_block")

    def location_check(self):
        for line in self.move_line_ids_without_package:
            if line.location_id not in self.location_id and line.location_id.location_id not in self.location_id:
                raise UserError(_("The origin location of each line must match that of the picking"))
            if (
                line.location_dest_id not in self.location_dest_id
                and line.location_dest_id.location_id not in self.location_dest_id
            ):
                raise UserError(_("The destination location of each line must match that of the picking"))

    def button_validate(self):
        self.location_check()
        return super().button_validate()
