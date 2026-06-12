# report_account_move_payment_receipt — Report Account Move Payment Receipt Real

> **Version:** 17.0.1.0.1 | **License:** LGPL-3 | **Author:** Jarsa

<!-- ============================================================ -->
<!-- ENGLISH SECTION — Technical Reference                        -->
<!-- ============================================================ -->

## Overview

This module modifies and replaces the standard Odoo accounting payment receipt report to adapt it to real operational requirements. It extends the `account.move` native model by binding a custom QWeb PDF report (`report_account_payment_receipt`) directly to it. The module overrides the default report action with a customized template defined in `reports/report_account_move_payment_receipt.xml`.

## Dependencies

### Odoo / OCA Modules

- `account` — Required as the base accounting module; provides the `account.move` model to which the custom report is bound.

### Python Libraries

None.

## Installation

1. Place the module in your addons path.
2. Update the module list: **Settings → Activate Developer Mode → Update Apps List**
3. Search for `report_account_move_payment_receipt` and click **Install**.
4. No additional post-install configuration is required. The report will be automatically available on `account.move` records.

## Models Reference

This module does not define any new Python models. It exclusively provides a QWeb report bound to the existing `account.move` model from the `account` module.

## Security Groups

No new security groups or access control rules are defined in this module. Access to the report inherits the permissions defined by the `account` module for the `account.move` model.

## Menus & Actions

No new menu items are introduced by this module. The report action is accessible through the existing Odoo accounting interface.

## Reports

| Report Name | Model | Report Type | Trigger |
|---|---|---|---|
| Payment Receipt | `account.move` | QWeb PDF | Action binding on `account.move` (available via the **Print** menu on journal entries / payment records) |

- **Technical report name:** `report_account_move_payment_receipt.report_account_payment_receipt`
- **Report file:** `report_account_move_payment_receipt.report_account_payment_receipt`
- **Binding type:** `report` (appears in the Print action menu on `account.move` records)

---

<!-- ============================================================ -->
<!-- SECCIÓN EN ESPAÑOL — Documentación Funcional                 -->
<!-- ============================================================ -->

## Descripción General

Este módulo personaliza el reporte de recibo de pago que Odoo genera para los movimientos contables (`account.move`). El objetivo principal es reemplazar el reporte estándar de Odoo con una versión adaptada a los requerimientos reales de operación del cliente, modificando el formato, los datos mostrados o el diseño del documento impreso que se entrega como comprobante de pago.

El reporte se activa directamente desde los registros contables en Odoo, permitiendo al usuario imprimir o descargar un comprobante en formato PDF desde cualquier registro de pago o asiento contable. Al instalar este módulo, el reporte personalizado sustituye o complementa el comportamiento estándar de impresión de recibos de pago en el módulo de Contabilidad.

Está diseñado para equipos de contabilidad, tesorería y administración que necesitan emitir comprobantes de pago con un formato específico que cumpla con los requerimientos internos o comerciales de la organización.

## Objetivo de Negocio

- Emitir comprobantes de pago en formato PDF con un diseño adaptado a los requerimientos reales del cliente.
- Reemplazar el reporte estándar de Odoo por uno que refleje la imagen corporativa y la información necesaria para operaciones financieras.
- Facilitar la entrega de recibos de pago a proveedores, clientes o internamente dentro del área de contabilidad.
- Garantizar que la información presentada en el comprobante cumple con los estándares operativos definidos por la empresa.
- Reducir el trabajo manual de formateo o post-procesamiento de documentos contables de pago.

## Flujos de Negocio Principales

### Flujo 1: Impresión del Recibo de Pago desde un Movimiento Contable

**Descripción:** Este flujo se desencadena cuando un usuario necesita generar un comprobante impreso de un pago registrado en Odoo. El resultado es un documento PDF con el formato personalizado definido por este módulo.

**Pasos:**
1. El usuario navega a **Contabilidad** en el menú principal de Odoo.
2. Accede a los registros de **Pagos** o **Asientos Contables** según corresponda.
3. Abre el registro del movimiento contable (`account.move`) para el cual desea generar el recibo.
4. En la parte superior del registro, hace clic en el menú de impresión o acción de reporte (botón **Imprimir** o ícono de engranaje).
5. Selecciona la opción **"Payment Receipt"** (Recibo de Pago) de la lista de reportes disponibles.
6. Odoo genera el PDF con el template personalizado definido en este módulo.
7. El usuario descarga, imprime o envía el comprobante según sus necesidades.

**Reglas de negocio importantes:**
- El reporte está vinculado directamente al modelo `account.move`, por lo que está disponible en todos los registros de dicho modelo que el usuario tenga permisos para ver.
- El acceso al reporte hereda los permisos del módulo estándar de contabilidad; no requiere configuración adicional de seguridad.
- El tipo de reporte es QWeb PDF, lo que significa que se genera del lado del servidor y requiere que Odoo tenga configurado correctamente su motor de generación de PDFs (wkhtmltopdf o equivalente).

## Guía de Configuración

1. **Instalar el módulo:** Ir a **Configuración → Aplicaciones**, buscar `Report Account Move Payment Receipt Real` e instalar.
2. **Verificar el reporte:** Abrir cualquier registro en **Contabilidad → Pagos** o **Contabilidad → Contabilidad → Asientos contables**, hacer clic en el menú de impresión y verificar que aparezca la opción **"Payment Receipt"**.
3. **Motor de PDF:** Asegurarse de que el servidor de Odoo tenga correctamente instalado y configurado `wkhtmltopdf` para la generación de reportes en PDF. Esto se puede verificar en **Configuración → Técnico → Acciones → Reportes**.
4. **Advertencia:** Si existía previamente otro reporte con el mismo nombre o binding sobre `account.move`, este módulo puede sobreescribir o convivir con él dependiendo de la configuración del sistema. Se recomienda verificar que no existan conflictos con otros módulos de reportes de pago.

## Campos y Pantallas Clave

### Movimiento Contable (account.move)

Este módulo no agrega campos nuevos al modelo. Actúa exclusivamente sobre la acción de reporte disponible para los registros existentes. Los campos mostrados en el reporte dependen del template QWeb definido en `reports/report_account_move_payment_receipt.xml`.

| Campo en pantalla | Para qué sirve | Valores posibles / Notas |
|---|---|---|
| (Determinado por el template QWeb) | El contenido exacto del reporte depende de la plantilla XML personalizada incluida en el módulo | No determinado completamente sin inspección completa del archivo de plantilla |

## Automatizaciones y Reglas

Este módulo no define automatizaciones, acciones programadas ni reglas de registro adicionales. El reporte se genera únicamente bajo demanda, cuando el usuario lo solicita manualmente desde el registro contable.

## Reportes Disponibles

### Recibo de Pago (Payment Receipt)

- **Nombre en pantalla:** Payment Receipt
- **Modelo:** Movimientos Contables (`account.move`)
- **Cómo acceder:** Desde cualquier registro de movimiento contable o pago en Odoo, mediante el menú **Imprimir → Payment Receipt**.
- **Formato:** PDF generado con tecnología QWeb.
- **Información mostrada:** Datos del comprobante de pago adaptados a los requerimientos reales del cliente (el detalle exacto del contenido está definido en el template QWeb personalizado del módulo).

## Preguntas Frecuentes (FAQ)

**P: ¿Dónde encuentro el botón para imprimir el Recibo de Pago?**
R: Debes abrir el registro de un pago o asiento contable en el módulo de Contabilidad. Una vez dentro del registro, busca el menú de impresión (generalmente representado por un ícono de engranaje o un botón que dice "Imprimir") en la parte superior de la pantalla. Ahí aparecerá la opción "Payment Receipt".

**P: ¿Este reporte reemplaza el recibo de pago que ya tenía en Odoo?**
R: Este módulo agrega o reemplaza el reporte de recibo de pago estándar con una versión personalizada adaptada a los requerimientos de la empresa. Si existía un reporte previo con el mismo nombre, es posible que este lo sustituya. Se recomienda verificar con el equipo de implementación si hay algún conflicto.

**P: ¿El reporte está disponible para todos los movimientos contables o solo para los pagos?**
R: El reporte está vinculado al modelo general de movimientos contables (`account.move`), por lo que técnicamente aparece disponible para todos los registros de ese modelo. Sin embargo, su uso principal está pensado para registros de tipo pago.

**P: ¿Puedo enviar el Recibo de Pago directamente por correo electrónico desde Odoo?**
R: Odoo permite adjuntar reportes PDF al enviar correos desde los registros. Sin embargo, este módulo no configura explícitamente una plantilla de correo para este reporte. La funcionalidad de envío por correo dependerá de la configuración general del módulo de contabilidad.

**P: ¿El reporte funciona en todos los idiomas configurados en Odoo?**
R: El reporte generará el contenido en el idioma configurado para el usuario o la empresa, siempre que las traducciones correspondientes estén disponibles en Odoo. Este módulo no incluye archivos de traducción propios (`.po`), por lo que las etiquetas personalizadas del template podrían mostrarse en el idioma en que fueron escritas originalmente.

**P: ¿Necesito configurar algo especial después de instalar el módulo?**
R: No se requiere configuración adicional. Una vez instalado, el reporte estará disponible automáticamente en los registros de movimientos contables. Solo debes asegurarte de que el servidor tenga correctamente instalado el motor de generación de PDFs (`wkhtmltopdf`).

**P: ¿Qué pasa si desinstalo este módulo?**
R: Al desinstalar el módulo, la acción de reporte personalizada será eliminada del sistema. Si el reporte estándar de Odoo fue reemplazado, es posible que la opción de imprimir el recibo de pago deje de estar disponible o vuelva al comportamiento original de Odoo según la configuración del sistema.

---

<!-- ============================================================ -->
<!-- NOTEBOOKLM TRAINING SECTION                                  -->
<!-- ============================================================ -->

## 🤖 Contexto para Asistente IA

> Esta sección está optimizada para el entrenamiento del asistente de IA del cliente.

**¿Qué hace este módulo en una oración?**
Este módulo reemplaza el reporte estándar de recibo de pago en Odoo con una versión personalizada en formato PDF, disponible directamente desde los movimientos contables.

**Palabras clave asociadas a este módulo:**
- Recibo de pago
- Payment Receipt
- Reporte de pago
- Comprobante de pago
- Movimiento contable
- account.move
- Imprimir recibo
- Reporte contable PDF
- QWeb PDF
- Reporte personalizado
- Contabilidad
- Jarsa
- Impresión de pagos
- Documento de pago

**Casos de uso típicos:**
1. "¿Cómo imprimo el recibo de un pago registrado en Odoo?"
2. "¿Dónde está la opción para generar el comprobante de pago en PDF?"
3. "El recibo de pago no aparece en el menú de impresión, ¿qué hago?"
4. "¿Puedo personalizar el formato del recibo de pago que genera Odoo?"
5. "Necesito imprimir un comprobante para entregarle al proveedor por el pago realizado."
6. "¿El reporte de pago incluye el nombre del proveedor y el monto pagado?"
7. "¿Cómo accedo al reporte Payment Receipt desde un asiento contable?"
8. "¿Este módulo modifica algún dato contable o solo cambia el formato del reporte?"

**Lo que este módulo NO hace:**
- No modifica la lógica contable ni los cálculos de pagos en Odoo; únicamente afecta el formato del reporte impreso.
- No agrega campos nuevos a los movimientos contables ni a los registros de pagos.
- No incluye funcionalidades de envío automático de comprobantes por correo electrónico.
- No gestiona la numeración, validación ni conciliación de pagos; esas funciones corresponden al módulo estándar de contabilidad de Odoo.
<!-- odoo-docs: last-commit=8e71b5dbe6264665fc32329f2b4a2ff809c24057 | updated=2026-05-11 -->
