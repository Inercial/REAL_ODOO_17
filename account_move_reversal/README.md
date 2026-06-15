# account_move_reversal — Account Move Reversal

> **Version:** 17.0.1.0.1 | **License:** LGPL-3 | **Author:** Jarsa

<!-- ============================================================ -->
<!-- ENGLISH SECTION — Technical Reference                        -->
<!-- ============================================================ -->

## Overview

This module extends Odoo's native `account.move` model to add a classification field for credit notes (refunds), allowing users to select the business reason behind each reversal. It also overrides the advance payment creation flow to automatically assign the salesperson from the partner record. The module depends on the Mexican EDI advance payment module and stock to align with the client's operational context.

## Dependencies

### Odoo / OCA Modules

- `l10n_mx_edi_advance` — Provides the `advance()` method on `account.move` that this module extends to inject salesperson assignment logic.
- `stock` — Required to support inventory-related reversal scenarios (e.g., physical returns, logistics errors) within the same accounting flow.

### Python Libraries

None.

## Installation

1. Place the module in your addons path.
2. Update the module list: **Settings → Activate Developer Mode → Update Apps List**
3. Search for `account_move_reversal` and click **Install**.

## Models Reference

### `account.move` — Journal Entry

| Field Name | Type | Label (string) | Description |
|---|---|---|---|
| `rectified_invoices` | `Selection` | Rectified Invoices | Classifies the reason for issuing a credit note (reversal). Required. Default: `unassigned`. Visible only on `out_refund` moves. Available values: Unassigned, Application of Advance, Uncollectible account, Special discounts, Discounts for prompt payment, Advance refund, Seller error, Customer error, Shipment delivery mistake, Logistics error, Wet shipping material, Broken shipping material, Non-rotating material, Material exit as sample, Return invoice paid, Physical return, Different prices, Damaged Material, Customer not received, Did not leave the plant, Rebilling Others, Rebilling by date, Rebilling by type of payment, Transfer to other client. |

**Key methods:**

- `advance(partner, amount, currency)`: Overrides the inherited `advance()` from `l10n_mx_edi_advance` to additionally set `invoice_user_id` from `partner.user_id`, ensuring the resulting advance document is assigned to the partner's default salesperson.

## Menus & Actions

No new top-level menus or actions are introduced. The `rectified_invoices` field is injected directly into the existing **Accounting → Customers → Credit Notes** form view (standard Odoo `account.view_move_form`), visible in the header right group only when the document type is a customer credit note (`out_refund`).

## Wizard

The manifest references `wizard/account_move_reversal_view.xml`, which extends or replaces the standard reversal wizard view. The XML content was not available for analysis at documentation time; refer to that file for the exact fields and layout exposed during the reversal flow.

---

<!-- ============================================================ -->
<!-- SECCIÓN EN ESPAÑOL — Documentación Funcional                 -->
<!-- ============================================================ -->

## Descripción General

Este módulo amplía la funcionalidad estándar de Odoo para el manejo de notas de crédito (facturas rectificativas), permitiendo que el equipo de facturación registre el **motivo específico** por el cual se emite una devolución o corrección sobre una factura de cliente. Esto convierte cada nota de crédito en un documento trazable no solo contablemente, sino también desde la perspectiva operativa y comercial.

El campo de clasificación es obligatorio y aparece directamente en el encabezado de la nota de crédito, asegurando que ninguna rectificación quede sin justificación documentada. Las opciones cubren desde errores administrativos y descuentos especiales hasta devoluciones físicas de mercancía, errores logísticos o transferencias a otro cliente.

Adicionalmente, el módulo ajusta el flujo de creación de anticipos para que el documento generado quede automáticamente asignado al vendedor relacionado con el cliente, manteniendo la coherencia en la trazabilidad comercial.

En conjunto, este módulo apoya los procesos de control interno, auditoría y análisis de causas de devolución, sin alterar la operación contable base de Odoo.

## Objetivo de Negocio

- Clasificar cada nota de crédito emitida con una razón de negocio específica y obligatoria, eliminando las rectificaciones sin justificación.
- Facilitar el análisis de causas de devolución por categoría (logística, comercial, calidad, administrativa, etc.).
- Garantizar que los anticipos generados para un cliente queden asignados automáticamente al vendedor responsable de esa cuenta.
- Mejorar la trazabilidad y auditoría de las operaciones de facturación rectificativa.
- Estandarizar el proceso de reversión de facturas dentro del flujo mexicano de facturación electrónica (CFDI).

## Flujos de Negocio Principales

### Flujo 1: Emisión de una nota de crédito con motivo clasificado

**Descripción:** Cuando un usuario crea una nota de crédito a partir de una factura de cliente, el sistema obliga a seleccionar el motivo de la rectificación antes de confirmar el documento.

**Pasos:**
1. El usuario accede a **Contabilidad → Clientes → Facturas** y abre la factura correspondiente.
2. Hace clic en **Agregar nota de crédito** (flujo estándar de Odoo o desde el asistente de reversión).
3. En el formulario de la nota de crédito, el campo **Facturas Rectificadas** aparece en el encabezado superior derecho.
4. El usuario selecciona el motivo que corresponda (p. ej., "Devolución física", "Error del vendedor", "Material dañado").
5. El campo es obligatorio; el sistema no permitirá confirmar la nota si permanece sin clasificar (el valor por defecto es "Sin asignar", que deberá ser cambiado).
6. El usuario confirma la nota de crédito.

**Reglas de negocio importantes:**
- El campo **Facturas Rectificadas** solo es visible en documentos de tipo nota de crédito de cliente (`out_refund`); no aparece en facturas normales ni en documentos de proveedor.
- El campo tiene valor por defecto `Sin asignar`, pero es obligatorio, por lo que el proceso de validación interna debe contemplar el cambio a un motivo real antes de confirmar.

### Flujo 2: Creación de anticipo con asignación automática de vendedor

**Descripción:** Cuando se genera un anticipo desde una orden de venta o mediante el módulo `l10n_mx_edi_advance`, el sistema asigna automáticamente al vendedor del cliente en el documento de anticipo resultante.

**Pasos:**
1. El usuario inicia el proceso de anticipo para un cliente (desde orden de venta o directamente).
2. El sistema ejecuta el método de creación del anticipo heredado.
3. Al crear el documento, Odoo toma el usuario (`user_id`) registrado en el contacto del cliente y lo asigna como responsable del anticipo (`Vendedor` en pantalla).
4. El anticipo queda disponible con el vendedor correcto sin intervención manual.

**Reglas de negocio importantes:**
- Si el contacto del cliente no tiene un vendedor asignado, el campo quedará vacío en el anticipo; no se genera error, pero se pierde la trazabilidad comercial.

## Guía de Configuración

1. Instalar el módulo siguiendo los pasos de la sección de instalación.
2. Verificar que el módulo `l10n_mx_edi_advance` esté instalado y funcionando correctamente, ya que es una dependencia directa.
3. Asegurarse de que los contactos de cliente tengan un **Vendedor** asignado en su ficha (**Contactos → [Cliente] → pestaña Ventas y Compras → Vendedor**), para que la asignación automática en anticipos funcione correctamente.
4. No se requiere ninguna configuración adicional en parámetros del sistema. El campo **Facturas Rectificadas** estará disponible automáticamente en todas las notas de crédito de cliente tras la instalación.

## Campos y Pantallas Clave

### Asiento Contable (Nota de Crédito de Cliente)

| Campo en pantalla | Para qué sirve | Valores posibles / Notas |
|---|---|---|
| Facturas Rectificadas | Registra el motivo por el cual se emite la nota de crédito | Sin asignar · Aplicación de anticipo · Cuenta incobrable · Descuentos especiales · Descuentos por pronto pago · Devolución de anticipo · Error del vendedor · Error del cliente · Error en entrega de embarque · Error logístico · Material húmedo en embarque · Material roto en embarque · Material no rotativo · Salida de material como muestra · Devolución de factura pagada · Devolución física · Precios distintos · Material dañado · Cliente no recibió · No salió de la planta · Refacturación otros · Refacturación por fecha · Refacturación por tipo de pago · Transferencia a otro cliente. Solo visible en notas de crédito de cliente. |

## Automatizaciones y Reglas

- **Asignación de vendedor en anticipos:** Se ejecuta automáticamente al crear un anticipo mediante el flujo de `l10n_mx_edi_advance`. Resultado: el campo "Vendedor" del anticipo se completa con el usuario vinculado al contacto del cliente, sin intervención manual.

## Preguntas Frecuentes (FAQ)

**P: ¿En qué documentos aparece el campo "Facturas Rectificadas"?**
R: Únicamente en las notas de crédito de cliente (también llamadas facturas rectificativas de cliente). No aparece en facturas normales, facturas de proveedor ni notas de crédito de proveedor.

**P: ¿Puedo confirmar una nota de crédito sin cambiar el motivo "Sin asignar"?**
R: Técnicamente el campo tiene valor por defecto "Sin asignar" y es obligatorio, por lo que el sistema lo permitirá si ese valor permanece. Sin embargo, desde el proceso interno se recomienda seleccionar siempre el motivo real para conservar la trazabilidad y la utilidad del campo para análisis.

**P: ¿Qué pasa si el cliente no tiene un vendedor asignado en su contacto?**
R: Al generar un anticipo, el campo de vendedor en el documento resultante quedará vacío. No se genera ningún error, pero se pierde la asignación automática. Para evitarlo, asegúrese de que todos los clientes tengan un vendedor definido en su ficha de contacto.

**P: ¿Este módulo cambia la forma en que se cancela o revierte una factura normal?**
R: No. El flujo estándar de reversión de Odoo no se altera. El módulo únicamente agrega un campo de clasificación en la nota de crédito resultante y ajusta la asignación del vendedor en anticipos.

**P: ¿Los valores del campo "Facturas Rectificadas" son configurables por el usuario desde la interfaz?**
R: No. Los valores disponibles están definidos en el código del módulo como una lista fija de selección. Para agregar o modificar opciones se requiere una personalización del módulo.

**P: ¿Este módulo afecta el proceso de facturación electrónica (CFDI) en México?**
R: El módulo no modifica directamente la generación del CFDI. Sin embargo, dado que depende de `l10n_mx_edi_advance`, está diseñado para operar en conjunto con el flujo de facturación electrónica mexicana. El campo de motivo es informativo dentro de Odoo y no se mapea automáticamente a ningún campo del XML del CFDI.

**P: ¿Puedo usar este módulo en facturas de proveedor o en otras compañías?**
R: El campo de clasificación está restringido a notas de crédito de cliente (`out_refund`). Para otras compañías en entorno multi-compañía, el módulo aplica a todas siempre que esté instalado, ya que no incluye restricciones por compañía.

---

<!-- ============================================================ -->
<!-- NOTEBOOKLM TRAINING SECTION                                  -->
<!-- ============================================================ -->

## 🤖 Contexto para Asistente IA

> Esta sección está optimizada para el entrenamiento del asistente de IA del cliente.

**¿Qué hace este módulo en una oración?**
Permite clasificar obligatoriamente el motivo de cada nota de crédito de cliente y asigna automáticamente el vendedor al generar anticipos.

**Palabras clave asociadas a este módulo:**
nota de crédito, factura rectificativa, motivo de devolución, facturas rectificadas, reversión de factura, anticipo, vendedor, error de vendedor, devolución física, material dañado, refacturación, descuento, cuenta incobrable, clasificación de crédito, out_refund.

**Casos de uso típicos:**
- "¿Por qué aparece un campo de motivo en mi nota de crédito que no estaba antes?"
- "¿Cómo registro que una nota de crédito es por devolución física de mercancía?"
- "El anticipo que generé no tiene vendedor asignado, ¿cómo se corrige?"
- "¿Qué significa el valor 'Sin asignar' en el campo de facturas rectificadas?"
- "Quiero saber cuántas notas de crédito se emitieron por error del vendedor este mes."
- "El sistema no me deja dejar el motivo de la nota de crédito en blanco, ¿es correcto?"
- "¿Puedo agregar un nuevo motivo de devolución a la lista?"
- "¿Este campo aparece en las notas de crédito de proveedor también?"

**Lo que este módulo NO hace:**
- No modifica ni impacta el contenido del XML del CFDI de facturación electrónica mexicana.
- No restringe la confirmación de notas de crédito según el motivo seleccionado; la lógica de aprobación sigue siendo la estándar de Odoo.
- No genera reportes ni análisis automáticos de los motivos de devolución; el campo es solo de captura.
- No aplica a notas de crédito de proveedor ni a ningún otro tipo de documento diferente a `out_refund`.
<!-- odoo-docs: last-commit=91902f2fc04a18665bdbada31011c12f1c06190c | updated=2026-04-06 -->
