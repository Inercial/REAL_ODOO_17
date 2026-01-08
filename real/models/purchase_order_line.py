# Copyright 2020, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).


from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    @api.depends("product_id")
    def _compute_has_restriction(self):
        for line in self:
            categories = line._get_restrict_product_categories()
            has_restriction = False
            if line.product_id.categ_id.id in categories.ids:
                has_restriction = True
                line.has_restriction = has_restriction
            line.has_restriction = has_restriction

    has_restriction = fields.Boolean(
        compute="_compute_has_restriction",
        store=True,
    )

    def _get_restrict_product_categories(self):
        category_model = self.env["product.category"]
        categories = category_model.search([("is_mp_category", "=", True)])
        return categories

    @api.onchange("product_id")
    def _onchange_product_id(self):
        has_group = self.env.user.has_group("real.res_groups_can_add_mp_products")
        if self.has_restriction and not has_group:
            raise ValidationError(_("You cannot add products with categories of MP"))
