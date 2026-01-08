# Copyright 2020, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

{
    "name": "Report Stock Picking Real",
    "summary": "Modify report to adapt real requirements",
    "version": "17.0.1.0.4",
    "category": "Stock",
    "author": "Jarsa",
    "website": "https://www.jarsa.com",
    "license": "LGPL-3",
    "depends": [
        "stock",
        "stock_barcode",
    ],
    "data": [
        "data/decimal_precision_data.xml",
        "views/stock_picking_view.xml",
        "views/stock_move_line_view.xml",
        "views/stock_move_view.xml",
        "reports/report_deliveryslip.xml",
        "reports/report_stock_picking.xml",
    ],
    "installable": True,
}
