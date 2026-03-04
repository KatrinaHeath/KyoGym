from __future__ import annotations

from PySide6.QtWidgets import QTableWidget


def limpiar_tabla(tabla: QTableWidget) -> None:
    """Limpia items y widgets embebidos (setCellWidget) sin tocar headers.

    En QTableWidget, los widgets insertados con setCellWidget pueden quedarse
    vivos (y pintándose) después de recargas/CRUD si no se retiran explícitamente.
    Eso produce texto/iconos duplicados o superpuestos.
    """
    tabla.setUpdatesEnabled(False)
    try:
        rows = tabla.rowCount()
        cols = tabla.columnCount()
        for r in range(rows):
            for c in range(cols):
                w = tabla.cellWidget(r, c)
                if w is None:
                    continue
                tabla.removeCellWidget(r, c)
                w.hide()
                w.setParent(None)
                w.deleteLater()

        tabla.clearContents()
        tabla.setRowCount(0)
    finally:
        tabla.setUpdatesEnabled(True)
