# report_account_invoice_real — Report Account Invoice Real

> **Version:** 17.0.1.0.9 | **License:** LGPL-3 | **Author:** Jarsa

<!-- ============================================================ -->
<!-- ENGLISH SECTION — Technical Reference                        -->
<!-- ============================================================ -->

## Overview

This module customizes the account invoice PDF reports in Odoo 17 to meet specific business requirements for a Mexican company. It extends the native `account.move` model and the `account.move.send` wizard to override report selection logic, ensuring that stamped CFDI invoices render a dedicated "original" template while credit memos use their own report layout. The module registers multiple QWeb report templates (customer invoices, credit memos, vendor bills, journals, delivery orders, and pólizas) and adds a `tons_display` field to invoice views.

## Dependencies

### Odoo / OCA Modules

- `l10n_mx_edi` — Required for Mexican electronic invoicing (CFDI) fields such as `l10n_mx_edi_cfdi_state` and `l10n_mx_edi_cfdi_attachment_id` used in report selection logic.
- `report_stock_picking_real` — Custom module that provides base report infrastructure and likely the `tons_display` field referenced on `account.move.line`.
- `account_payment_order_banorte` — Custom module for Banorte bank payment orders; required as a dependency for report context.
- `account_move_reversal` — Provides credit memo (reversal) functionality for `account.move`; required for credit memo report flows.
- `real` — Base custom module for the client's Odoo instance; provides foundational customizations.

### Python Libraries

None.

## Installation

1. Place the module in your addons path.
2. Update the module list: **Settings → Activate Developer Mode → Update Apps List**
3. Search for `report_account_invoice_real` and click **Install**.
4. All report templates are loaded automatically via the `data` entries in the manifest. No additional post-install configuration is required.

## Models Reference

### `account.move` — Journal Entry / Invoice

This model is inherited; no new fields are declared directly in this module. The module overrides the `_get_name_invoice_report` method.

| Field Name | Type | Label (string) | Description |
|---|---|---|---|
| `tons_display` | (inherited from `report_stock_picking_real`) | Tons | Displays the total tons associated with the invoice or invoice line. Referenced in views but declared in a dependency module. |
| `previous_folio` | (inherited from dependency) | Previous Folio | Shown in the invoice form after the `tons_display` field; represents a prior document folio reference. Declared in a dependency module. |

**Key methods:**
- `_get_name_invoice_report`: Overrides the native method to return `report_account_invoice_real.report_invoice_original_real` when the invoice has a sent CFDI stamp (`l10n_mx_edi_cfdi_state == 'sent'` and `l10n_mx_edi_cfdi_attachment_id` is set); otherwise delegates to the parent implementation.

### `account.move.send` (TransientModel) — Send & Print Invoice Wizard

This wizard model is inherited to override PDF report generation during the send/print flow.

| Field Name | Type | Label (string) | Description |
|---|---|---|---|
| (No new fields declared) | — | — | Only method logic is overridden. |

**Key methods:**
- `_prepare_invoice_pdf_report`: Overrides the native preparation method. Skips generation if a PDF report is already attached (`invoice_pdf_report_id`). Selects `report_account_invoice_real.report_invoice_credit_memo_real` for `out_refund` move types, or `report_account_invoice_real.action_report_invoice_original` for all other outgoing invoice types. Renders the selected report and populates `invoice_data["pdf_attachment_values"]` with the binary content, filename, MIME type, and field binding.

## Security Groups

No new security groups or `ir.model.access.csv` entries are defined in this module. Access control relies entirely on the dependency modules.

## Menus & Actions

No new menu items are defined in this module. The module extends existing Odoo accounting views only.

## Reports

All reports are QWeb templates registered under the `report_account_invoice_real` module technical name.

| Report ID / Name | Model | Trigger / Purpose |
|---|---|---|
| `report_invoice_original_real` / Report Invoice Original Real | `account.move` | Rendered for stamped CFDI customer invoices (sent state). Selected automatically by `_get_name_invoice_report`. |
| `action_report_invoice_original` | `account.move` | Used during send/print flow for outgoing invoices (non-credit-memo). Triggered by `_prepare_invoice_pdf_report`. |
| `report_invoice_credit_memo_real` | `account.move` | Used during send/print flow for `out_refund` (credit memo) documents. Triggered by `_prepare_invoice_pdf_report`. |
| `report_account_invoice_without_amount` | `account.move` | Invoice report variant without amounts. |
| `report_account_invoice_attachment_nc` | `account.move` | Attachment variant for credit notes (NC). |
| `report_account_invoice_instructions` | `account.move` | Invoice with payment instructions. |
| `report_account_invoice_vendor_bill` | `account.move` | Vendor bill report. |
| `report_account_invoice_vendor_credit_note` | `account.move` | Vendor credit note report. |
| `report_account_invoice_delivery_order` | `account.move` | Delivery order report linked to invoice. |
| `report_account_invoice_sales_journal` | `account.move` | Sales journal report. |
| `report_account_invoice_credit_journal` | `account.move` | Credit journal report. |
| `report_account_invoice_purchase_journal` | `account.move` | Purchase journal report. |
| `report_account_invoice_poliza` | `account.move` | Póliza contable (accounting entry journal voucher) report. |

---

<!-- ============================================================ -->
<!-- SECCIÓN EN ESPAÑOL — Documentación Funcional                 -->
<!-- ============================================================ -->

## Descripción General

Este módulo adapta los reportes de impresión de facturas de Odoo para cumplir con los requisitos reales de operación de la empresa, en el contexto de la facturación electrónica mexicana (CFDI). Su propósito principal es garantizar que cada tipo de documento fiscal —facturas de cliente, notas de crédito, facturas de proveedor, diarios contables y pólizas— se imprima con el formato correcto según las reglas de negocio establecidas.

El módulo detecta automáticamente si una factura ya fue timbrada ante el SAT y, en ese caso, utiliza la plantilla de impresión oficial ("original") en lugar de la genérica de Odoo. Del mismo modo, cuando se genera una nota de crédito, el sistema selecciona automáticamente el reporte específico para ese tipo de documento.

Adicionalmente, el módulo incorpora la visualización del campo "Toneladas" directamente en las líneas de factura y en el encabezado del documento, lo que permite a los usuarios del área comercial y de logística verificar los volúmenes facturados sin necesidad de consultar otros documentos.

Toda la lógica opera de manera transparente para el usuario: no requiere configuración manual ni selección de plantillas. El sistema elige el reporte adecuado en el momento de imprimir o enviar la factura.

## Objetivo de Negocio

- Garantizar que las facturas timbradas ante el SAT se impriman siempre con la plantilla oficial "original", cumpliendo con los requisitos de presentación fiscal.
- Automatizar la selección del reporte correcto según el tipo de documento (factura, nota de crédito, factura de proveedor), eliminando errores humanos al momento de imprimir.
- Proveer formatos de impresión diferenciados para cada necesidad: con monto, sin monto, con instrucciones de pago, para notas de crédito, para diarios y para pólizas contables.
- Mostrar el dato de toneladas en las facturas de venta, facilitando la verificación de volúmenes para empresas que operan con mercancías pesadas.
- Asegurar que los documentos enviados por correo electrónico al cliente incluyan el PDF correcto y con nombre de archivo adecuado de forma automática.

## Flujos de Negocio Principales

### Flujo 1: Impresión de Factura de Cliente Timbrada

**Descripción:** Cuando un usuario desea imprimir o descargar una factura de cliente que ya fue enviada al SAT (timbrada/sellada con CFDI), el sistema detecta automáticamente el estado del timbre y selecciona la plantilla de impresión "original".

**Pasos:**
1. El usuario abre una factura de cliente desde el menú **Contabilidad → Clientes → Facturas**.
2. El usuario hace clic en el botón de impresión o en la opción de descargar PDF.
3. El sistema verifica si la factura tiene estado CFDI "enviado" y si existe un archivo CFDI adjunto.
4. Si ambas condiciones se cumplen, el sistema genera el PDF usando la plantilla `report_invoice_original_real`.
5. Si no se cumplen, delega la generación al comportamiento estándar de Odoo.
6. El usuario recibe el PDF con el formato correcto.

**Reglas de negocio importantes:**
- La plantilla "original" solo se aplica cuando el CFDI ha sido efectivamente enviado al SAT (`l10n_mx_edi_cfdi_state == 'sent'`) Y existe un archivo CFDI adjunto.
- Si la factura no ha sido timbrada, se utiliza el reporte base de Odoo o el configurado en módulos dependientes.

---

### Flujo 2: Envío de Factura por Correo Electrónico

**Descripción:** Cuando el usuario utiliza el flujo de "Enviar e Imprimir" desde la factura, el sistema genera automáticamente el PDF correcto según el tipo de documento y lo adjunta al correo antes de enviarlo al cliente.

**Pasos:**
1. El usuario abre una factura de cliente o nota de crédito y hace clic en **Enviar e Imprimir**.
2. El sistema verifica si ya existe un reporte PDF adjunto a la factura (`invoice_pdf_report_id`).
3. Si no existe, el sistema determina el tipo de documento:
   - Si es una **nota de crédito** (`out_refund`): se usa la plantilla `report_invoice_credit_memo_real`.
   - Si es cualquier otro tipo de factura de salida: se usa la plantilla `action_report_invoice_original`.
4. El sistema renderiza el reporte PDF correspondiente.
5. El PDF generado se adjunta a los datos del correo con el nombre de archivo estándar de la factura.
6. El usuario puede revisar y enviar el correo con el documento correcto adjunto.

**Reglas de negocio importantes:**
- Si la factura ya tiene un PDF adjunto previo (`invoice_pdf_report_id`), el sistema no regenera el reporte, evitando sobrescribir documentos ya validados.
- La selección del reporte es automática y no requiere intervención del usuario.
- El nombre del archivo PDF sigue el estándar definido por el método `_get_invoice_report_filename()` de Odoo.

---

### Flujo 3: Visualización de Toneladas en Facturas de Venta

**Descripción:** Para empresas que facturan productos medidos en toneladas, el módulo agrega el campo "Tons" en las vistas de lista, formulario y kanban de las líneas de factura, así como en el encabezado del documento.

**Pasos:**
1. El usuario abre o crea una factura de cliente.
2. En la tabla de líneas de factura, puede activar la columna opcional **Tons** para verla junto a la cantidad.
3. En la vista de lista de facturas (**Contabilidad → Clientes → Facturas**), la columna **Tons** aparece disponible como columna opcional después de "Total".
4. En el encabezado de la factura (parte superior derecha del formulario), también se muestra el campo **Tons** con el total de la factura.

**Reglas de negocio importantes:**
- El campo "Tons" solo es visible en facturas de **cliente** (ventas). En facturas y notas de crédito de proveedor (`in_invoice`, `in_refund`), el campo se oculta automáticamente.
- El campo es de solo lectura y calculado; su valor proviene del módulo `report_stock_picking_real`.

---

### Flujo 4: Impresión de Reportes Especializados

**Descripción:** El módulo registra múltiples plantillas de reporte que pueden ser accedidas según el contexto: pólizas contables, diarios de ventas, compras y crédito, órdenes de entrega, y formatos sin monto.

**Pasos:**
1. El usuario accede a la factura o documento contable correspondiente.
2. Desde el menú de impresión (ícono de engranaje o botón "Imprimir"), selecciona el tipo de reporte deseado.
3. El sistema genera el PDF con la plantilla específica seleccionada.

**Reglas de negocio importantes:**
- Los reportes de diario (ventas, crédito, compras) están diseñados para impresión contable interna.
- El reporte de póliza (`report_account_invoice_poliza`) genera el comprobante contable en formato de póliza.
- El reporte "sin monto" (`report_account_invoice_without_amount`) permite entregar documentos a terceros sin revelar valores monetarios.

## Guía de Configuración

1. Instalar el módulo siguiendo los pasos de instalación descritos en la sección técnica.
2. Verificar que el módulo `l10n_mx_edi` esté correctamente configurado con los certificados del SAT en **Contabilidad → Configuración → Configuración → CFDI**.
3. No se requieren configuraciones adicionales dentro de este módulo: toda la lógica de selección de reportes opera automáticamente.
4. Para verificar que los reportes están disponibles, ir a **Configuración → Técnico → Reportes → Reportes** (en modo desarrollador) y buscar por "real" o "invoice".
5. **Advertencia:** Este módulo depende de `report_stock_picking_real` para el campo "Tons". Si ese módulo no está instalado correctamente, las vistas de factura mostrarán errores de campo faltante.

## Campos y Pantallas Clave

### Factura / Asiento Contable

| Campo en pantalla | Para qué sirve | Valores posibles / Notas |
|---|---|---|
| Tons | Muestra el total de toneladas facturadas en el documento completo | Valor numérico calculado; visible solo en facturas de cliente (oculto en facturas/notas de crédito de proveedor) |
| Folio Anterior | Referencia al folio del documento previo relacionado | Texto libre; visible en el formulario de factura después del campo Tons |

### Líneas de Factura

| Campo en pantalla | Para qué sirve | Valores posibles / Notas |
|---|---|---|
| Tons | Muestra las toneladas correspondientes a cada línea de producto | Valor numérico calculado; columna opcional en la tabla de líneas; oculta en documentos de proveedor |

## Automatizaciones y Reglas

- **Selección automática de plantilla de impresión:** Se ejecuta cada vez que el usuario imprime una factura. El sistema evalúa el estado CFDI de la factura y elige automáticamente entre la plantilla "original" (para facturas timbradas) y la plantilla estándar de Odoo. No requiere intervención del usuario.

- **Generación automática de PDF en el flujo de envío:** Se ejecuta cuando el usuario utiliza "Enviar e Imprimir". El sistema selecciona entre la plantilla de nota de crédito y la plantilla de factura original según el tipo de documento (`out_refund` vs. otros tipos de salida), y genera el PDF antes de adjuntarlo al correo.

- **Control de regeneración de PDF:** Si la factura ya tiene un reporte PDF adjunto, el sistema omite la regeneración automática, protegiendo documentos previamente generados y validados.

## Reportes Disponibles

| Reporte | Descripción | Cómo acceder |
|---|---|---|
| Factura Original | Formato oficial para facturas de cliente timbradas ante el SAT | Automático al imprimir facturas con CFDI enviado |
| Nota de Crédito | Formato específico para notas de crédito de cliente | Automático al enviar/imprimir documentos `out_refund` |
| Factura sin Monto | Versión de la factura que oculta los valores monetarios | Disponible desde el menú de impresión de la factura |
| Factura con Instrucciones | Incluye instrucciones de pago al pie del documento | Disponible desde el menú de impresión de la factura |
| Adjunto NC | Documento adjunto para notas de crédito | Disponible desde el menú de impresión |
| Factura de Proveedor | Formato para facturas recibidas de proveedores | Disponible en documentos de proveedor |
| Nota de Crédito de Proveedor | Formato para notas de crédito recibidas de proveedores | Disponible en documentos de proveedor |
| Orden de Entrega | Reporte de entrega vinculado a la factura | Disponible desde el menú de impresión de la factura |
| Diario de Ventas | Reporte contable interno de ventas del período | Disponible desde el menú de impresión |
| Diario de Crédito | Reporte contable interno de notas de crédito | Disponible desde el menú de impresión |
| Diario de Compras | Reporte contable interno de compras del período | Disponible desde el menú de impresión |
| Póliza | Comprobante de póliza contable del asiento | Disponible desde el menú de impresión de la factura |

## Preguntas Frecuentes (FAQ)

**P: ¿Por qué algunas facturas se imprimen con un formato diferente al de otras?**
R: El sistema selecciona automáticamente el formato según si la factura fue timbrada ante el SAT. Las facturas con CFDI enviado utilizan la plantilla "original", mientras que las que aún no han sido timbradas usan el formato estándar de Odoo. Esto es completamente automático y no requiere ninguna acción por parte del usuario.

**P: ¿Puedo elegir manualmente qué plantilla de reporte usar para imprimir una factura?**
R: La selección de la plantilla principal (original vs. estándar) es automática y depende del estado del CFDI. Sin embargo, desde el menú de impresión de la factura es posible seleccionar otros formatos disponibles como "sin monto", "con instrucciones", "póliza", etc.

**P: ¿Por qué no veo el campo "Tons" en las facturas de proveedor?**
R: El campo "Tons" fue diseñado para operaciones de venta y está configurado para ocultarse automáticamente en todos los documentos de proveedor (facturas de compra y notas de crédito de proveedor). Esto es por diseño para evitar confusión en los documentos de compra.

**P: Al hacer clic en "Enviar e Imprimir", ¿cómo sabe el sistema qué PDF adjuntar al correo?**
R: El sistema verifica el tipo de documento: si es una nota de crédito de cliente, usa la plantilla de nota de crédito; para cualquier otro tipo de factura de salida, usa la plantilla de factura original. El PDF se genera y adjunta automáticamente antes de que el correo sea enviado.

**P: ¿Qué pasa si ya hay un PDF adjunto en la factura y vuelvo a hacer "Enviar e Imprimir"?**
R: Si la factura ya tiene un reporte PDF adjunto previo, el sistema no regenera ni sobreescribe ese archivo. Esto protege los documentos que ya fueron generados y posiblemente compartidos o archivados.

**P: ¿El módulo funciona sin conexión al SAT o en facturas no timbradas?**
R: Sí. Si la factura no tiene estado CFDI "enviado" o no tiene archivo CFDI adjunto, el sistema delega la generación del reporte al comportamiento estándar de Odoo, por lo que el módulo funciona correctamente también para facturas no timbradas o en entornos de prueba.

**P: ¿Puedo imprimir una póliza contable desde la factura?**
R: Sí. El módulo incluye la plantilla de reporte "Póliza" (`report_account_invoice_poliza`) que genera el comprobante de póliza contable. Este reporte está disponible desde el menú de impresión de la factura cuando se accede en modo desarrollador o a través de la acción correspondiente.

**P: ¿El campo "Folio Anterior" es obligatorio para imprimir una factura?**
R: No. El campo "Folio Anterior" es informativo y su llenado es opcional. Su presencia en el formulario permite registrar referencias a documentos previos relacionados, pero no es requerido por ninguna validación del módulo para generar reportes.

---

<!-- ============================================================ -->
<!-- NOTEBOOKLM TRAINING SECTION                                  -->
<!-- ============================================================ -->

## 🤖 Contexto para Asistente IA

> Esta sección está optimizada para el entrenamiento del asistente de IA del cliente.

**¿Qué hace este módulo en una oración?**
Personaliza y automatiza la selección e impresión de reportes de facturas en Odoo para cumplir con los requisitos de facturación electrónica mexicana (CFDI) y necesidades operativas de la empresa, incluyendo formatos diferenciados para facturas, notas de crédito, diarios contables y pólizas.

**Palabras clave asociadas a este módulo:**
- Reporte de factura
- Factura original
- CFDI timbrado
- Nota de crédito
- Imprimir factura
- PDF factura
- Enviar factura por correo
- Toneladas en factura
- Tons
- Póliza contable
- Diario de ventas
- Factura sin monto
- Instrucciones de pago
- Folio anterior
- Factura de proveedor

**Casos de uso típicos:**
1. "¿Por qué mi factura se imprime diferente a la de mi compañero?"
2. "¿Cómo puedo imprimir una factura sin que aparezcan los montos?"
3. "Necesito imprimir la póliza contable de una factura, ¿cómo lo hago?"
4. "Al enviar la factura por correo, ¿qué formato PDF recibe el cliente?"
5. "¿Dónde veo las toneladas facturadas en una factura de venta?"
6. "¿Por qué no aparece el campo de toneladas en las facturas de mis proveedores?"
7. "¿El sistema elige automáticamente el formato de impresión o lo tengo que seleccionar yo?"
8. "¿Puedo reimprimir una factura que ya fue timbrada con el formato oficial?"

**Lo que este módulo NO hace:**
- No timbra facturas ante el SAT ni gestiona el proceso de firma electrónica CFDI; esa funcionalidad corresponde al módulo `l10n_mx_edi`.
- No modifica los datos contables ni los montos de las facturas; solo controla el formato de impresión y visualización.
- No agrega nuevos flujos de aprobación ni validaciones sobre el contenido de las facturas.
- No gestiona el envío masivo de facturas ni automatiza correos programados; solo interviene en el flujo individual de "Enviar e Imprimir".
<!-- odoo-docs: last-commit=bc3aed09b867c535fa821b5cc7f6af1e62e0cb44 | updated=2026-05-19 -->
