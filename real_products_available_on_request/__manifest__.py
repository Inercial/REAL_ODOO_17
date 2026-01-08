# Copyright 2020, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

{
    "name": "Real Products Available On Request",
    "summary": "Module Add field client_location",
    "version": "17.0.1.0.1",
    "category": "Instance",
    "author": "Jarsa",
    "website": "https://www.jarsa.com",
    "license": "LGPL-3",
    "depends": [
        "sale",
        "stock_analytic",
    ],
    "data": [
        "views/res_partner_view.xml",
        "views/sale_order_view.xml",
        "views/stock_picking_view.xml",
        "views/stock_move_view.xml",
    ],
    "installable": True,
}
