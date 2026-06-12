from odoo import fields, models


class MrpBom(models.Model):
    _inherit = "mrp.bom"

    x_studio_formula = fields.Char(string="Fórmula")
