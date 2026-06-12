# real — Real Instance

> **Version:** 17.0.1.0.36 | **License:** LGPL-3 | **Author:** Jarsa

<!-- ============================================================ -->
<!-- ENGLISH SECTION — Technical Reference                        -->
<!-- ============================================================ -->

## Overview

`real` is a vertical instance module for Odoo 17 that aggregates and customizes business logic across Sales, Manufacturing, Inventory, Accounting, CRM, and Purchasing for a specific client deployment. It extends core Odoo models including `sale.order`, `account.move`, `mrp.production`, `stock.picking`, `res.partner`, `crm.lead`, `hr.expense`, `purchase.order`, and many others with industry-specific fields, validations, security rules, and workflows. The module introduces new master data models (equipment, license plates, dump truck drivers, shipment types, product category classes) and enforces granular role-based access control through custom security groups and user roles. It also customizes several QWeb reports and adds computed inventory metrics (tons, liters, forecasted quantities) across the supply chain.

## Dependencies

### Odoo / OCA Modules

- `l10n_mx` — Mexican localization (fiscal fields, CFDI, DIOT)
- `sale_management` — Core sales order management
- `stock_customs_account_date` — Custom accounting date on stock operations
- `crm` — CRM leads and opportunities
- `mrp` — Manufacturing orders and BOMs
- `account_accountant` — Full accounting features
- `google_spreadsheet_import` — Google Sheets import integration
- `board` — Dashboard boards
- `base_user_role` — Role-based user groups
- `sale_crm` — CRM integration with sales quotations
- `base_address_extended` — Extended address fields (city model)
- `attachment_indexation` — Attachment full-text indexing
- `base_automation` — Automated actions engine
- `base_import_module` — Import modules from UI
- `base_vat` — VAT validation
- `product_matrix` — Product matrix in sale/purchase lines
- `stock_request_partner` — Stock requests with partner
- `report_sale_order_real` — Custom sale order report (local module)
- `report_stock_picking_real` — Custom picking report (local module)
- `account_payment_order` — Payment orders (OCA)
- `stock_picking_change_date` — Change scheduled date on pickings
- `contacts` — Contacts app
- `mrp_request` — Manufacturing requests (OCA/local)
- `hr_expense` — Employee expenses
- `l10n_mx_edi_hr_expense` — Mexican EDI for expenses
- `stock_request_analytic` — Analytic accounts on stock requests
- `account_reports` — Accounting reports engine
- `stock_landed_costs` — Landed costs on inventory
- `web` — Odoo web framework
- `l10n_mx_edi_advance` — Mexican advance payments (CFDI)
- `account_followup` — Customer follow-up
- `account_financial_risk` — Financial risk management (OCA)
- `l10n_mx_edi_sale` — Mexican EDI on sales
- `delivery` — Delivery methods

### Python Libraries

- `pytz` — Timezone handling in `sale_order.py`
- `markupsafe` — Safe HTML markup in `stock_move.py`, `sale_order.py`
- `psycopg2` — Direct DB operations in `res_partner.py` for rank reset
- `xml.etree.ElementTree` — XML parsing for CFDI emisor in `account_move.py`
- `re` — Regular expressions for lot name validation in `stock_production_lot.py`

## Installation

1. Place the module folder `real` in your Odoo addons path.
2. Update the module list: **Settings → Activate Developer Mode → Update Apps List**.
3. Search for `Real Instance` and click **Install**.
4. After installation, review the system parameter `real.block_inventory_priority` (default: `False`) under **Settings → Technical → Parameters → System Parameters** to optionally enable automatic priority assignment for local pickings.
5. Assign users to the appropriate roles defined in `security/res_user_roles_data.xml` (Seller, Collection, Operations, Shipments, Marketing, Sales Manager, Manufacturing, Accounting, Payments, Foreign Shipments).

---

## Models Reference

### `account.move` — Account Move (inherited)

| Field Name | Type | Label (string) | Description |
|---|---|---|---|
| `way_of_shipment_id` | Many2one (`res.partner`) | Way of Shipment | Freight supplier linked to the invoice; filtered by `Supplier Freight` category |
| `way_shipment_type_id` | Many2one (related `partner_id.way_shipment_type_id`) | Way Shipment Type | Shipment type inherited from partner |
| `child_tag_ids` | Many2many (related `partner_id.child_tag_ids`) | Contacts | Delivery contacts inherited from partner |
| `is_freight_supplier` | Boolean | — | Marks if the partner is a freight supplier; controls visibility of freight destination fields |
| `state_id` | Many2one (`res.country.state`) | Freight Destination State | Destination state for freight invoices (MX only) |
| `city_id` | Many2one (`res.city`) | Freight Destination City | Destination city filtered by selected state |
| `stop_inv` | Boolean | Don't pay this invoice | Blocks invoice from being registered as paid |
| `tons_display` | Float (computed) | Tons | Sum of tons from all invoice lines |
| `previous_folio` | Char | Previous Folio | Reference to a prior folio |
| `x_studio_tarimas` | Integer | Tarimas | Number of pallets |
| `x_studio_departamento` | Selection (related) | Departamento | Department from partner |
| `xml_emisor` | Char | Nombre proveedor global | Emisor name parsed from attached XML for global supplier |

**Key methods:**
- `get_xml_content`: Parses attached XML file to extract the `Emisor` name for partner "PROVEEDOR GLOBAL"
- `_compute_tons`: Sums `tons_display` from all `invoice_line_ids`
- `_compute_l10n_mx_edi_payment_policy`: Overrides payment policy computation; forces `PUE` for all invoices, sets `PPD` only for out_invoices with future due date or multiple payment term lines
- `action_register_payment`: Raises `UserError` if any invoice in the set has `stop_inv = True`
- `default_get`: Sets today's date as default `date` and `invoice_date` for vendor bills
- `action_post`: Calls `_chek_pdf_xml` and `get_xml_content` before posting
- `_chek_pdf_xml`: Validates that Mexican vendor bills have both a PDF and XML attachment before posting
- `_domain_way_of_shipment`: Returns domain filtering partners to the `Supplier Freight` category
- `_onchange_partner_id`: Auto-fills shipping partner, way of shipment, and responsible user from partner's child tags; marks `is_freight_supplier`
- `_onchange_partner_shipping_id`: Auto-fills `way_of_shipment_id`, `invoice_user_id`, and `freight_cost` on lines from shipping partner
- `_onchange_invoice_line_ids`: Propagates `freight_cost` from shipping partner to all lines
- `_onchange_invoice_date_real`: Syncs `date` to `invoice_date` for vendor bills
- `_onchange_city_id`: Clears `city_id` when state changes
- `_post`: For credit notes (`out_refund`) generated from invoices, copies analytic distribution to lines that lack it

---

### `account.payment` — Account Payment (inherited)

| Field Name | Type | Label (string) | Description |
|---|---|---|---|
| `reonciliation_date` | Date (computed) | Bank Reconciliation Date | Maximum date among reconciled bank statement lines |
| `x_studio_tarimas` | Integer (related `move_id.x_studio_tarimas`) | Tarimas | Number of pallets from related journal entry |

**Key methods:**
- `_compute_reconciliation_date`: Computes the maximum date from reconciled bank statement lines
- `action_post`: Calls `check_invs` before posting payment
- `check_invs`: Raises `ValidationError` if the partner has any invoice with `stop_inv = True`

---

### `account.payment.line` — Account Payment Line (inherited)

| Field Name | Type | Label (string) | Description |
|---|---|---|---|
| *(no new fields)* | — | — | — |

**Key methods:**
- `move_line_id_change`: Raises `ValidationError` if the selected move line's invoice has `stop_inv = True`

---

### `account.payment.order` — Account Payment Order (inherited)

| Field Name | Type | Label (string) | Description |
|---|---|---|---|
| *(no new fields)* | — | — | — |

**Key methods:**
- `_prepare_move`: Sets `ref` to `bank_lines.communication` when exactly one bank line exists

---

### `account.aged.partner.balance.report.handler` — Account Aged Partner Balance (inherited, abstract)

| Field Name | Type | Label (string) | Description |
|---|---|---|---|
| *(no new fields)* | — | — | — |

**Key methods:**
- `_get_sql`: Modifies the aged balance SQL to append the move reference in parentheses after the move name (e.g., `INV/2024/0001 (REF123)`)

---

### `crm.lead` — CRM Lead (inherited)

| Field Name | Type | Label (string) | Description |
|---|---|---|---|
| `current_user_can_win_opportunities` | Boolean (computed) | — | True if current user belongs to `res_groups_allow_win_opportunities` |

**Key methods:**
- `_compute_can_win_opportunities`: Checks group membership for winning opportunities
- `write`: Enforces stage progression rules: cannot go back to previous stages; cannot change stage of won opportunity; cannot mark as won without proper group membership; users in `res_groups_can_change_lead_stages` are exempt

---

### `hr.expense` — HR Expense (inherited)

| Field Name | Type | Label (string) | Description |
|---|---|---|---|
| `payment_mode` | Selection | Payment Mode | Defaults to `petty_account` |
| `analytic_distribution` | Json | Analytic Distribution | Required analytic distribution for expenses |

**Key methods:**
- `_compute_is_editable`: Extends editability logic to allow account managers to edit expenses in `approve` state
- `force_approved`: For non-company-account expenses, sets all three approval flags and assigns global partner from system parameter; posts a chatter message

---

### `l10n_mx_edi.advance` — MX EDI Advance (inherited)

| Field Name | Type | Label (string) | Description |
|---|---|---|---|
| `x_studio_notas` | Char | Notas | Free-text notes on advance payment |

---

### `mrp.bom` — MRP Bill of Materials (inherited)

| Field Name | Type | Label (string) | Description |
|---|---|---|---|
| `x_studio_formula` | Char | Fórmula | Formula reference for the BOM |

---

### `mrp.dump.truck.driver` — Dump Truck Driver

| Field Name | Type | Label (string) | Description |
|---|---|---|---|
| `name` | Char | Name | Driver's name (required) |
| `active` | Boolean | Active | Whether the driver is active (default: True) |

---

### `mrp.equipment` — Equipment

| Field Name | Type | Label (string) | Description |
|---|---|---|---|
| `name` | Char | Name | Equipment name (required) |

---

### `mrp.license.plate` — License Plate

| Field Name | Type | Label (string) | Description |
|---|---|---|---|
| `name` | Char | Name | License plate identifier (required) |
| `active` | Boolean | Active | Whether the plate is active (default: True) |

---

### `mrp.production` — Manufacturing Order (inherited)

| Field Name | Type | Label (string) | Description |
|---|---|---|---|
| `equipment_id` | Many2one (`mrp.equipment`) | Equipment | Equipment used in production |
| `date_planned_start` | Datetime | Scheduled Date Start | Planned start date (copyable) |
| `hide_dump_info` | Boolean | — | Controls visibility of driver/plate fields (default: True) |
| `driver` | Many2one (`mrp.dump.truck.driver`) | Driver | Dump truck driver assigned |
| `plate` | Many2one (`mrp.license.plate`) | Plate | License plate of assigned vehicle |
| `qty_of_block` | Boolean | — | Flag to bypass overflow confirmation once set |
| `x_studio_frmula` | Char (related `bom_id.x_studio_formula`) | Fórmula | Formula from the BOM |

**Key methods:**
- `action_confirm`: Propagates `equipment_id` to all related stock move lines upon confirmation
- `action_cancel`: Restricted to users in `res_groups_can_see_button_action_cancel_in_mrp_production`
- `_onchange_product_id`: Shows/hides dump info fields based on `driver_commission` flag on product
- `pre_button_mark_done`: If quantity difference exceeds ±10 and `qty_of_block` is False, opens overflow confirmation wizard

---

### `mrp.request` — Manufacturing Request (inherited)

| Field Name | Type | Label (string) | Description |
|---|---|---|---|
| `available_qty` | Float (computed) | Available Qty | Sum of quantities in locations 8 (Stock), 19 (Quality), 11 (Preparación) |
| `product_max_qty` | Float (computed) | Max Qty | Maximum reorder quantity from orderpoint at location 8 |
| `product_min_qty` | Float (computed) | Min Qty | Minimum reorder quantity from orderpoint |
| `qty_multiple` | Float (computed) | Qty Multiple | Order quantity multiple from orderpoint |
| `qty_ordered` | Float (computed) | Qty Ordered | Sum of pending outgoing moves to customer/sample/installation/complaint locations |
| `qty_in_production` | Float (computed) | Qty in Production | Pending moves from Production (15) to Quality (19) |
| `local` | Float (computed) | Local | Pending moves for local clients from Preparación/Muestras |
| `foreigner` | Float (computed) | Foreign | Pending moves for foreign clients from Preparación/Muestras |
| `qty_to_max` | Float (computed) | Pending Max Inv | `product_max_qty - (available_qty + qty_in_production)` |
| `forecasted_qty` | Float (computed) | Forecasted Qty | `available_qty + qty_in_production - pending_sample_moves` |
| `parent_category_id` | Many2one (related) | Parent Category | Parent category of the requested product |

**Key methods:**
- `_compute_available_qty`: Searches stock quants in hardcoded location IDs 8, 19, 11
- `_compute_orderpoint`: Looks up reorder rules for location 8
- `_compute_qty_ordered`: Sums pending moves to locations 5, 24, 38, 39
- `_compute_qty_in_production`: Sums pending moves from 15 to 19
- `_compute_qty_to_max`: Computes gap to maximum inventory
- `_compute_forecasted_qty`: Net forecast considering in-progress sample moves
- `_compute_local`: Pending moves for local or unclassified clients
- `_compute_foreigner`: Pending moves for foreign clients

---

### `product.category` — Product Category (inherited)

| Field Name | Type | Label (string) | Description |
|---|---|---|---|
| `is_mp_category` | Boolean | Is MP Category | Flags category as raw material (restricts purchase access) |
| `category_class_id` | Many2one (`product.category.class`) | Category Class | Class grouping for cost/reporting purposes |
| `ebitda_report` | Boolean | EBITDA Report | Whether this category is included in EBITDA reporting |
| `x_studio_porcentaje` | Float | Porcentaje | Percentage value for the category |

---

### `product.category.class` — Product Category Class

| Field Name | Type | Label (string) | Description |
|---|---|---|---|
| `name` | Char | Name | Class name (required) |
| `cpt` | Float | CPT | Cost per ton value (required, default 0.0) |

---

### `product.product` — Product Variant (inherited)

| Field Name | Type | Label (string) | Description |
|---|---|---|---|
| `freight_weight` | Float | Freight Weight | Weight used for freight cost calculation |
| `tons_display` | Float (computed) | Tons | Available quantity × weight / 1000 |
| `driver_commission` | Boolean | Driver Commission | Whether this product triggers driver/plate fields on MO |
| `parent_category_id` | Many2one (related `categ_id.parent_id`) | Parent Category | Parent category of the product |
| `liters_display` | Float (computed) | Litros | `qty_available × weight` (liters equivalent) |

**Key methods:**
- `_compute_liters`: Computes `qty_available * weight`
- `_compute_tons`: Computes `qty_available * weight / 1000`

---

### `purchase.order` — Purchase Order (inherited)

| Field Name | Type | Label (string) | Description |
|---|---|---|---|
| `currency_copy` | Char (computed) | Currency (Copy) | Name of the selected currency |

**Key methods:**
- `_compute_currency_copy`: Returns `currency_id.name` on currency change
- `_prepare_invoice`: Propagates `is_freight_supplier` flag to generated vendor bill
- `button_confirm`: Validates that all order lines have an analytic distribution before confirming

---

### `purchase.order.line` — Purchase Order Line (inherited)

| Field Name | Type | Label (string) | Description |
|---|---|---|---|
| `has_restriction` | Boolean (computed) | Has Restriction | True if product's category is flagged as MP category |

**Key methods:**
- `_compute_has_restriction`: Checks if product category is in MP categories
- `_get_restrict_product_categories`: Returns all categories with `is_mp_category = True`
- `_onchange_product_id`: Raises `ValidationError` if user lacks `res_groups_can_add_mp_products` and product has MP restriction

---

### `res.partner` — Contact (inherited)

| Field Name | Type | Label (string) | Description |
|---|---|---|---|
| `freight_cost` | Float | Freight Cost | Cost of freight (precision: Freight Factor) |
| `loads` | Boolean | Loads | Indicates partner handles loads |
| `prompt_payment` | Boolean | Prompt Payment | Partner pays promptly |
| `review_day` | Selection | Review Day | Day of week for account reviews |
| `paydays` | Selection | Paydays | Day of week for payments |
| `full_record` | Boolean | Full Record | Partner has complete record |
| `pamphletes` | Boolean | Pamphletes | Partner receives brochures |
| `samples` | Boolean | Samples | Partner receives samples |
| `pricers` | Boolean | Pricers | Partner receives price lists |
| `child_tag_ids` | Many2many (computed) | Contacts | Delivery contacts linked via tag group logic |
| `commercial_name` | Char | Commercial Name | Commercial/trade name |
| `sales_phone` | Char | Sales Phone | Phone for sales contact |
| `commercial_address` | Char | Commercial Address | Commercial address |
| `x_studio_boolean_field_5iE6W` | Boolean | Critico | Marks partner as critical |
| `x_studio_fecha_alta_de_cliente` | Date | Fecha Alta de Cliente | Client registration date |
| `x_studio_departamento` | Selection | Departamento | Department classification |
| `x_studio_extras` | Selection | Extras | Extra services (Maniobras, Reparto, etc.) |
| `x_studio_zona` | Selection | Zona | Delivery zone (0–9) |
| `way_of_shipment_id` | Many2one (`res.partner`) | Way of Shipment | Default freight supplier for this partner |
| `way_shipment_type_id` | Many2one (`way.of.shipment.type`) | Way Shipment Type | Shipment type |
| `visit_frequency` | Integer | Visit Frequency | How often the partner is visited |
| `contact_is_customer` | Boolean | Is customer? | Sets/unsets customer rank |
| `contact_is_supplier` | Boolean | Is supplier? | Sets/unsets supplier rank |
| `prompt_payment_days` | Integer | Prompt Payment Days | Days for prompt payment |
| `special_info` | Text | Special Info | Special delivery instructions |
| `total_due` | Monetary | Total Due | Restricted to accounting/seller groups |
| `total_overdue` | Monetary | Total Overdue | Restricted to accounting/seller groups |
| `followup_status` | Selection | Followup Status | Restricted to accounting/seller groups |
| `followup_line_id` | Many2one | Followup Level | Restricted to accounting/seller groups |
| `followup_responsible_id` | Many2one | Followup Responsible | Restricted to accounting/seller groups |

**Key methods:**
- `_onchange_company_type`: Sets `type = 'delivery'` for persons, `type = 'contact'` for companies
- `_compute_childs_type_delivery`: Computes delivery contacts linked by tag group membership
- `_update_childs_parents`: Updates child_tag_ids for parent company partners
- `_onchange_contact_is_customer`: Increases or resets customer rank
- `_onchange_contact_is_supplier`: Increases or resets supplier rank
- `_reset_rank`: Directly resets rank field to 0 using SQL with NOWAIT lock
- `_get_risk_sale_order_domain`: Extends financial risk domain to include `invoice_status = 'no'`

---

### `res.users` — Users (inherited)

| Field Name | Type | Label (string) | Description |
|---|---|---|---|
| `force_share` | Boolean | Force Share | Forces portal/share behavior even for internal users |
| `default_analytic_account_id` | Many2one (`account.analytic.account`) | Default Analytic Account | Default analytic account assigned to user's sales orders |

**Key methods:**
- `_compute_share`: Overrides share computation; internal users or those with `force_share = True` are set as non-shared

---

### `sale.order` — Sale Order (inherited)

| Field Name | Type | Label (string) | Description |
|---|---|---|---|
| `commitment_date_real` | Datetime | Commitment Date | Custom commitment date replacing native field |
| `po_name` | Text | PO Name | Customer purchase order name/reference |
| `comment_marketing` | Text | Marketing Comment | Marketing submission notes |
| `can_modify_invoice` | Boolean (computed) | — | Whether current user can modify invoice address |
| `can_modify_quotation_date` | Boolean (computed) | — | Whether user can modify quotation date |
| `can_modify_pricelist` | Boolean (computed) | — | Whether user can modify pricelist |
| `child_tag_ids` | Many2many (related) | Contacts | Delivery contacts from partner |
| `analytic_account_id` | Many2one | Analytic Account | Required; copied on duplicate |
| `order_signal` | Selection | Order Signal | `on_time`, `due_soon`, or `overdue` based on dates |
| `out_pending` | Selection | Out Pending | `available` or `not available` for outgoing stock |
| `x_studio_ciudad_de_entrega` | Char (related) | Ciudad de entrega | Shipping city |
| `x_studio_zona` | Selection (related) | Zona | Delivery zone from shipping partner |
| `x_studio_text_field_v3Z0L` | Text | Celular fletero | Freight driver phone number |
| `x_studio_estatus_embarques` | Selection | Estatus embarque | Shipment status (6 stages) |
| `x_studio_indicaciones_especiales` | Text (related) | Indicaciones especiales | Special instructions from shipping partner |
| `x_studio_related_field_zMLGz` | Char (related) | Ciudad Entrega | Shipping city (duplicate) |
| `x_studio_zona_1` | Selection (related) | Zona 1 | Zone from shipping partner (duplicate) |
| `x_studio_special_info_client` | Text (related) | Special info | Special info from shipping partner |
| `way_of_shipment_id` | Many2one (`res.partner`) | Way of Shipment | Freight supplier; propagates to pickings |
| `way_shipment_type_id` | Many2one (related) | Way Shipment Type | Shipment type from partner |
| `total_volume` | Float (computed) | Total Volume | Total volume of all order lines |
| `state` | Selection | Status | Adds `check` (Inquiry) state before `draft` |

**Key methods:**
- `confirm_quote`: Transitions state from `check` to `draft`
- `_prepare_invoice`: Passes `way_of_shipment_id` to generated invoice
- `_compute_pricelist_id`: Only computes pricelist in `draft` state; uses shipping partner's pricelist
- `_real_onchange_partner_id`: Clears shipping partner and sets analytic account from user's default
- `_onchange_partner_shipping_id`: Auto-fills pricelist, way of shipment, user, and analytic account
- `_check_prices_of_pricelist`: Triggers price update when pricelist or shipping partner changes
- `create`: Validates user permissions; runs order validations after creation
- `write`: Enforces edit restrictions after creation; blocks seller role from modifying non-allowed fields; propagates `way_of_shipment_id` to pickings
- `validate_partner_shipping_id_pricelist`: Ensures pricelist matches shipping partner unless user has override group
- `validate_no_empty_order`: Raises error if order has no lines

---

### `stock.lot` (`stock.production.lot`) — Production Lot (inherited)

| Field Name | Type | Label (string) | Description |
|---|---|---|---|
| *(no new fields)* | — | — | — |

**Key methods:**
- `create` / `write`: Calls `validate_lot_name` after creation/update
- `validate_lot_name`: Validates lot name against regex patterns for `PT POLVOS` and `PT PINTURAS Y PASTAS` categories; validates embedded date is within last 10 days

---

### `stock.move` — Stock Move (inherited)

| Field Name | Type | Label (string) | Description |
|---|---|---|---|
| `equipment_id` | Many2one (`mrp.equipment`) | Equipment | Equipment from MO (read-only) |
| `parent_category_id` | Many2one (related) | Parent Category | Parent category of product |
| `sale_order_id` | Many2one (related `picking_id.sale_id`) | Sale Order | Related sale order |
| `product_category_id` | Many2one (related `product_id.categ_id`) | Product Category | Product's category |
| `way_of_shipment_id` | Many2one (related `picking_id.way_of_shipment_id`) | Way of Shipment | Shipment method from picking |
| `way_of_shipment_type_id` | Many2one (related) | Way of Shipment Type | Shipment type |
| `picking_note` | Html (related `picking_id.note`) | Picking Notes | Notes from the picking |
| `salesman_id` | Many2one (related) | Salesman | Salesperson from sale order |

**Key methods:**
- `_get_new_picking_values`: Propagates `way_of_shipment_id` from sale order or stock request to new picking
- `_compute_should_consume_qty`: Adjusts consumed quantity when MO produces more than planned
- `_set_quantity_done_prepare_vals`: Aligns done quantity to remaining production quantity
- `action_view_picking`: Opens picking form from move
- `action_view_sale`: Opens sale order form from move
- `create`: Posts chatter message on picking listing new products added
- `write`: Posts chatter message on picking when quantities change
- `unlink`: Posts chatter message on picking when lines are deleted

### `stock.move.line` — Stock Move Line (inherited)

| Field Name | Type | Label (string) | Description |
|---|---|---|---|
| `equipment_id` | Many2one (related `move_id.equipment_id`) | Equipment | Equipment from parent move |
| `parent_category_id` | Many2one (related) | Parent Category | Parent category of product |

---

### `stock.picking` — Stock Picking (inherited)

| Field Name | Type | Label (string) | Description |
|---|---|---|---|
| `way_of_shipment_id` | Many2one (`res.partner`) | Way of Shipment | Freight supplier for this transfer |
| `salesman_id` | Many2one (related `sale_id.user_id`) | Salesman | Salesperson from sale order |
| `way_shipment_type_id` | Many2one (related) | Way Shipment Type | Shipment type from partner |
| `hide_picking_block` | Boolean (computed) | — | Whether picking block UI is hidden |
| `machine_id` | Many2one (`mrp.equipment`) | Machine | Equipment linked via origin MO |
| `x_studio_char_field_Rxj40` | Char | New Texto | Free text field |
| `x_studio_many2one_field_aAHDt` | Many2one (`stock.request`) | Solicitud de existencias | Linked stock request |
| `x_studio_related_field_46xN8` | Many2one (related) | New Campo relacionado | Related stock request |

**Key methods:**
- `_compute_machine_name`: Looks up equipment from MO matching `origin`
- `create`: Automatically sets priority to `1` (urgent) for local pickings from main stock location when `real.block_inventory_priority = True`
- `_compute_hide_picking_block`: Checks `res_groups_hide_picking_block` group membership
- `location_check`: Validates that each move line's source/destination locations are consistent with the picking's locations
- `button_validate`: Runs `location_check` before validating
- `_compute_scheduled_date`: Sets scheduled date equal to sale order date for pickings linked to sales

---

### `stock.quant` — Stock Quant (inherited)

| Field Name | Type | Label (string) | Description |
|---|---|---|---|
| `parent_category_id` | Many2one (related) | Parent Category | Parent category of product |
| `tons_display` | Float (computed) | Tons | `quantity × product weight / 1000` |

**Key methods:**
- `_compute_tons`: Calculates tons from quantity and product weight

---

### `stock.request.order` — Stock Request Order (inherited)

| Field Name | Type | Label (string) | Description |
|---|---|---|---|
| `way_of_shipment_id` | Many2one (`res.partner`) | Way of Shipment | Freight supplier for the request |
| `way_shipment_type_id` | Many2one (related) | Way Shipment Type
<!-- odoo-docs: last-commit=bc3aed09b867c535fa821b5cc7f6af1e62e0cb44 | updated=2026-05-19 -->
