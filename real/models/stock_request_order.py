# Copyright 2021, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class StockRequestOrder(models.Model):
    _inherit = "stock.request.order"

    def _domain_way_of_shipment(self):
        category = self.env.ref("real.res_partner_category_supplier_freight", False)
        category_id = False
        if category:
            category_id = category.id
        return [("category_id", "=", category_id)]

    way_of_shipment_id = fields.Many2one(
        "res.partner",
        domain=lambda self: self._domain_way_of_shipment(),
        tracking=True,
    )
    way_shipment_type_id = fields.Many2one(related="partner_id.way_shipment_type_id")
    child_tag_ids = fields.Many2many(related="partner_id.child_tag_ids")
    partner_shipping_id = fields.Many2one(
        "res.partner",
        string="Delivery Address",
        readonly=True,
        domain=["|", ("company_id", "=", False), ("company_id", "=", "company_id")],
    )
    child_tag_required = fields.Boolean(default=True)

    @api.onchange("partner_id")
    def onchange_partner_id(self):
        """Use native method, because we need to execute first that method to
        change pricelist and then compute the price in every line.
        """
        self.way_of_shipment_id = self.partner_id.way_of_shipment_id

        if self.partner_id.child_tag_ids:
            self.partner_shipping_id = self.partner_id.child_tag_ids[0]
            self.child_tag_required = True

        if not self.partner_id.child_tag_ids:
            self.partner_shipping_id = False
            self.child_tag_required = False

    def action_confirm(self):
        res = super().action_confirm()
        partner_id = 0
        if self.picking_ids:
            if self.partner_shipping_id:
                partner_id = self.partner_shipping_id.id
            else:
                partner_id = self.partner_id.id

            self.picking_ids.write(
                {
                    "partner_id": partner_id,
                }
            )
        return res
