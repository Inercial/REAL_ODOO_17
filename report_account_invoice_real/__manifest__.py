# Copyright 2020, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

{
    "name": "Report Account Invoice Real",
    "summary": "Modify report to adapt real requirements",
    "version": "17.0.1.0.4",
    "category": "Accounting",
    "author": "Jarsa",
    "website": "https://www.jarsa.com",
    "license": "LGPL-3",
    "depends": [
        "l10n_mx_edi",
        "report_stock_picking_real",
        "account_payment_order_banorte",
        "account_move_reversal",
        "real",
    ],
    "data": [
        "views/account_move_view.xml",
        "reports/report_account_invoice_base.xml",
        "reports/report_account_invoice_original.xml",
        "reports/report_account_invoice_without_amount.xml",
        "reports/report_account_invoice_credit_memo.xml",
        "reports/report_account_invoice_attachment_nc.xml",
        "reports/report_account_invoice_instructions.xml",
        "reports/report_account_invoice_vendor_base.xml",
        "reports/report_account_invoice_vendor_bill.xml",
        "reports/report_account_invoice_vendor_credit_note.xml",
        "reports/report_account_invoice_delivery_order.xml",
        "reports/report_account_invoice_journal_base.xml",
        "reports/report_account_invoice_sales_journal.xml",
        "reports/report_account_invoice_credit_journal.xml",
        "reports/report_account_invoice_purchase_journal.xml",
        "reports/report_account_invoice_poliza.xml",
        "reports/report_account_invoice_reports.xml",
    ],
    "installable": True,
}
