# l10n_mx_banorte_check_report — Report Check for Banorte

> **Version:** 17.0.1.0.1 | **License:** LGPL-3 | **Author:** Jarsa

<!-- ============================================================ -->
<!-- ENGLISH SECTION — Technical Reference                        -->
<!-- ============================================================ -->

## Overview

This module extends the Mexican check printing functionality in Odoo by providing an XLSX-format check report specifically designed for Banorte bank. It inherits from `account.payment` and `res.currency` to override check printing behavior and currency-to-words conversion, routing Banorte-layout payments to a custom XLSX report instead of the default PDF output. The amount-in-words conversion is handled using the `num2words` Python library with locale-aware language support.

## Dependencies

### Odoo / OCA Modules

- `l10n_mx_check_printing` — Provides the base Mexican check printing functionality, including the `mx_check_layout` field on journals and the Banorte action reference used to identify the correct layout.
- `report_xlsx` — Provides the XLSX report engine (`report_type: xlsx`) required to render the Banorte check template as an Excel file.

### Python Libraries

- `num2words` — Used in `res_currency.amount_to_text()` to convert numeric amounts into words in the appropriate locale language for check printing.

## Installation

1. Place the module in your addons path.
2. Update the module list: **Settings → Activate Developer Mode → Update Apps List**
3. Search for `l10n_mx_banorte_check_report` and click **Install**.
4. Ensure the `num2words` Python package is installed in your environment: `pip install num2words`.
5. Configure the journal's check layout to **Banorte** in **Accounting → Configuration → Journals** for the module to route printing correctly.

## Models Reference

### `account.payment` — Payment

| Field Name | Type | Label (string) | Description |
|---|---|---|---|
| *(inherited fields only — no new fields defined)* | — | — | This model is extended via `_inherit`; no new fields are added. |

**Key methods:**

- `do_print_checks()`: Overrides the standard check printing action. If the payment's journal `mx_check_layout` matches the Banorte action reference (`l10n_mx_check_printing.action_print_check_banorte`), it sets the payment state to `posted` and returns an `ir.actions.report` action of type `xlsx` targeting the Banorte XLSX report. Otherwise, it delegates to the parent implementation.
- `get_pages()`: Builds and returns a list of page dictionaries containing the data to be rendered in the XLSX template, including check number, formatted date (long format), partner name (uppercased), currency, state, formatted amount, and amount in words (uppercased, wrapped with `(* ... *)`).

---

### `res.currency` — Currency

| Field Name | Type | Label (string) | Description |
|---|---|---|---|
| *(inherited fields only — no new fields defined)* | — | — | This model is extended via `_inherit`; no new fields are added. |

**Key methods:**

- `amount_to_text(amount)`: Overrides the standard currency-to-words conversion. Splits the amount into integer and fractional parts, converts the integer part to words using `num2words` in the user's active language (`lang.iso_code`), appends the currency unit label, and formats the cents as `XX/100 M.N.` (Mexican notation). Falls back to English if the language is not supported by `num2words`.

## Security Groups

No new security groups or access control rules are defined in this module. Access is governed by the existing permissions of the `l10n_mx_check_printing` and base `account` modules.

## Menus & Actions

No new menu items are introduced by this module. The Banorte XLSX report is triggered programmatically through the existing **Print Checks** button available on `account.payment` records when the journal layout is set to Banorte.

## Reports

| Report Name | Technical Name | Model | Trigger |
|---|---|---|---|
| Banorte Check (XLSX) | `l10n_mx_banorte_check_report.banorte_check_xlsx` | `account.payment` | Triggered via the **Print Checks** button on a payment when the journal's check layout is set to Banorte |

---

<!-- ============================================================ -->
<!-- SECCIÓN EN ESPAÑOL — Documentación Funcional                 -->
<!-- ============================================================ -->

## Descripción General

Este módulo fue desarrollado para empresas mexicanas que realizan pagos mediante cheques emitidos a través del banco Banorte. Su función principal es generar el formato de cheque en Excel (XLSX) con la estructura y el contenido requeridos por dicha institución bancaria, en lugar del formato PDF estándar que ofrece Odoo.

El módulo se integra de forma transparente con el proceso de impresión de cheques ya existente en Odoo. Cuando el usuario intenta imprimir un cheque cuyo diario contable está configurado con el layout de Banorte, el sistema detecta automáticamente esta configuración y redirige la generación del documento hacia el reporte XLSX especializado.

Adicionalmente, el módulo mejora la conversión de montos en letra, ajustándola al estándar utilizado en México: la parte entera se escribe con palabras en el idioma configurado en el sistema, y los centavos se expresan en formato de fracción (`XX/100 M.N.`), tal como lo requieren los cheques bancarios en México.

## Objetivo de Negocio

- Cumplir con el formato oficial de cheques requerido por Banorte para pagos emitidos desde Odoo.
- Automatizar la generación del documento de cheque en formato XLSX, reduciendo errores manuales de llenado.
- Garantizar que el monto en letra aparezca correctamente en el idioma del sistema y con la notación monetaria mexicana (`M.N.`).
- Integrar el flujo de impresión de cheques Banorte dentro del proceso estándar de pagos de Odoo sin requerir pasos adicionales del usuario.
- Registrar automáticamente el pago como **Publicado** al momento de imprimir el cheque, asegurando la trazabilidad contable.

## Flujos de Negocio Principales

### Flujo 1: Impresión de Cheque Banorte desde un Pago

**Descripción:** Este flujo se activa cuando un usuario intenta imprimir un cheque para un pago registrado en un diario configurado con el layout de Banorte. El resultado es la descarga de un archivo XLSX con el formato de cheque listo para imprimir.

**Pasos:**
1. El usuario navega a **Contabilidad → Pagos** y localiza el pago al proveedor que desea pagar mediante cheque.
2. El usuario hace clic en el botón **Imprimir Cheques** dentro del formulario del pago.
3. El sistema verifica si el diario del pago tiene configurado el layout de Banorte.
4. Si el layout corresponde a Banorte, el sistema cambia automáticamente el estado del pago a **Publicado**.
5. El sistema genera y descarga el archivo XLSX con el formato de cheque Banorte, incluyendo: número de cheque, fecha larga, nombre del beneficiario en mayúsculas, monto numérico formateado y monto en letra con notación `M.N.`.
6. El usuario imprime el archivo XLSX en el papel de cheque físico del banco.

**Reglas de negocio importantes:**
- El módulo solo activa el flujo XLSX si el layout del diario es exactamente `l10n_mx_check_printing.action_print_check_banorte`. Cualquier otro layout seguirá el comportamiento estándar de Odoo.
- El pago se marca como **Publicado** automáticamente en el momento de la impresión, lo que impide modificaciones posteriores al registro contable.
- El nombre del beneficiario siempre se imprime en mayúsculas.
- El monto en letra se genera en el idioma activo del usuario en Odoo; si el idioma no es soportado por la librería de conversión, se usa inglés como respaldo.
- Los centavos siempre se expresan como `XX/100 M.N.` independientemente del idioma seleccionado.

## Guía de Configuración

1. **Instalar el módulo** desde **Configuración → Aplicaciones**, buscando `Report Check for Banorte`.
2. **Verificar la instalación de la dependencia Python:** Asegurarse de que la librería `num2words` esté disponible en el servidor de Odoo. En caso contrario, ejecutar `pip install num2words` en el entorno del servidor.
3. **Configurar el diario de cheques Banorte:** Ir a **Contabilidad → Configuración → Diarios**, seleccionar el diario bancario de Banorte y, en la pestaña de configuración avanzada, establecer el campo **Layout de cheques MX** con el valor **Banorte**.
4. **Verificar el idioma del sistema:** El monto en letra se genera en el idioma configurado para el usuario. Se recomienda tener instalado el idioma **Español (MX)** para garantizar la correcta conversión.
5. **Probar la impresión:** Crear un pago de prueba usando el diario configurado y hacer clic en **Imprimir Cheques** para verificar que se descarga el archivo XLSX correctamente.

> **Advertencia:** Una vez que se hace clic en **Imprimir Cheques**, el pago pasa automáticamente al estado **Publicado**. Este cambio es contablemente significativo y no se puede revertir fácilmente. Asegúrese de que los datos del pago sean correctos antes de imprimir.

## Campos y Pantallas Clave

### Pago (Pantalla de Pago)

| Campo en pantalla | Para qué sirve | Valores posibles / Notas |
|---|---|---|
| Número de cheque | Identifica de forma única el cheque emitido; se imprime en el documento XLSX | Generado automáticamente por la secuencia del diario |
| Fecha | Fecha que aparece en el cheque físico; se imprime en formato largo (ej. "15 de enero de 2025") | Fecha del pago registrado en Odoo |
| Beneficiario | Nombre de la empresa o persona a quien se emite el cheque; se imprime en mayúsculas | Tomado del campo **Contacto** del pago |
| Importe | Monto numérico del cheque con símbolo de moneda | Formateado según la moneda del pago |
| Importe en letras | Monto escrito con palabras en el idioma del sistema, con centavos en formato `XX/100 M.N.` | Generado automáticamente; incluye el nombre de la unidad monetaria (ej. "Pesos") |
| Moneda | Divisa en la que se emite el cheque | Tomada del diario o del pago |
| Estado | Estado contable del pago | Se establece en **Publicado** automáticamente al imprimir |

### Diario (Pantalla de Configuración de Diarios)

| Campo en pantalla | Para qué sirve | Valores posibles / Notas |
|---|---|---|
| Layout de cheques MX | Determina qué formato de cheque se usará al imprimir | Debe seleccionarse **Banorte** para activar este módulo |

## Automatizaciones y Reglas

- **Cambio automático de estado al imprimir:** Se ejecuta cuando el usuario hace clic en **Imprimir Cheques** y el layout del diario es Banorte. Resultado: el pago pasa automáticamente del estado borrador o cualquier estado previo al estado **Publicado** (`posted`), registrando los asientos contables correspondientes.

## Reportes Disponibles

**Cheque Banorte (XLSX)**
- **Cómo acceder:** Desde el formulario de un pago, haciendo clic en el botón **Imprimir Cheques**, siempre que el diario tenga configurado el layout de Banorte.
- **Qué muestra:** Una hoja de cálculo Excel con los datos del cheque: número de cheque, fecha en formato largo, nombre del beneficiario en mayúsculas, monto numérico con símbolo de moneda, y monto en letra con el formato `(* IMPORTE EN PALABRAS *)` más los centavos en notación `XX/100 M.N.`
- **Formato:** XLSX (Microsoft Excel), diseñado para imprimirse sobre el papel de cheque físico de Banorte.

## Preguntas Frecuentes (FAQ)

**P: ¿Este módulo funciona con cualquier banco o solo con Banorte?**
R: Solo funciona con Banorte. El módulo detecta específicamente el layout de cheques configurado como Banorte en el diario. Si el diario tiene cualquier otro layout, el sistema utilizará el comportamiento estándar de Odoo para imprimir cheques.

**P: ¿En qué idioma se genera el monto en letra?**
R: El monto en letra se genera automáticamente en el idioma que tenga configurado el usuario en Odoo al momento de imprimir. Si el idioma no está soportado por la librería de conversión, el sistema utiliza inglés como respaldo. Para obtener el resultado en español mexicano, se recomienda tener el idioma **Español (MX)** instalado y activo.

**P: ¿Por qué el pago queda en estado "Publicado" después de imprimir el cheque?**
R: Esto es parte del diseño del módulo. Al imprimir el cheque, el sistema asume que el pago ha sido formalizado y lo registra contablemente de forma automática. Esto garantiza que haya trazabilidad entre el cheque físico emitido y el movimiento contable en Odoo. Se recomienda revisar todos los datos antes de hacer clic en **Imprimir Cheques**.

**P: ¿Puedo volver a imprimir el cheque si cometí un error?**
R: Técnicamente sí es posible volver a ejecutar la acción de impresión, ya que el módulo no bloquea la reimpresión. Sin embargo, dado que el pago ya habrá sido publicado en el primer intento, cualquier corrección de datos (monto, beneficiario, fecha) requeriría cancelar y recrear el pago siguiendo los procesos contables estándar de Odoo.

**P: ¿Qué pasa si no tengo instalada la librería `num2words` en el servidor?**
R: El módulo fallará al intentar generar el monto en letra, lo que resultará en un error al imprimir el cheque. Es indispensable instalar la librería `num2words` en el entorno Python del servidor de Odoo antes de usar este módulo (`pip install num2words`).

**P: ¿El archivo XLSX generado está listo para imprimirse directamente sobre el cheque físico?**
R: El archivo XLSX está estructurado con los datos correctos según el formato Banorte, pero la alineación final depende de que la impresora y el papel de cheque físico estén correctamente configurados. Se recomienda hacer una prueba de impresión sobre papel normal antes de usar el papel de cheque real.

**P: ¿Los centavos siempre aparecen en formato XX/100 M.N.?**
R: Sí, independientemente del idioma del usuario o de la moneda del pago, los centavos siempre se expresan en el formato `XX/100 M.N.` (notación estándar para cheques en México), seguido de la parte entera en palabras y el nombre de la unidad monetaria.

---

<!-- ============================================================ -->
<!-- NOTEBOOKLM TRAINING SECTION                                  -->
<!-- ============================================================ -->

## 🤖 Contexto para Asistente IA

> Esta sección está optimizada para el entrenamiento del asistente de IA del cliente.

**¿Qué hace este módulo en una oración?**
Genera automáticamente el formato de cheque de Banorte en archivo Excel (XLSX) desde los pagos de Odoo, incluyendo el monto en letra con notación mexicana.

**Palabras clave asociadas a este módulo:**
- Cheque Banorte
- Impresión de cheques
- Cheques en XLSX
- Cheques México
- Monto en letra
- Layout Banorte
- Pago con cheque
- Formato de cheque
- Imprimir cheques
- num2words
- M.N. (Moneda Nacional)
- Diario Banorte
- Cheque proveedor
- Report XLSX
- l10n_mx

**Casos de uso típicos:**
1. Un usuario de cuentas por pagar necesita imprimir un cheque para pagar a un proveedor usando el banco Banorte y quiere que Odoo genere el documento directamente.
2. El área de tesorería quiere asegurarse de que el monto en letra en el cheque físico esté en español y con el formato correcto de centavos (`XX/100 M.N.`).
3. Un administrador de Odoo necesita configurar el diario bancario de Banorte para que los cheques se generen en formato Excel en lugar de PDF.
4. Un contador necesita que el pago quede registrado como publicado automáticamente al momento de emitir el cheque, para mantener la integridad contable.
5. El equipo de pagos quiere saber por qué al hacer clic en "Imprimir Cheques" de Banorte se descarga un archivo `.xlsx` en lugar de un PDF.
6. Un usuario reporta que el monto en letra no aparece correctamente y necesita saber si el problema es el idioma configurado en su perfil.

**Lo que este módulo NO hace:**
- No gestiona la impresión de cheques de bancos distintos a Banorte; otros layouts siguen el comportamiento estándar de Odoo.
- No envía el cheque por correo electrónico ni genera una versión PDF del formato Banorte.
- No valida si el número de cheque ya fue utilizado previamente ni gestiona la chequera (eso corresponde al módulo base de impresión de cheques).
- No modifica el flujo contable de conciliación bancaria; únicamente genera el documento imprimible.
<!-- odoo-docs: last-commit=8e71b5dbe6264665fc32329f2b4a2ff809c24057 | updated=2026-05-11 -->
