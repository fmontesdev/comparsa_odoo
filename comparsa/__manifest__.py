# -*- coding: utf-8 -*-
{
  'name': 'Comparsa',
  'summary': 'Gestión de la comparsa de Moros i Cristians',
  'description': '''
Módulo de gestión interna para la comparsa Los Marineros de Ontinyent.

Funcionalidades principales:
- Gestión de socios: alta, baja, régimen de cuotas y asignación
- Asignación de cargos y roles a los socios
- Eventos: festeros, comidas y actos internos, con control de precios y modo de inscripción
- Inscripciones a eventos con control de permisos por régimen
- Cuotas periódicas (mensual/anual) y de evento, con seguimiento de pagos
- Gestión de escuadras y su participación en los eventos
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
  'depends': ['base'],
  # Carga los archivos para la política de seguridad (grupos y accesos) y las vistas
  'data': [
  ],
}
