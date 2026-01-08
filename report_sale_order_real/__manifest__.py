# Copyright 2020, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

{
    "name": "Report Sale Order Real",
    "summary": "Modify report to adapt real requirements",
    "version": "17.0.1.0.0",
    "category": "Sale",
    "author": "Jarsa",
    "website": "https://www.jarsa.com",
    "license": "LGPL-3",
    "depends": [
        "sale_management",
        "report_stock_picking_real",
        "sale_pdf_quote_builder",
    ],
    "data": [
        "views/sale_order_view.xml",
        "reports/report_sale_order.xml",
        "reports/report_sale_order_quotation.xml",
        "reports/report_sale_order_order.xml",
        "reports/sale_order_reports.xml",
    ],
    "installable": True,
}
