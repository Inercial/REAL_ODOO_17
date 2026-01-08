# Copyright 2021, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class WayOfShipmentType(models.Model):
    _name = "way.of.shipment.type"
    _description = "Way Of Shipment Type"

    name = fields.Char("Way Of Shipment Type", required=True, translate=True)
    days_to_delivery = fields.Integer()
