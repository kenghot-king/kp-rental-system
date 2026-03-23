{
    'name': 'GGG Gantt',
    'category': 'Hidden',
    'summary': 'Gantt chart view for Odoo Community Edition',
    'description': """
GGG Gantt Chart View
====================
Provides a Gantt chart view type for Odoo Community Edition.
Features: drag-drop, resize, dependency connectors, virtual scrolling,
progress bars, unavailability display, and scale selection.
    """,
    'version': '19.0.1.0.0',
    'depends': ['web'],
    'assets': {
        'web._assets_primary_variables': [
            'ggg_gantt/static/src/gantt_view.variables.scss',
        ],
        'web.assets_backend_lazy': [
            'ggg_gantt/static/src/**/*',
        ],
    },
    'auto_install': False,
    'author': 'GGG',
    'license': 'LGPL-3',
}
