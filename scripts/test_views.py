import sys
sys.path.append(r'c:/Users/katri/OneDrive/Documentos/KyoGym')
from importlib import import_module
mods = ['views.inventario_view','views.clientes_view','views.pagos_view','views.membresias_view']
for m in mods:
    import_module(m)
    print(f'Imported {m}')
print('ALL_OK')
