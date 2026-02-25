# 🎭 Comparsa — Módulo Odoo 19

> Módulo de gestión interna para la comparsa **Marineros** de Ontinyent.

---

## 📋 Requisitos

- Odoo 19 Community
- Módulos Odoo: `base`, `account`, `l10n_es`

---

## 🚀 Instalación

1. Copiar la carpeta `comparsa/` dentro del directorio `addons` de la instancia Odoo
2. Actualizar el módulo desde CLI para que se ejecute la migración de esquema:
   ```bash
   odoo -u comparsa -d <base_de_datos> --stop-after-init
   ```
3. Reiniciar el servidor Odoo
4. Alternativamente, desde la UI: activar modo desarrollador → **Aplicaciones → Actualizar lista → Buscar "Comparsa" → Instalar**

---

## 🗂️ Estructura

```
comparsa/
├── data/
│   └── comparsa_cron.xml               # Cron mensual de generación de cuotas
├── models/
│   ├── comparsa_member.py              # Comparsista (herencia delegada de res.partner)
│   ├── comparsa_regime.py              # Régimen de cuotas
│   ├── comparsa_squad.py               # Escuadra
│   ├── comparsa_role.py                # Cargo
│   ├── comparsa_role_assignment.py     # Asignación de cargo a miembro
│   ├── comparsa_event.py               # Acto
│   ├── comparsa_event_category.py      # Categoría de acto
│   ├── comparsa_event_registration.py  # Inscripción a un acto
│   ├── comparsa_event_guest.py         # Invitado en una inscripción
│   ├── comparsa_squad_event.py         # Logística de escuadra en un acto
│   ├── comparsa_charge.py              # Cobro / cuota
│   ├── comparsa_charge_type.py         # Tipo de cobro
│   ├── comparsa_charge_line.py         # Línea de desglose de un cobro
│   ├── comparsa_account_move.py        # Extensión de account.move (sincronización de estado)
│   └── comparsa_res_partner.py         # Extensión de res.partner (bandas, restaurantes)
├── security/
│   ├── res_groups.xml                  # Grupos de seguridad
│   └── ir.model.access.csv             # Reglas de acceso por modelo
├── static/
│   └── src/
│       ├── css/comparsa.css
│       └── js/calendar_popover_patch.js
├── views/
│   ├── comparsa_member_views.xml
│   ├── comparsa_regime_views.xml
│   ├── comparsa_squad_views.xml
│   ├── comparsa_role_views.xml
│   ├── comparsa_role_assignment_views.xml
│   ├── comparsa_event_views.xml
│   ├── comparsa_event_category_views.xml
│   ├── comparsa_event_registration_views.xml
│   ├── comparsa_squad_event_views.xml
│   ├── comparsa_charge_views.xml
│   ├── comparsa_charge_type_views.xml
│   ├── comparsa_charge_generation_wizard_views.xml
│   └── comparsa_menus.xml
└── wizards/
    └── comparsa_charge_generation_wizard.py  # Wizard de generación manual de cuotas
```

---

## ⚙️ Modelos y funcionalidades

### 👤 Miembros (`comparsa.member`)
Herencia delegada sobre `res.partner`. Cada miembro es también un contacto de Odoo.

| Campo | Descripción |
|---|---|
| `regime_type_id` | Régimen de cuotas asignado |
| `payment_plan` | Plan de pago: mensual o anual |
| `squad_id` | Escuadra a la que pertenece |
| `role_assignment_ids` | Cargos asignados |
| `active` | Alta/baja en la comparsa |

---

### 📄 Regímenes (`comparsa.member.regime.type`)
Catálogo configurable de regímenes. Define las cuotas y los permisos de asistencia por defecto.

| Campo | Descripción |
|---|---|
| `monthly_amount` | Cuota mensual |
| `yearly_amount` | Cuota anual |
| `allow_festive_by_default` | Permite asistir a actos festivos por defecto |
| `allow_meal_by_default` | Permite asistir a comidas por defecto |
| `allow_internal_by_default` | Permite asistir a actos internos por defecto |
| `allowed_event_ids` | Excepciones: actos permitidos puntualmente fuera del régimen |

---

### 🪖 Escuadras (`comparsa.squad`)
Agrupación de miembros dentro de la comparsa.

---

### 🏅 Cargos (`comparsa.role`) y asignaciones (`comparsa.role.assignment`)
Catálogo de cargos de la comparsa y su asignación temporal a miembros, con fecha de inicio y fin.

---

### 📅 Actos (`comparsa.event`)
Representa cualquier acto de la comparsa: festivos, comidas o internos.

| Campo | Descripción |
|---|---|
| `event_category_id` | Categoría del acto (define su tipo) |
| `event_type` | Calculado: `festive`, `meal`, `internal` |
| `date` | Fecha y hora del acto |
| `registration_mode` | Control de quién puede inscribirse: solo miembros, con niños, con invitados o abierto |
| `pricing_mode` | Gratuito o precio fijo |
| `price_member / price_guest / price_children` | Precios por tipo de asistente |
| `restaurant_partner_id` | Solo para comidas: restaurante donde se celebra |
| `menu` | Descripción del menú (solo comidas) |

> ⚠️ Las validaciones garantizan la coherencia entre modo de inscripción, modo de precio y precios definidos.

---

### 📝 Inscripciones (`comparsa.event.registration`)
Registro de asistencia de un miembro a un acto.

| Campo | Descripción |
|---|---|
| `member_id` | Miembro que se inscribe |
| `with_partner` | Asiste con pareja |
| `num_children` | Número de niños a cargo |
| `guest_ids` | Invitados (personas externas a la comparsa) |
| `state` | `confirmed` / `cancelled` |
| `charge_id` | Cobro generado automáticamente al inscribirse |

**Reglas de negocio:**
- ✅ Al crear una inscripción en un acto de precio fijo, se genera automáticamente un cobro con las líneas correspondientes (miembro, pareja, niños, invitados)
- 🔒 Una inscripción con cobro generado **no puede modificarse** (miembro, pareja, niños ni invitados). Hay que cancelar primero el cobro
- ❌ Al cancelar la inscripción, se cancela el cobro si está pendiente; bloquea si ya está facturado o pagado
- 🚫 Un miembro no puede tener dos inscripciones activas en el mismo acto
- 🔑 Los permisos de asistencia se validan según el régimen del miembro

---

### 🙋 Invitados (`comparsa.event.guest`)
Personas externas a la comparsa que asisten a un acto como invitados de un miembro. Se vinculan a un contacto `res.partner` que no sea empresa, ni banda, ni restaurante, ni miembro de la comparsa.

---

### 🥁 Logística de escuadras (`comparsa.squad.event`)
Asignación de escuadras a actos festivos, con la banda de música contratada.

---

### 💶 Cobros (`comparsa.charge`)
Representa cualquier cobro a un miembro: cuota mensual, cuota anual o cuota de acto.

| Campo | Descripción |
|---|---|
| `charge_type_id` | Tipo de cobro (catálogo) |
| `period_key` | Clave de periodo: `YYYY-MM` (mensual), `YYYY` (anual) |
| `line_ids` | Líneas de desglose |
| `amount_total` | Total calculado de las líneas |
| `state` | `pending` → `invoiced` → `partial` / `paid` / `cancelled` |
| `invoice_id` | Factura de Odoo asociada |

El estado del cobro se sincroniza automáticamente con el estado de pago de la factura mediante override de `_compute_payment_state`. Si se cancela o elimina la factura, el cobro vuelve a `pending`.

**Códigos de tipo de cobro reservados:**

| Código | Uso |
|---|---|
| `CUOTA_MES` | Cuota mensual periódica |
| `CUOTA_ANO` | Cuota anual periódica |
| `ACTO` | Cuota de inscripción a un acto |

---

### 🔄 Generación de cuotas periódicas

- **⏰ Cron automático:** Se ejecuta el día 1 de cada mes. En septiembre genera tanto la cuota mensual como la anual.
- **🧙 Wizard manual:** Menú **Cobros → Generar cuotas**. Permite seleccionar mes, año y tipo (mensual, anual o ambas). Muestra el número de cobros creados y omitidos (por duplicado).

> La generación omite miembros que ya tienen el cobro del periodo, evitando duplicados.

---

### 🏢 Contactos externos (`res.partner` extendido)

El campo `comparsa_partner_type` clasifica los partners externos relevantes para la comparsa:

| Valor | Descripción |
|---|---|
| `band` 🎺 | Banda de música contratada para actos festivos |
| `restaurant` 🍽️ | Restaurante para comidas |

Accesibles desde el menú **Configuración → Bandas de Música / Restaurantes**.

---

## 🧭 Menús

| Menú | Submenús |
|---|---|
| 👤 **Miembros** | Miembros, Escuadras, Regímenes, Cargos, Asignaciones de cargos |
| 📅 **Actos** | Actos, Categorías, Logística de escuadras, Inscripciones, Invitados |
| 💶 **Cobros** | Cobros, Generar cuotas, Tipos de cobro |
| ⚙️ **Configuración** | Bandas de música, Restaurantes |

---

## 🔐 Seguridad

Actualmente todos los modelos usan el grupo estándar `base.group_user` (cualquier usuario interno de Odoo) con permisos completos de lectura, escritura, creación y eliminación. La diferenciación por roles (Gestor / Administrador) está pendiente de implementar.

---

## ✍️ Autor

**Francisco Montés Doria**
