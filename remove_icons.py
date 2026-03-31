import os

views_path = 'views'
for filename in os.listdir(views_path):
    if filename.endswith('.py'):
        filepath = os.path.join(views_path, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Eliminar líneas con setIcon
        lines = content.split('\n')
        new_lines = []
        for line in lines:
            if 'setIcon(QMessageBox.' not in line:
                new_lines.append(line)
        
        new_content = '\n'.join(new_lines)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f'Procesado: {filename}')

print('Todos los iconos eliminados!')
