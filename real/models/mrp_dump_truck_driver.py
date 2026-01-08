# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).


from odoo import fields, models


class MrpDumpTruckDriver(models.Model):
    _name = "mrp.dump.truck.driver"
    _description = "Dump Truck Driver"

    name = fields.Char(required=True)
    active = fields.Boolean(default=True)
