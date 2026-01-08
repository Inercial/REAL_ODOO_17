# Copyright 2021, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class ProductCategory(models.Model):
    _inherit = "product.category"

    is_mp_category = fields.Boolean("Is MP Category")
    category_class_id = fields.Many2one("product.category.class")
    ebitda_report = fields.Boolean(default=False)
