# real_reports — Real Reports

> **Version:** 17.0.1.0.11 | **License:** LGPL-3 | **Author:** Jarsa

<!-- ============================================================ -->
<!-- ENGLISH SECTION — Technical Reference                        -->
<!-- ============================================================ -->

## Overview

`real_reports` is a custom Odoo 17 reporting module built for the "Real" company. It provides a comprehensive suite of business intelligence reports covering sales invoicing, bank movements, production (MRP), inventory, collections, costs and prices, landed costs, general ledger auditing, cancelled invoices, and more. The module defines its own PostgreSQL-backed reporting models (many using `_auto = False` database views) and extends native Odoo models including `account.move`, `stock.quant`, `mrp.production`, `stock.landed.cost`, and `account.move.line`. All reports are exposed through dedicated menu items grouped under Sales Reports, Accounting Reports, Production Reports, Inventory Reports, and Purchase Reports sections.

## Dependencies

### Odoo / OCA Modules

- `sale_stock` — Required for sales order and stock move data used in sales and inventory reports
- `l10n_mx_edi` — Required for Mexican EDI payment method fields (`l10n_mx_edi_payment_method_id`) used in bank and invoice reports
- `report_account_invoice_real` — Base invoice reporting module that this module extends
- `real` — Core customization module for the Real company providing base models and configurations
- `mrp_request` — Manufacturing request module whose data is consumed in MRP reports
- `real_products_available_on_request` — Products available on request module used in inventory/quant reports
- `account_move_reversal` — Required for credit note and cancellation data used in credit and cancelled invoice reports

### Python Libraries

- `xlsxwriter` — Used in `general_ledger_audit.py` for Excel report generation
- `io` — Used for in-memory byte streams when generating Excel output

## Installation

1. Place the module in your addons path.
2. Update the module list: **Settings → Activate Developer Mode → Update Apps List**
3. Search for `real_reports` and click **Install**.
4. Ensure all dependent modules (`real`, `mrp_request`, `real_products_available_on_request`, `report_account_invoice_real`) are already installed before installing this module.

## Models Reference

### `sale.invoice.report.real` — Sale Invoice Report Real

| Field Name | Type | Label (string) | Description |
|---|---|---|---|
| id | Integer | ID | Record identifier |
| name | Char | Name | Invoice/document name or number |
| description | Char | Description | Line description or product name |
| invoice_date | Date | Invoice Date | Date of the invoice |
| invoice_date_due | Date | Due Date | Payment due date |
| partner_id | Many2one (res.partner) | Partner | Customer linked to the invoice |
| invoice_user_id | Many2one (res.users) | Salesperson | Salesperson assigned to the invoice |
| move_type | Selection | Type | Move type (out_invoice, out_refund, etc.) |
| total | Float | Total | Total invoice amount |
| tons_display | Float | Tons | Quantity in tons |
| tons_litres | Float | Liters | Quantity in liters |
| total_sale_no_freight_with_tax | Float | Sale without Freight (with tax) | Sale amount excluding freight, including tax |
| freight_total_with_tax | Float | Freight Total (with tax) | Freight amount including tax |
| parent_category_id | Many2one (product.category) | Parent Category | Parent product category |
| rectified_invoices | Char | Credit Note Type | Type/description of rectified invoice |

**Key methods:**
- `init`: Creates or replaces the `sale_invoice_report_real` SQL view joining `account_move`, `account_move_line`, `product_template`, `product_category`, and related tables

---

### `account.invoice.report.real` — Account Invoice Report Real

| Field Name | Type | Label (string) | Description |
|---|---|---|---|
| id | Integer | ID | Record identifier |
| date | Date | Date | Accounting entry date |
| account_name | Char | Account | Account name |
| partner_id | Many2one (res.partner) | Partner | Partner linked to the entry |
| description | Char | Description | Entry description/label |
| reference | Char | Reference | Entry reference |
| amount | Float | Amount | Entry amount |
| currency_id | Many2one (res.currency) | Currency | Currency of the entry |
| l10n_mx_edi_payment_method_id | Many2one (l10n_mx_edi.payment.method) | Payment Method | Mexican EDI payment method |

**Key methods:**
- `init`: Creates or replaces the `account_invoice_report_real` SQL view from `account_move`, `account_move_line`, and `account_account`

---

### `account.bank.report.real` — Account Bank Report Real

| Field Name | Type | Label (string) | Description |
|---|---|---|---|
| id | Integer | ID | Record identifier |
| date | Date | Date | Payment/journal entry date |
| account_name | Char | Account | Bank account name |
| supplier_type | Char | Supplier Type | Type of supplier |
| partner_id | Many2one (res.partner) | Partner | Vendor or customer partner |
| l10n_edi_employee_id | Many2one (hr.employee) | Employee | Employee linked to the expense |
| description | Char | Description | Payment description |
| reference | Char | Reference | Payment reference |
| check_number | Char | Check Number | Check number if applicable |
| amount | Float | Amount | Payment amount |
| currency_id | Many2one (res.currency) | Currency | Currency |
| l10n_mx_edi_payment_method_id | Many2one (l10n_mx_edi.payment.method) | Payment Method | Mexican EDI payment method |
| state | Selection | State | Payment state |

**Key methods:**
- `init`: Creates or replaces the `account_bank_report_real` SQL view from `account_payment` and related tables

---

### `quant.report.real` — Quant Report Real

| Field Name | Type | Label (string) | Description |
|---|---|---|---|
| id | Integer | ID | Record identifier |
| product_id | Many2one (product.product) | Product | Product variant |
| product_name | Char | Product Name | Product display name |
| quantity | Float | Quantity | Stock quantity on hand |
| commited_qty | Float | Committed Qty | Quantity committed in sales orders |
| available | Float | Available | Available quantity (on hand minus committed) |
| tons | Float | Tons | Quantity expressed in tons |
| qty_in_production | Float | Qty in Production | Quantity currently in production |
| category_id | Many2one (product.category) | Category | Product category |
| parent_category_id | Many2one (product.category) | Parent Category | Parent product category |
| location_id | Many2one (stock.location) | Location | Storage location |

**Key methods:**
- `init`: Creates or replaces the `quant_report_real` SQL view aggregating `stock_quant`, `product_product`, `product_template`, `product_category`, and `sale_order_line`

---

### `mrp.report.real` — MRP Report Real

| Field Name | Type | Label (string) | Description |
|---|---|---|---|
| id | Integer | ID | Record identifier |
| product_id | Many2one (product.product) | Product | Finished product being manufactured |
| equipment_name | Char | Equipment | Name of the manufacturing equipment/work center |
| product_uom_qty | Float | Planned Qty | Planned production quantity |
| qty_producing | Float | Qty Producing | Actual produced quantity |
| waste | Float | Waste | Waste quantity |
| tons | Float | Tons | Production quantity in tons |
| date_finished | Datetime | Date Finished | Date production order was finished |
| parent_category_id | Many2one (product.category) | Parent Category | Parent product category |

**Key methods:**
- `init`: Creates or replaces the `mrp_report_real` SQL view from `mrp_production`, `product_product`, `product_template`, `product_category`

---

### `credit.report.real` — Credit Report Real

| Field Name | Type | Label (string) | Description |
|---|---|---|---|
| id | Integer | ID | Record identifier |
| name | Char | Name | Credit note number |
| rectified_invoices | Char | Rectified Invoices | Reference to the original invoice rectified |
| partner_id | Many2one (res.partner) | Customer | Customer partner |
| invoice_date | Date | Invoice Date | Date of the credit note |
| credit_note_date | Date | Credit Note Date | Date of the credit note (used for filtering) |
| payment_date | Date | Payment Date | Payment date |
| days_invoice | Integer | Days | Days difference between invoice and payment |
| total | Float | Total | Credit note total amount |

**Key methods:**
- `init`: Creates or replaces the `credit_report_real` SQL view from `account_move` filtered to `out_refund` type

---

### `collection.report.real` — Collection Report Real

| Field Name | Type | Label (string) | Description |
|---|---|---|---|
| id | Integer | ID | Record identifier |
| invoice_name | Char | Invoice | Invoice number |
| invoice_user_id | Many2one (res.users) | Salesperson | Salesperson responsible for the invoice |
| payment_date | Date | Payment Date | Date payment was received |
| max_date | Date | Max Date | Maximum date used for filtering ranges |
| partner_id | Many2one (res.partner) | Customer | Customer partner |
| days_invoice | Integer | Days | Days since invoice was issued |
| total | Float | Total | Total amount of the invoice |
| total_0_60 | Float | Total 0 - 60 | Amount collected within 0–60 days |
| total_more_60 | Float | Total 61 + | Amount collected after 60 days |
| currency_id | Many2one (res.currency) | Currency | Currency |

**Key methods:**
- `init`: Creates or replaces the `collection_report_real` SQL view joining `account_move` payments and invoice lines

---

### `production.consumption.report.real` — Production Consumption Report Real

| Field Name | Type | Label (string) | Description |
|---|---|---|---|
| id | Integer | ID | Record identifier |
| product_id | Many2one (product.product) | Product | Raw material product consumed |
| equipment_id | Many2one (maintenance.equipment) | Equipment | Equipment where consumption occurred |
| product_uom_qty | Float | Consumed Qty | Quantity of material consumed |
| date | Date | Date | Consumption date |

**Key methods:**
- `init`: Creates or replaces the `production_consumption_report_real` SQL view from `mrp_production` and `stock_move`

---

### `kardex.report.real` — Kardex Report Real

| Field Name | Type | Label (string) | Description |
|---|---|---|---|
| id | Integer | ID | Record identifier |
| date | Date | Date | Movement date |
| accounting_date | Date | Accounting Date | Accounting date of the move |
| product_id | Many2one (product.product) | Product | Product involved in the movement |
| name | Char | Concept | Movement concept/description |
| origin | Char | Origin | Origin document reference |
| reference | Char | Reference | Additional reference |
| category_id | Many2one (product.category) | Category | Product category |
| parent_category_id | Many2one (product.category) | Parent Category | Parent product category |
| incoming | Float | Incoming | Incoming stock quantity |
| outgoing | Float | Outgoing | Outgoing stock quantity |
| account_move_id | Many2one (account.move) | Account Move | Linked accounting entry |
| stock_move_id | Many2one (stock.move) | Stock Move | Linked stock movement |

**Key methods:**
- `init`: Creates or replaces the `kardex_report_real` SQL view from `stock_move` and related tables

---

### `stock.landed.cost.report.real` — Stock Landed Cost Report Real

| Field Name | Type | Label (string) | Description |
|---|---|---|---|
| id | Integer | ID | Record identifier |
| date | Date | Date | Date of landed cost application |
| product_id | Many2one (product.product) | Product | Raw material product affected |
| expense_product_id | Many2one (product.product) | Expense Product | Product used as expense/freight concept |
| quantity | Float | Quantity | Quantity of product |
| former_unit_cost | Float | Former Unit Cost | Unit cost before landed cost application |
| unit_additional_landed_cost | Float | Unit Additional Landed Cost | Additional cost per unit from landed cost |
| category_id | Many2one (product.category) | Category | Product category |
| parent_category_id | Many2one (product.category) | Parent Category | Parent product category |

**Key methods:**
- `init`: Creates or replaces the `stock_landed_cost_report_real` SQL view from `stock_landed_cost`, `stock_valuation_adjustment_lines`, and related tables

---

### `expense.report.real` — Expense Report Real

| Field Name | Type | Label (string) | Description |
|---|---|---|---|
| id | Integer | ID | Record identifier |
| journal_id | Many2one (account.journal) | Journal | Accounting journal |
| date | Date | Date | Entry date |
| account_id | Many2one (account.account) | Account | Accounting account |
| name | Char | Name | Entry label/name |
| ref | Char | Reference | Entry reference |
| debit | Float | Debit | Debit amount |
| credit | Float | Credit | Credit amount |
| balance | Float | Balance | Net balance (debit minus credit) |

**Key methods:**
- `init`: Creates or replaces the `expense_report_real` SQL view from `account_move_line` and `account_journal`

---

### `report.kardex.report.wiz` — Kardex Report Wizard

| Field Name | Type | Label (string) | Description |
|---|---|---|---|
| id | Integer | ID | Record identifier |
| date_start | Date | Start Date | Start date for kardex filtering |
| date_end | Date | End Date | End date for kardex filtering |
| product_ids | Many2many (product.product) | Products | Products to include in the kardex |
| category_ids | Many2many (product.category) | Categories | Product categories to filter |

**Key methods:**
- `action_print_report`: Generates and returns the Kardex PDF report filtered by date range and selected products/categories

---

### `expense.report.real.wiz` — Expense Report Wizard

| Field Name | Type | Label (string) | Description |
|---|---|---|---|
| id | Integer | ID | Record identifier |
| date_start | Date | Start Date | Start date for expense filtering |
| date_end | Date | End Date | End date for expense filtering |
| journal_ids | Many2many (account.journal) | Journals | Journals to include in the report |

**Key methods:**
- `action_print_report`: Filters `expense.report.real` records by date and journal, then triggers PDF or pivot report

---

### `wizard.report.mrp.request` — Wizard Report MRP Request

| Field Name | Type | Label (string) | Description |
|---|---|---|---|
| id | Integer | ID | Record identifier |
| date_start | Date | Start Date | Start date for MRP request report |
| date_end | Date | End Date | End date for MRP request report |
| workcenter_ids | Many2many (mrp.workcenter) | Work Centers | Work centers to include in report |

**Key methods:**
- `action_print_report`: Generates PDF report for MRP requests filtered by date and work center

---

### `account.fcr.report` — Account FCR Report

| Field Name | Type | Label (string) | Description |
|---|---|---|---|
| id | Integer | ID | Record identifier |
| rep_select | Selection | Report | Selection of FCR report type to generate |
| date_start | Date | Start Date | Start date of the report period |
| date_end | Date | End Date | End date of the report period |

**Key methods:**
- `action_print_report`: Executes SQL queries against analytic accounts and journal entries, then renders the FCR QWeb PDF template with grouped cost center data

---

### `freight.line.report` — Freight Line Report

| Field Name | Type | Label (string) | Description |
|---|---|---|---|
| id | Integer | ID | Record identifier |
| date_start | Date | Start Date | Start date for freight line calculation |
| date_end | Date | End Date | End date for freight line calculation |

**Key methods:**
- `action_print_report`: Queries invoice lines for freight-included-in-price products grouped by product name and renders the PDF template

---

### `costs.and.prices.report` — Costs and Prices Report

| Field Name | Type | Label (string) | Description |
|---|---|---|---|
| id | Integer | ID | Record identifier |
| date_start | Date | Start Date | Start date for cost/price calculation period |
| date_end | Date | End Date | End date for cost/price calculation period |

**Key methods:**
- `action_print_report`: Executes multi-table SQL queries combining production orders, invoices, and stock valuations to compute costs, sales, freight, quantities, and margin percentages by product line; renders PDF

---

### `general.ledger.audit` — General Ledger Audit

| Field Name | Type | Label (string) | Description |
|---|---|---|---|
| id | Integer | ID | Record identifier |
| date_start | Date | Start Date (Desde) | Start date for general ledger audit period |
| date_end | Date | End Date (Hasta) | End date for general ledger audit period |

**Key methods:**
- `action_print_report`: Executes SQL query on `account_move_line` grouped by analytic distribution and account, renders QWeb PDF with debit/haber/balance columns grouped by division/department
- `action_print_excel`: Generates Excel (.xlsx) file using `xlsxwriter` with the same ledger audit data, returned as base64-encoded file download

---

### `report.real_reports.general_ledger_audit_template` — General Ledger Audit XLSX Template

| Field Name | Type | Label (string) | Description |
|---|---|---|---|
| id | Integer | ID | Internal record ID |

**Key methods:**
- `_get_report_values`: Provides the data dictionary (`query`, `div_dep`, `div_group`, `sum_total1`, `sum_total2`, `sum_total3`, `title`, `date_start`, `date_end`, `today`) consumed by the QWeb PDF template

---

### `report.cancelled.invoices` — Report Cancelled Invoices

| Field Name | Type | Label (string) | Description |
|---|---|---|---|
| id | Integer | ID | Record identifier |
| date_start | Date | Start Date | Start date for cancelled invoices search |
| date_end | Date | End Date | End date for cancelled invoices search |

**Key methods:**
- `action_print_report`: Queries `account_move` for invoices cancelled in a period different from the original invoice date, enriches with cost and tonnage data, renders PDF

---

### `physical.inventory.count` — Physical Inventory Count

| Field Name | Type | Label (string) | Description |
|---|---|---|---|
| id | Integer | ID | Record identifier |

**Key methods:**
- `action_print_report`: Queries current stock quantities for POLVOS and EMULSIONES categories, returns QWeb PDF formatted as a physical inventory count sheet (format L-044)

---

### `pending.tons.wizard` — Pending Tons Wizard

| Field Name | Type | Label (string) | Description |
|---|---|---|---|
| id | Integer | ID | Record identifier |
| datetime_input | Datetime | Date/Time Input | Reference datetime for pending tons calculation |
| result_tons | Float | Result Tons | Computed pending tons result (read-only) |

**Key methods:**
- `action_compute`: Calculates the total pending (undelivered) tons from confirmed sales orders as of the given datetime, storing the result in `result_tons`

---

### `report.stock.quant.real` — Report Stock Quant Real

| Field Name | Type | Label (string) | Description |
|---|---|---|---|
| id | Integer | ID | Record identifier |
| product_id | Many2one (product.product) | Product | Product variant |
| pending_qty_local | Float | Pending Qty Local | Pending quantity from local orders |
| pending_qty_foreign | Float | Pending Qty Foreign | Pending quantity from foreign orders |
| pending_total | Float | Pending Total | Total pending quantity |
| available_space | Float | Available Space | Available storage space |
| excess | Float | Excess | Excess quantity over available space |
| batch_number | Char | Batch Number | Oldest batch/lot number |

**Key methods:**
- `init`: Creates or replaces the `report_stock_quant_real` SQL view combining stock quants with pending sales order quantities

## Security Groups

All models grant full CRUD permissions (`perm_read=1, perm_write=1, perm_create=1, perm_unlink=1`) to `base.group_user` (all internal users). No model-level restrictions beyond this are defined.

| Model | Group | Read | Write | Create | Delete |
|---|---|---|---|---|---|
| sale.invoice.report.real | All Internal Users | ✓ | ✓ | ✓ | ✓ |
| account.invoice.report.real | All Internal Users | ✓ | ✓ | ✓ | ✓ |
| account.bank.report.real | All Internal Users | ✓ | ✓ | ✓ | ✓ |
| quant.report.real | All Internal Users | ✓ | ✓ | ✓ | ✓ |
| mrp.report.real | All Internal Users | ✓ | ✓ | ✓ | ✓ |
| credit.report.real | All Internal Users | ✓ | ✓ | ✓ | ✓ |
| collection.report.real | All Internal Users | ✓ | ✓ | ✓ | ✓ |
| production.consumption.report.real | All Internal Users | ✓ | ✓ | ✓ | ✓ |
| kardex.report.real | All Internal Users | ✓ | ✓ | ✓ | ✓ |
| report.kardex.report.wiz | All Internal Users | ✓ | ✓ | ✓ | ✓ |
| stock.landed.cost.report.real | All Internal Users | ✓ | ✓ | ✓ | ✓ |
| expense.report.real | All Internal Users | ✓ | ✓ | ✓ | ✓ |
| expense.report.real.wiz | All Internal Users | ✓ | ✓ | ✓ | ✓ |
| wizard.report.mrp.request | All Internal Users | ✓ | ✓ | ✓ | ✓ |
| report.stock.quant.real | All Internal Users | ✓ | ✓ | ✓ | ✓ |
| account.fcr.report | All Internal Users | ✓ | ✓ | ✓ | ✓ |
| freight.line.report | All Internal Users | ✓ | ✓ | ✓ | ✓ |
| costs.and.prices.report | All Internal Users | ✓ | ✓ | ✓ | ✓ |
| general.ledger.audit | All Internal Users | ✓ | ✓ | ✓ | ✓ |
| report.real_reports.general_ledger_audit_template | All Internal Users | ✓ | ✓ | ✓ | ✓ |
| report.cancelled.invoices | All Internal Users | ✓ | ✓ | ✓ | ✓ |
| physical.inventory.count | All Internal Users | ✓ | ✓ | ✓ | ✓ |
| pending.tons.wizard | All Internal Users | ✓ | ✓ | ✓ | ✓ |

## Menus & Actions

All top-level menus are children of `spreadsheet_dashboard.spreadsheet_dashboard_menu_root` (the main Dashboards/Reports menu root).

### Accounting Reports

| Menu Path | Action |
|---|---|
| Accounting Reports > Bank Check Report | Lists bank receipts filtered by check payment method |
| Accounting Reports > Bank Electronic Transfer Report | Lists bank receipts filtered by electronic transfer |
| Accounting Reports > Bank Cash Report | Lists bank receipts filtered by cash payment |
| Accounting Reports > Bank Other Report | Lists bank receipts filtered by other payment methods |
| Accounting Reports > Bank Expense Report | Lists bank expense movements (tree + pivot) |
| Accounting Reports > Invoice/Credit Note Report | Lists credit notes grouped by type |
| Accounting Reports > Collection by Salesman | Collections grouped by salesperson |
| Accounting Reports > Reportes FCR | Form to generate FCR cost center reports (PDF) |
| Accounting Reports > general ledger audit | Form to generate General Ledger Audit (PDF/Excel) |

### Sale Reports

| Menu Path | Action |
|---|---|
| Sale Reports > Liters sold by seller | Pivot of emulsion liters sold by salesperson |
| Sale Reports > Tons sold by seller | Pivot of powder tons sold by salesperson |
| Sale Reports > Sales Traveling Leaf | Pivot of sales by parent product category |
| Sale Reports > Credit Note Traveling Leaf | Tree list of credit notes grouped by type |
| Sale Reports > Maniobras Incluidas en Precio | Form to generate freight-included-in-price PDF report |
| Sale Reports > Cancelled Invoices Report | Form to generate cancelled invoices PDF report |
| Sale Reports > Pending Tons Report | Wizard to compute pending (undelivered) tons |

### Production Reports

| Menu Path | Action |
|---|---|
| Production Reports > Production Emulsiones | Pivot of emulsion production analysis (previous day) |
| Production Reports > Production Polvos | Pivot of powder production analysis (previous day) |
| Production Reports > Costos y Precios por Lineas | Form to generate costs and prices PDF report |
| Production Reports > Consumption of loads | Pivot of raw material consumption per production |
| Production Reports > Consumption of loads by equipment | Pivot of raw material consumption grouped by equipment |

### Inventory Reports

| Menu Path | Action |
|---|---|
| Inventory Reports > Inventory Analysis | Tree + pivot of current stock quantities, tons, and committed quantities |

### Purchase Reports

| Menu Path | Action |
|---|---|
| Purchase Reports > Raw Material Freight | Tree + pivot of landed costs applied to raw materials |

## Reports

| Report Name | Model | Type | Trigger |
|---|---|---|---|
| Bank Expenses Report | account.bank.report.real | QWeb PDF | Print button on list/from binding |
| Credit Note Report | credit.report.real | QWeb PDF | Print button on list/from binding |
| Reportes FCR | account.fcr.report | QWeb PDF | `action_print_report` button in form |
| Libro Mayor Audit (PDF) | general.ledger.audit | QWeb PDF | `action_print_report` button in form |
| Libro Mayor Audit (Excel) | general.ledger.audit | XLSX | `action_print_excel` button in form |
| Costos y Precios por Lineas | costs.and.prices.report | QWeb PDF | `action_print_report` button in form |
| Maniobras Incluidas en Precio | freight.line.report | QWeb PDF | `action_print_report` button in form |
| Cancelled Invoices Report | report.cancelled.invoices | QWeb PDF | `action_print_report` button in form |
| Physical Inventory Count | physical.inventory.count | QWeb PDF | `action_print_report` button / binding |
| Kardex Report | kardex.report.real (via wizard) | QWeb PDF | `action_print_report` in wizard |
| Expense Report | expense.report.real (via wizard) | QWeb PDF / Pivot | `action_print_report` in wizard |
| MRP Request Report | wizard.report.mrp.request | QWeb PDF | `action_print_report` in wizard |

---

<!-- ============================================================ -->
<!-- SECCIÓN EN ESPAÑOL — Documentación Funcional                 -->
<!-- ============================================================ -->

## Descripción General

El módulo `real_reports` es un paquete de reportes empresariales desarrollado a medida para la empresa Real. Su propósito principal es centralizar en Odoo toda la información operativa y financiera que los distintos departamentos necesitan para tomar decisiones diarias: ventas, cobranza, producción, inventario, compras y contabilidad.

El módulo no modifica los procesos existentes de Odoo; en cambio, crea vistas de base de datos (SQL views) que consolidan y presentan información ya registrada en el sistema de una manera más útil para el negocio. Esto significa que los datos siempre están actualizados en tiempo real sin necesidad de exportar a Excel o ejecutar procesos adicionales.

Cada área de la empresa cuenta con su propio grupo de reportes accesible desde el menú principal de Odoo, con filtros predeterminados que facilitan el análisis diario. La mayoría de los reportes muestran automáticamente la información del día anterior al abrirse, lo que los hace ideales para revisiones matutinas de operación.

Además de las vistas interactivas (tabla y tabla dinámica), varios reportes pueden exportarse como documentos PDF con formato corporativo o como archivos Excel listos para distribuir, facilitando el trabajo con clientes, auditores o equipos externos.

## Objetivo de Negocio

- Proporcionar a los gerentes de ventas, producción, compras y finanzas un acceso unificado a los reportes operativos del día anterior sin necesidad de abrir múltiples módulos o exportar datos.
- Eliminar el uso de hojas de cálculo externas para el seguimiento de cobranza, producción de polvos y emulsiones, consumos de materia prima y costos de flete.
- Permitir la generación de reportes PDF con formato oficial de la empresa (número de formato, revisión, logo) directamente desde Odoo para uso en auditorías y rendición de cuentas.
- Ofrecer al área de contabilidad herramientas de auditoría del libro mayor con agrupación por centro de costos/división, exportables a Excel para revisión externa.
- Controlar el inventario físico mediante un formato imprimible de conteo físico que incluye las cantidades actuales en Odoo como referencia para el contador.
- Calcular en tiempo real las toneladas pendientes de entrega a una fecha y hora determinada, apoyando la planeación logística y de producción.

## Flujos de Negocio Principales

### Flujo 1: Revisión diaria de ventas e ingresos bancarios

**Descripción:** Cada mañana, el área de ventas y tesorería revisa los ingresos del día anterior, ya sea por cobros con cheque, transferencia electrónica, efectivo u otros métodos. El flujo consolida los movimientos bancarios y las facturas cobradas de forma automática.

**Pasos:**
1. El usuario accede al menú **Accounting Reports** desde el menú principal.
2. Selecciona la opción correspondiente: **Bank Check Report**, **Bank Electronic Transfer Report**, **Bank Cash Report** o **Bank Other Report**.
3. El sistema muestra automát
<!-- odoo-docs: last-commit=8e71b5dbe6264665fc32329f2b4a2ff809c24057 | updated=2026-05-11 -->
