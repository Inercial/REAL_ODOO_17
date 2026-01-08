# Copyright 2021, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
# pylint: skip-file

from odoo import api, fields, models


class SaleInvoiceReportReal(models.Model):
    _name = "sale.invoice.report.real"
    _description = "Sale Invoice Report for Real"
    _auto = False
    _rec_name = "invoice_date"
    _order = "invoice_date desc"

    sale_id = fields.Many2one(
        comodel_name="sale.order",
        readonly=True,
    )

    account_id = fields.Many2one(
        comodel_name="account.account",
        readonly=True,
    )
    invoice_date = fields.Date(
        readonly=True,
    )
    invoice_date_due = fields.Date(
        readonly=True,
    )
    name = fields.Char(
        readonly=True,
    )
    description = fields.Char(
        readonly=True,
    )
    move_type = fields.Selection(
        selection=[
            ("out_invoice", "Invoice"),
            ("out_refund", "Credit Note"),
        ],
        readonly=True,
    )
    rectified_invoices = fields.Selection(
        selection=[
            ("unassigned", "Unassigned"),
            ("application_of_advance", "Application of Advance"),
            ("uncollectible_account", "Uncollectible account"),
            ("Special_discounts", "Special discounts"),
            ("discounts_promp_payment", "Discounts for prompt payment"),
            ("advance_refund", "Advance refund"),
            ("Seller_error", "Seller error"),
            ("custom_err", "Customer error"),
            ("shipment_delivery_mistake", "Shipment delivery mistake"),
            ("logistics_err", "Logistics error"),
            ("wet_shipping_material", "Wet shipping material"),
            ("broken_shipping_material", "Broken shipping material"),
            ("non_rotating_material", "Non-rotating material"),
            ("material_exit_sample", "Material exit as sample"),
            ("return_invoice_paid", "Return invoice paid"),
            ("physical_retur", "Physical return"),
            ("different_prices", "Different prices"),
            ("damaged_material", "Damaged Material"),
            ("customer_not_received", "Customer not received"),
            ("did_not_leave_plant", "Did not leave the plant"),
            ("rebilling_others", "Rebilling Others"),
            ("rebilling_date", "Rebilling by date"),
            ("rebilling_type_payment", "Rebilling by type of payment"),
            ("transfer_other_client", "Transfer to other client"),
        ],
        readonly=True,
    )
    invoice_user_id = fields.Many2one(
        comodel_name="res.users",
        readonly=True,
    )
    partner_id = fields.Many2one(
        comodel_name="res.partner",
        readonly=True,
    )
    seller_id = fields.Many2one(
        comodel_name="res.partner",
        readonly=True,
    )
    l10n_mx_edi_usage = fields.Selection(
        selection=[
            ("G01", "Acquisition of merchandise"),
            ("G02", "Returns, discounts or bonuses"),
            ("G03", "General expenses"),
            ("I01", "Constructions"),
            ("I02", "Office furniture and equipment investment"),
            ("I03", "Transportation equipment"),
            ("I04", "Computer equipment and accessories"),
            ("I05", "Dices, dies, molds, matrices and tooling"),
            ("I06", "Telephone communications"),
            ("I07", "Satellite communications"),
            ("I08", "Other machinery and equipment"),
            ("D01", "Medical, dental and hospital expenses."),
            ("D02", "Medical expenses for disability"),
            ("D03", "Funeral expenses"),
            ("D04", "Donations"),
            ("D05", "Real interest effectively paid for mortgage loans (room house)"),
            ("D06", "Voluntary contributions to SAR"),
            ("D07", "Medical insurance premiums"),
            ("D08", "Mandatory School Transportation Expenses"),
            ("D09", "Deposits in savings accounts, premiums based on pension plans."),
            ("D10", "Payments for educational services (Colegiatura)"),
            ("P01", "To define"),
        ],
        string="Usage",
        readonly=True,
    )
    state = fields.Selection(
        selection=[
            ("draft", "Draft"),
            ("posted", "Posted"),
            ("cancel", "Cancel"),
        ],
        readonly=True,
    )
    city = fields.Char(
        readonly=True,
    )
    partner_shipping_id = fields.Many2one(
        comodel_name="res.partner",
        string="Shipping Address",
        readonly=True,
    )
    delivery_city = fields.Char(
        readonly=True,
    )
    partner_category_id = fields.Many2one(
        comodel_name="res.partner.category",
        readonly=True,
    )
    way_of_shipment_id = fields.Many2one(
        comodel_name="res.partner",
        readonly=True,
    )
    default_code = fields.Char(
        readonly=True,
    )
    product_id = fields.Many2one(
        comodel_name="product.product",
        readonly=True,
    )
    product_name = fields.Char(
        readonly=True,
    )
    quantity = fields.Float(
        readonly=True,
    )
    price_unit = fields.Monetary(
        readonly=True,
    )
    currency_id = fields.Many2one(
        comodel_name="res.currency",
        readonly=True,
    )
    subtotal = fields.Monetary(
        readonly=True,
    )
    total = fields.Monetary(
        readonly=True,
    )
    document_amount_untaxed = fields.Monetary(
        readonly=True,
    )
    document_amount_total = fields.Monetary(
        readonly=True,
    )
    weight = fields.Float(
        readonly=True,
    )
    tons_litres = fields.Float(
        readonly=True,
    )
    tons_display = fields.Float(readonly=True, string="Tons")
    freight_cost = fields.Monetary(
        readonly=True,
    )
    freight_cost_ton = fields.Monetary(
        string="Freight Cost by Ton",
        readonly=True,
    )
    freight_weight = fields.Float(
        readonly=True,
    )
    unit_price_no_freight = fields.Monetary(
        readonly=True,
    )
    total_sale_no_freight = fields.Monetary(
        readonly=True,
    )
    total_sale_no_freight_with_tax = fields.Monetary(
        readonly=True,
    )
    freight_total = fields.Monetary(
        readonly=True,
    )
    freight_total_with_tax = fields.Monetary(
        readonly=True,
    )
    parent_category_id = fields.Many2one(
        comodel_name="product.category",
        readonly=True,
    )
    category_id = fields.Many2one(
        comodel_name="product.category",
        readonly=True,
    )
    partner_create_date = fields.Datetime(
        readonly=True,
    )
    partner_shipping_create_date = fields.Datetime(
        readonly=True,
    )
    forklift = fields.Boolean(
        readonly=True,
    )
    grouped_category_id = fields.Many2one(
        comodel_name="res.partner.category",
        string="Grouped",
        readonly=True,
    )
    partner_pricelist_id = fields.Many2one(
        comodel_name="product.pricelist",
        readonly=True,
    )
    order_pricelist_id = fields.Many2one(
        comodel_name="product.pricelist",
        readonly=True,
    )
    document_day = fields.Char(
        readonly=True,
    )
    document_day_name = fields.Char(
        readonly=True,
    )
    document_month = fields.Char(
        readonly=True,
    )
    document_year = fields.Char(
        readonly=True,
    )
    document_month_year = fields.Char(
        readonly=True,
    )

    _depends = {
        "account.move.line": [
            "quantity",
            "price_unit",
            "currency_id",
            "price_subtotal",
            "price_total",
            "tons_display",
            "freight_cost",
            "move_id",
            "product_id",
            "name",
        ],
        "account.move": [
            "invoice_date",
            "name",
            "move_type",
            "l10n_mx_edi_usage",
            "state",
            "invoice_user_id",
            "partner_id",
            "partner_shipping_id",
            "move_type",
            "id",
            "rectified_invoices",
            "invoice_date_due",
        ],
        "res.partner": [
            "city_id",
            "city",
            "city_id",
            "create_date",
        ],
        "product.product": [
            "default_code",
            "weight",
            "freight_weight",
            "id",
            "product_tmpl_id",
        ],
        "product.template": [
            "name",
            "categ_id",
        ],
        "product.category": [
            "name",
            "id",
        ],
        "sale.order": [
            "name",
            "id",
        ],
        "res.users": [
            "id",
            "partner_id",
        ],
        "ir.property": [
            "res_id",
            "value_reference",
        ],
        "product.pricelist": ["id"],
        "product.template.attribute.value": [
            "id",
            "product_attribute_value_id",
        ],
        "product.attribute.value": [
            "name",
            "id",
        ],
        "account.account": [
            "id",
        ],
    }

    @property
    def _table_query(self):
        return "%s %s %s %s" % (self._select(), self._from(), self._where(), self._order_by())

    @api.model
    def _select(self):
        return """
    SELECT AML.id AS id,
    AM.invoice_date,
    AM.invoice_date_due,
    AM.name,
    AM.move_type,
    AM.rectified_invoices,
    CASE WHEN AM.rectified_invoices IN (
        'rebilling_date','rebilling_type_payment','rebilling_others',
        'physical_retur','did_not_leave_plant','uncollectible_account',
        'broken_shipping_material','shipment_delivery_mistake','transfer_other_client',
        'customer_not_received','Seller_error') THEN 'Refund'
        WHEN AM.rectified_invoices IN ('Special_discounts',
        'different_prices','return_invoice_paid','damaged_material') THEN 'Discounts'
        WHEN AM.rectified_invoices IN ('discounts_promp_payment') THEN 'Promp Payment'
        ELSE 'unassigned' END AS rectified_invoices_type,
    AM.l10n_mx_edi_usage as l10n_mx_edi_usage,
    AM.state,
    AM.invoice_user_id,
    AM.partner_id,
    rpR.id AS seller_id,
    CASE
                WHEN RP.city_id IS NULL
                THEN RP.city
                ELSE (
                    SELECT rc.name ->> 'es_MX'
                    FROM res_city AS rc
                    WHERE RP.city_id = rc.id)
                END AS city,
    AM.partner_shipping_id,
    CASE
                WHEN RP2.city_id IS NULL
                THEN RP2.city
                ELSE (
                    SELECT rc.name ->> 'es_MX'
                    FROM res_city AS rc
                    WHERE RP2.city_id = rc.id)
                END AS delivery_city,
    (SELECT rpc.id
        FROM res_partner_res_partner_category_rel AS rel
        LEFT JOIN res_partner_category AS rpc ON rpc.id = rel.category_id
        WHERE rel.partner_id = RP2.id AND rpc.parent_id = 319
        ORDER BY name asc LIMIT 1) AS partner_category_id,
    rpS.id AS way_of_shipment_id,
    aml.account_id,
    PP.default_code,
    pp.id AS product_id,
    trim(PT.name->>'es_MX' || ' ' || coalesce(pav.name->>'es_MX','')) AS product_name,
    CASE
        WHEN AM.move_type = 'out_refund'
        THEN AML.quantity * -1
        ELSE AML.quantity END AS quantity,
    CASE
        WHEN AM.move_type = 'out_refund'
        THEN AML.price_unit * -1
        ELSE AML.price_unit END AS price_unit,
    AML.currency_id,
    CASE
        WHEN AM.move_type = 'out_refund'
        THEN AML.price_subtotal * -1
        ELSE AML.price_subtotal END AS subtotal,
    CASE
        WHEN AM.move_type = 'out_refund'
        THEN AML.price_total * -1
        ELSE AML.price_total END AS total,
    CASE
        WHEN AM.move_type = 'out_refund'
        THEN AM.amount_untaxed * -1
        ELSE AM.amount_untaxed END AS document_amount_untaxed,
    CASE
        WHEN AM.move_type = 'out_refund'
        THEN AM.amount_total * -1
        ELSE AM.amount_total END AS document_amount_total,
    CASE
        WHEN AM.move_type = 'out_refund'
        THEN PP.weight * -1
        ELSE PP.weight END AS weight,
    CASE
        WHEN AM.move_type = 'out_refund'
        THEN ROUND(AML.quantity * PP.weight, 2) * -1
        ELSE ROUND(AML.quantity * PP.weight, 2) END
        AS tons_litres,
    AML.name AS description,
    CASE
        WHEN AM.move_type = 'out_refund'
        THEN AML.tons_display * -1
        ELSE AML.tons_display END AS tons_display,
    AML.freight_cost,
    CASE WHEN AM.move_type = 'out_refund'
        THEN (AML.freight_cost * 1000) * -1
        ELSE (AML.freight_cost * 1000) END AS freight_cost_ton,
    pp.freight_weight AS freight_weight,
    CASE WHEN AM.move_type = 'out_refund'
        THEN (AML.price_unit - (AML.freight_cost * pp.freight_weight)) * -1
        ELSE (AML.price_unit - (AML.freight_cost * pp.freight_weight)) END
        AS unit_price_no_freight,
    CASE WHEN AM.move_type = 'out_refund'
        THEN ((AML.price_unit -
        (AML.freight_cost * pp.freight_weight)) * AML.quantity) * -1
        ELSE (AML.price_unit -
        (AML.freight_cost * pp.freight_weight)) * AML.quantity END
        AS total_sale_no_freight,
    CASE WHEN AM.move_type = 'out_refund'
        THEN (((AML.price_unit -
            (AML.freight_cost * pp.freight_weight)) * AML.quantity) * 1.16) * -1
        ELSE (((AML.price_unit -
            (AML.freight_cost * pp.freight_weight)) * AML.quantity) * 1.16) END
        AS total_sale_no_freight_with_tax,
    CASE WHEN AM.move_type = 'out_refund'
        THEN ((AML.freight_cost * pp.freight_weight) * AML.quantity) * -1
        ELSE (AML.freight_cost * pp.freight_weight) * AML.quantity END
        AS freight_total,
    CASE WHEN AM.move_type = 'out_refund'
        THEN (((AML.freight_cost * pp.freight_weight) * AML.quantity) * 1.16) * -1
        ELSE (((AML.freight_cost * pp.freight_weight) * AML.quantity) * 1.16) END
        AS freight_total_with_tax,
    (SELECT PC2.id FROM product_category AS PC2 WHERE PC2.id = PC.parent_id) AS parent_category_id,
    PC.id AS category_id,
    RP.create_date AS partner_create_date,
    RP2.create_date AS partner_shipping_create_date,
    RP2.loads AS forklift,
    (SELECT
        rpc.id
        FROM res_partner_res_partner_category_rel AS rel
        LEFT JOIN res_partner_category AS rpc ON rpc.id = rel.category_id
        WHERE rel.partner_id = RP2.id AND rpc.parent_id = 1
        ORDER BY name asc LIMIT 1) AS grouped_category_id,
    PPL.id AS partner_pricelist_id,
    PPL2.id AS order_pricelist_id,
    SO.id AS sale_id,
    to_char(AM.invoice_date, 'DD') AS document_day,
    to_char(AM.invoice_date, 'TMDay') AS document_day_name,
    to_char(AM.invoice_date, 'TMMonth') AS document_month,
    to_char(AM.invoice_date, 'YYYY') AS document_year,
(to_char(AM.invoice_date, 'TMMonth') || ', ' || to_char(am.invoice_date, 'YYYY')) AS document_month_year
    """

    @api.model
    def _from(self):
        return """
            FROM account_move_line AS AML
    LEFT JOIN account_move AS AM ON AM.id = AML.move_id
    LEFT JOIN res_partner AS RP ON RP.id = AM.partner_id
    LEFT JOIN res_partner AS RP2 ON RP2.id = AM.partner_shipping_id
    LEFT JOIN product_product AS PP ON PP.id = AML.product_id
    LEFT JOIN product_template AS PT ON PT.id = PP.product_tmpl_id
    LEFT JOIN product_category AS PC ON PC.id = PT.categ_id
    LEFT JOIN sale_order AS SO ON SO.name = AM.invoice_origin AND so.partner_id = am.partner_id
    LEFT JOIN res_users AS ru2 ON ru2.id = am.invoice_user_id
    LEFT JOIN res_partner AS rpS ON rpS.id = AM.way_of_shipment_id
    LEFT JOIN res_partner AS rpR ON rpR.id = ru2.partner_id
    LEFT JOIN ir_property AS ir ON substr(ir.res_id,1,strpos(ir.res_id,',') -1) = 'res.partner'
        AND CAST(substr(ir.res_id,strpos(ir.res_id,',')+1) AS INT) = RP2.id
        AND substr(ir.value_reference,1,strpos(ir.value_reference,',') -1) = 'product.pricelist'
LEFT JOIN product_pricelist AS PPL ON PPL.id = CAST(substr(ir.value_reference,strpos(ir.value_reference,',')+1) AS INT)
    LEFT JOIN product_pricelist AS PPL2 ON PPL2.id = so.pricelist_id
    LEFT JOIN product_variant_combination pvc on pvc.product_product_id = pp.id
    LEFT JOIN product_template_attribute_value ptav on ptav.id = pvc.product_template_attribute_value_id
    LEFT JOIN product_attribute_value pav on pav.id = ptav.product_attribute_value_id
    LEFT JOIN account_account aa on aa.id = aml.account_id
        """

    @api.model
    def _where(self):
        return """
            WHERE AM.state IN ('posted')
                AND AM.move_type IN ('out_invoice','out_refund')
                AND AML.price_subtotal > 0
                AND AA.account_type in ('income', 'income_other')
                AND AML.product_id not in (671)
                AND AML.account_id NOT IN (5,24)
        """

    @api.model
    def _order_by(self):
        return """
            ORDER BY am.invoice_date, am.name ASC
        """
