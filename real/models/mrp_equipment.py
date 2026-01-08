# Copyright 2020, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).


from odoo import fields, models


class MrpEquipment(models.Model):
    _name = "mrp.equipment"
    _description = "Equipment"

    name = fields.Char(required=True)
