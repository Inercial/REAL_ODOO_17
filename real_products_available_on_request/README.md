# real_products_available_on_request — Real Products Available On Request

> **Version:** 17.0.1.0.1 | **License:** LGPL-3 | **Author:** Jarsa

<!-- ============================================================ -->
<!-- ENGLISH SECTION — Technical Reference                        -->
<!-- ============================================================ -->

## Overview

This module extends the native Odoo models `res.partner`, `sale.order`, `stock.picking`, and `stock.move` to introduce a `client_location` field that classifies contacts (specifically delivery addresses) as either **Local** or **Foreigner**. The field is propagated via related fields from the partner to sale orders, stock pickings, and stock moves, allowing downstream logistics documents to reflect the client's location category automatically.

## Dependencies

### Odoo / OCA Modules

- `sale` — Required to extend the `sale.order` model and inject the `client_location` field into the sale order form view.
- `stock_analytic` — Required to extend `stock.move` and `stock.picking` models; the view injection in `stock_move_view.xml` anchors itself relative to the `analytic_distribution` field provided by this module.

### Python Libraries

None.

## Installation

1. Place the module in your addons path.
2. Update the module list: **Settings → Activate Developer Mode → Update Apps List**
3. Search for `real_products_available_on_request` and click **Install**.
4. After installation, navigate to any contact record and set the **Client Location** field on delivery address entries to classify them as Local or Foreigner.

## Models Reference

### `res.partner` — Contact

| Field Name | Type | Label (string) | Description |
|---|---|---|---|
| `client_location` | Selection (`local`, `foreigner`) | *(no explicit string set — defaults to field name)* | Classifies the contact/delivery address as Local or Foreigner. Visible and required only when the partner type is `delivery`. |

**Key methods:**
- No custom methods defined; field addition only.

---

### `sale.order` — Sales Order

| Field Name | Type | Label (string) | Description |
|---|---|---|---|
| `client_location` | Selection (related) | *(no explicit string set — defaults to field name)* | Related field from `partner_shipping_id.client_location`. Stored in the database for filtering/grouping purposes. |

**Key methods:**
- No custom methods defined; related field propagation only.

---

### `stock.picking` — Transfer

| Field Name | Type | Label (string) | Description |
|---|---|---|---|
| `client_location` | Selection (related) | *(no explicit string set — defaults to field name)* | Related field from `partner_id.client_location`. Stored in the database for filtering/grouping purposes. |

**Key methods:**
- No custom methods defined; related field propagation only.

---

### `stock.move` — Stock Move

| Field Name | Type | Label (string) | Description |
|---|---|---|---|
| `client_location` | Selection (related) | *(no explicit string set — defaults to field name)* | Related field from `partner_id.client_location`. Stored in the database for filtering/grouping purposes. |

**Key methods:**
- No custom methods defined; related field propagation only.

---

## Security Groups

No custom security groups or access rules are defined in this module (`security/` directory not present). Access to the new fields follows the existing Odoo access rules for each respective model.

## Menus & Actions

No new menus or actions are introduced by this module. All changes are injected into existing views:

- **Contacts form** (`base.view_partner_form`) — `client_location` field added before the VAT field; visible and required only for delivery address records.
- **Sales Order form** (`sale.view_order_form`) — `client_location` field added after the Payment Terms field.
- **Transfer form** (`stock.view_picking_form`) — `client_location` field added after the Destination Location field.
- **Stock Move form** (`stock.view_move_form`) — `client_location` field added after the Analytic Distribution field.

---

<!-- ============================================================ -->
<!-- SECCIÓN EN ESPAÑOL — Documentación Funcional                 -->
<!-- ============================================================ -->

## Descripción General

Este módulo agrega a Odoo la capacidad de clasificar a los clientes (específicamente sus direcciones de entrega) según su ubicación geográfica: **Local** o **Extranjero**. Esta clasificación se registra directamente en la ficha del contacto y se propaga automáticamente a los documentos relacionados como órdenes de venta, transferencias de almacén y movimientos de inventario.

El propósito principal es que el equipo de logística y ventas pueda identificar rápidamente si un cliente requiere un tratamiento diferente en términos de envío, documentación aduanal u otros procesos internos que dependen de si el destino de la mercancía es nacional o internacional.

Gracias a que el campo se almacena en cada documento, es posible utilizarlo para filtrar, agrupar y generar reportes segmentados por tipo de cliente en toda la cadena desde la venta hasta la entrega física.

## Objetivo de Negocio

- Clasificar las direcciones de entrega de los clientes como **Locales** o **Extranjeras** para facilitar la gestión logística.
- Propagar automáticamente la clasificación del cliente a las órdenes de venta, transferencias y movimientos de inventario, eliminando la captura manual repetitiva.
- Permitir el filtrado y agrupación de documentos por ubicación del cliente en módulos de ventas e inventario.
- Apoyar procesos diferenciados de entrega o documentación según el destino de la mercancía (nacional vs. internacional).
- Garantizar que en toda dirección de tipo "Entrega" se registre obligatoriamente la clasificación, evitando omisiones.

## Flujos de Negocio Principales

### Flujo 1: Registro de la ubicación del cliente en la dirección de entrega

**Descripción:** Este flujo se activa cuando se crea o edita una dirección de entrega en la ficha de un contacto. El usuario debe indicar si el cliente es Local o Extranjero, información que servirá como base para los documentos posteriores.

**Pasos:**
1. El usuario navega al menú **Contactos** y abre o crea un registro de cliente.
2. Agrega o edita una dirección de tipo **Entrega** (dentro de la pestaña de contactos del formulario).
3. En el formulario de la dirección de entrega, aparece el campo **Client Location** antes del campo de RFC/NIF.
4. El usuario selecciona **Local** o **Foreigner** (Extranjero). Este campo es obligatorio para las direcciones de tipo entrega.
5. Guarda el registro.

**Reglas de negocio importantes:**
- El campo **Client Location** solo es visible cuando el tipo de contacto es **Entrega** (`type == 'delivery'`).
- El campo es **obligatorio** para registros de tipo entrega; no se puede guardar una dirección de entrega sin esta clasificación.

---

### Flujo 2: Propagación automática de la clasificación a la orden de venta

**Descripción:** Cuando se crea una orden de venta y se selecciona una dirección de envío, la clasificación de ubicación del cliente se copia automáticamente a la orden, sin intervención del usuario.

**Pasos:**
1. El usuario crea una nueva **Orden de Venta** desde el menú de Ventas.
2. Selecciona el cliente y la **Dirección de Envío** correspondiente.
3. El campo **Client Location** en la orden de venta se actualiza automáticamente con el valor registrado en la dirección de entrega seleccionada.
4. El campo queda visible en el formulario de la orden, después del campo de Términos de Pago.

**Reglas de negocio importantes:**
- El valor proviene directamente del campo `client_location` de la dirección de envío (`partner_shipping_id`).
- Si la dirección de envío no tiene clasificación asignada, el campo en la orden de venta aparecerá vacío.
- El campo se almacena en la base de datos, permitiendo búsquedas y agrupaciones.

---

### Flujo 3: Propagación automática de la clasificación a transferencias y movimientos de inventario

**Descripción:** Cuando se genera una transferencia de almacén (ya sea desde una orden de venta o de forma manual), la clasificación del cliente se propaga automáticamente tanto a la transferencia como a cada uno de sus movimientos de inventario.

**Pasos:**
1. Se confirma una orden de venta o se crea manualmente una **Transferencia** en el módulo de Inventario.
2. El sistema asocia el contacto (partner) a la transferencia.
3. El campo **Client Location** en la transferencia se llena automáticamente tomando el valor del contacto asociado.
4. Cada **Movimiento de Stock** generado hereda igualmente la clasificación desde su contacto vinculado.
5. El campo es visible en el formulario de la transferencia (después de **Ubicación de Destino**) y en el formulario del movimiento de stock (después de **Distribución Analítica**).

**Reglas de negocio importantes:**
- El campo en transferencias proviene de `partner_id.client_location` del contacto de la transferencia.
- El campo en movimientos de stock proviene de `partner_id.client_location` del contacto del movimiento.
- Ambos campos se almacenan en base de datos para su uso en reportes y filtros.

---

## Guía de Configuración

1. **Instalar el módulo** siguiendo los pasos de la sección de instalación.
2. Navegar a **Contactos** en el menú principal de Odoo.
3. Para cada cliente que tenga entregas clasificadas, abrir su ficha y localizar las direcciones de tipo **Entrega**.
4. En cada dirección de entrega, asignar el valor correcto en el campo **Client Location**: **Local** para clientes nacionales, **Foreigner** para clientes internacionales.
5. Verificar que las **Órdenes de Venta** existentes o nuevas reflejen correctamente la clasificación al seleccionar la dirección de envío.
6. Verificar en **Inventario → Transferencias** que las transferencias generadas muestren el campo correctamente.

> **Advertencia:** Las direcciones de entrega existentes que no tengan el campo configurado mostrarán el valor vacío en órdenes de venta y transferencias hasta que se actualicen manualmente en la ficha del contacto.

---

## Campos y Pantallas Clave

### Contacto (Dirección de Entrega)

| Campo en pantalla | Para qué sirve | Valores posibles / Notas |
|---|---|---|
| Client Location | Clasifica al cliente/dirección de entrega según su ubicación geográfica | **Local** (cliente nacional) / **Foreigner** (cliente extranjero). Solo visible y obligatorio cuando el tipo de dirección es "Entrega". |

### Orden de Venta

| Campo en pantalla | Para qué sirve | Valores posibles / Notas |
|---|---|---|
| Client Location | Muestra la clasificación de ubicación del cliente de envío vinculado a la orden | **Local** / **Foreigner**. Se llena automáticamente desde la dirección de envío. Solo lectura en la práctica (campo relacionado). |

### Transferencia

| Campo en pantalla | Para qué sirve | Valores posibles / Notas |
|---|---|---|
| Client Location | Indica si el destinatario de la transferencia es local o extranjero | **Local** / **Foreigner**. Se llena automáticamente desde el contacto de la transferencia. |

### Movimiento de Stock

| Campo en pantalla | Para qué sirve | Valores posibles / Notas |
|---|---|---|
| Client Location | Clasifica el movimiento de inventario según la ubicación del contacto asociado | **Local** / **Foreigner**. Se llena automáticamente desde el contacto del movimiento. |

---

## Automatizaciones y Reglas

- **Propagación de Client Location a Orden de Venta:** Se ejecuta automáticamente cuando se selecciona o cambia la dirección de envío en una orden de venta. Resultado: el campo `Client Location` de la orden refleja el valor de la dirección de entrega seleccionada.
- **Propagación de Client Location a Transferencia:** Se ejecuta automáticamente cuando se asocia un contacto a una transferencia de inventario. Resultado: el campo `Client Location` de la transferencia refleja el valor del contacto.
- **Propagación de Client Location a Movimiento de Stock:** Se ejecuta automáticamente cuando se asocia un contacto a un movimiento de inventario. Resultado: el campo `Client Location` del movimiento refleja el valor del contacto.

---

## Preguntas Frecuentes (FAQ)

**P: ¿En qué parte del formulario de contacto aparece el campo Client Location?**
R: Aparece dentro de la ficha del contacto, en las direcciones de tipo "Entrega", específicamente antes del campo de RFC/NIF. No es visible en el formulario principal del contacto ni en otros tipos de dirección (facturación, contacto, etc.).

**P: ¿Es obligatorio llenar el campo Client Location en todas las direcciones?**
R: No, solo es obligatorio en las direcciones de tipo **Entrega**. Para otros tipos de contacto el campo no aparece y no es requerido.

**P: ¿Qué pasa si no lleno el campo Client Location en una dirección de entrega?**
R: Odoo no permitirá guardar la dirección de entrega sin ese campo. Es un campo requerido para ese tipo de registro, por lo que el sistema mostrará un error de validación si se intenta guardar sin seleccionar un valor.

**P: ¿Puedo modificar manualmente el campo Client Location en una orden de venta o transferencia?**
R: No directamente. El campo en la orden de venta y en las transferencias es un campo relacionado (read-only en su origen), lo que significa que su valor depende del contacto asociado. Para cambiarlo, se debe actualizar el valor en la ficha del contacto (dirección de entrega).

**P: ¿El campo Client Location aparece en las vistas de lista o solo en el formulario?**
R: Según la configuración actual del módulo, el campo se agrega únicamente a las vistas de formulario. Sin embargo, al estar almacenado en la base de datos (`store=True`), es posible agregarlo manualmente a vistas de lista o usarlo como filtro/grupo en las búsquedas personalizadas.

**P: ¿Qué sucede con las órdenes de venta o transferencias que ya existían antes de instalar el módulo?**
R: Los documentos existentes mostrarán el campo vacío hasta que se actualice la clasificación en las fichas de los contactos correspondientes. Los documentos nuevos tomarán el valor automáticamente desde el contacto.

**P: ¿Este módulo distingue entre múltiples tipos de cliente extranjero (por país)?**
R: No. El módulo únicamente ofrece dos clasificaciones: **Local** y **Foreigner**. No hay subdivisión por país o región. Si se requiere mayor granularidad, se necesitaría una personalización adicional.

---

<!-- ============================================================ -->
<!-- NOTEBOOKLM TRAINING SECTION                                  -->
<!-- ============================================================ -->

## 🤖 Contexto para Asistente IA

> Esta sección está optimizada para el entrenamiento del asistente de IA del cliente.

**¿Qué hace este módulo en una oración?**
Agrega un campo de clasificación de ubicación del cliente (Local o Extranjero) en las direcciones de entrega de los contactos y lo propaga automáticamente a órdenes de venta, transferencias de inventario y movimientos de stock.

**Palabras clave asociadas a este módulo:**
- Client Location
- Local
- Extranjero / Foreigner
- Dirección de entrega
- Clasificación de cliente
- Orden de venta
- Transferencia
- Movimiento de inventario
- Contacto
- Dirección de envío
- Logística
- Cliente nacional
- Cliente internacional
- Campo relacionado
- Inventario

**Casos de uso típicos:**
1. "¿Cómo marco a un cliente como extranjero en Odoo?"
2. "¿Por qué el campo Client Location no aparece en la ficha del contacto principal?"
3. "¿Cómo sé si una orden de venta es para un cliente local o extranjero?"
4. "¿Por qué la transferencia no muestra el tipo de cliente?"
5. "Quiero filtrar mis transferencias por clientes locales, ¿es posible?"
6. "El campo Client Location aparece vacío en mis órdenes de venta, ¿qué debo revisar?"
7. "¿Dónde configuro si un cliente es local o extranjero?"
8. "¿El campo de ubicación del cliente se llena solo o tengo que capturarlo en cada documento?"

**Lo que este módulo NO hace:**
- No genera documentos aduanales ni gestiona trámites de exportación/importación.
- No clasifica clientes por país específico ni por región; solo distingue entre Local y Extranjero.
- No modifica reglas de precio, impuestos ni términos de pago según la clasificación del cliente.
- No incluye reportes predefinidos; el campo está disponible para usarse en reportes o filtros personalizados.

---

- Models documented: 4
- Total fields documented: 4
- Business flows identified: 3
- FAQ questions generated: 7
- Sections omitted: Reports, Controllers / API Endpoints, Wizards
<!-- odoo-docs: last-commit=8e71b5dbe6264665fc32329f2b4a2ff809c24057 | updated=2026-05-11 -->
