# Comparsa — Módulo Odoo 19

Módulo de gestión interna para la comparsa **Los Marineros** de Ontinyent.

## Funcionalidades

- **Socios**: alta, baja, régimen de cuotas y asignación
- **Organización**: escuadras, cargos y asignación de cargos
- **Eventos**: festeros, comidas y actos internos, con control de precios y modo de inscripción
- **Inscripciones**: control de permisos por régimen de socio
- **Cuotas**: periódicas (mensual/anual) y por evento, con seguimiento de pagos

## Requisitos

- Odoo 19
- Módulo base de Odoo (sin dependencias adicionales)

## Instalación

1. Copiar la carpeta `comparsa/` dentro del directorio `addons` de tu instancia Odoo
2. Activar el modo desarrollador en Odoo
3. Ir a **Aplicaciones → Actualizar lista de aplicaciones**
4. Buscar `Comparsa` e instalar

## Estructura

```
comparsa/
├── models/          # Modelos de datos
├── security/        # Grupos de acceso y reglas de permisos
├── views/           # Vistas (pendiente)
├── __init__.py
└── __manifest__.py
```

## Grupos de seguridad

| Grupo         | Descripción                                              |
|---------------|----------------------------------------------------------|
| Gestor        | CRUD en modelos operacionales; lectura en catálogos      |
| Administrador | Todo lo anterior + CRUD completo en catálogos de configuración |

## Autor

Francisco Montés Doria
