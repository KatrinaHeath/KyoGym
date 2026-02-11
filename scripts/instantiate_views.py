import sys
sys.path.append(r'c:/Users/katri/OneDrive/Documentos/KyoGym')
from PySide6.QtWidgets import QApplication
import importlib, traceback
app = QApplication([])
mods = [
    ('DashboardView','views.dashboard_view','DashboardView'),
    ('MembresiasView','views.membresias_view','MembresiasView'),
    ('ClientesView','views.clientes_view','ClientesView'),
    ('PagosView','views.pagos_view','PagosView'),
    ('InventarioView','views.inventario_view','InventarioView'),
]
for name, module, cls in mods:
    try:
        m = importlib.import_module(module)
        C = getattr(m, cls)
        print(f'Instantiating {name}...')
        w = C()
        print(f'{name} instantiated OK')
    except Exception as e:
        print(f'Exception while instantiating {name}:', e)
        traceback.print_exc()
print('Done')
