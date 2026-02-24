# -*- coding: utf-8 -*-
{
  'name': 'Comparsa',
  'summary': 'Gestión de la comparsa Marineros de Ontinyent',
  'description': '''
Módulo de gestión interna para la comparsa Marineros de Ontinyent.

Funcionalidades principales:
- Gestión de comparsistas: alta, baja, régimen de cuotas y asignación
- Asignación de cargos a los comparsistas
- Eventos: festeros, comidas y actos internos, con control de precios y modo de inscripción
- Inscripciones a eventos con control de permisos por régimen
- Cuotas periódicas (mensual/anual) y de evento, con seguimiento de pagos
- Gestión de escuadras y su participación en los eventos
- Integración con la contabilidad de Odoo: generación de facturas y sincronización de estado de cobro
''',
  'author': 'Francisco Montés Doria',
  'website': '',
  # En la siguiente URL se indica que categorías pueden usarse
  # https://github.com/odoo/odoo/blob/17.0/odoo/addons/base/data/ir_module_category_data.xml
  'category': 'Extra Tools',
  # Convenio de versión: <versión_odoo>.<mayor>.<menor>.<parche>
  'version': '19.0.1.0.0',
  'application': True,
  'installable': True,
  # Indicamos lista de módulos necesarios para que este funcione correctamente
  'depends': ['base', 'account'],
  # Carga los archivos para la política de seguridad (grupos y accesos) y las vistas
  'data': [
    # Seguridad — grupos primero, después accesos
    'security/res_groups.xml',
    'security/ir.model.access.csv',
    # Vistas
    'views/comparsa_menus.xml',
    'views/comparsa_member_views.xml',
    'views/comparsa_squad_views.xml',
    'views/comparsa_regime_views.xml',
    'views/comparsa_role_views.xml',
    'views/comparsa_role_assignment_views.xml',
    'views/comparsa_event_views.xml',
    'views/comparsa_event_category_views.xml',
    'views/comparsa_event_registration_views.xml',
    'views/comparsa_squad_event_views.xml',
  ],
  'assets': {
    'web.assets_backend': [
      'comparsa/static/src/css/comparsa.css',
      'comparsa/static/src/js/calendar_popover_patch.js',
    ],
  },
}
