# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).


from odoo import fields, models


class ProductCategoryClass(models.Model):
    _name = "product.category.class"
    _description = "Product Category Class"

    name = fields.Char(required=True)
    cpt = fields.Float(required=True, default=0.0)
