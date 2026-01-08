# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).


from odoo import fields, models


class MrpLicensePlate(models.Model):
    _name = "mrp.license.plate"
    _description = "License Plate"

    name = fields.Char(required=True)
    active = fields.Boolean(default=True)
