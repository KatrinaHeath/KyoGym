from PySide6.QtCore import Qt


def aplicar_estilo_tabla_moderna(tabla, compacta=False, embebida=False):
    tabla.setAlternatingRowColors(True)
    tabla.setShowGrid(False)
    tabla.setMouseTracking(True)
    tabla.verticalHeader().setVisible(False)
    tabla.verticalHeader().setMinimumSectionSize(52)
    tabla.verticalHeader().setDefaultSectionSize(44 if compacta else 52)

    header = tabla.horizontalHeader()
    header.setDefaultAlignment(Qt.AlignLeft | Qt.AlignVCenter)
    header.setMinimumHeight(38 if compacta else 42)
    header.setSortIndicatorShown(True)
    header.setHighlightSections(False)

    borde = "none" if embebida else "1px solid #d9e0ea"
    radio = "0px" if embebida else "10px"

    tabla.setStyleSheet(f"""
        QTableWidget {{
            background-color: #ffffff;
            border: {borde};
            border-radius: {radio};
            font-size: 13px;
            color: #1a1a1a;
            alternate-background-color: #f9f9f9;
            outline: 0;
            gridline-color: #eeeeee;
        }}
        QTableWidget::item {{
            border: none;
            border-bottom: 1px solid #eeeeee;
            padding: 10px 12px;
            color: #1a1a1a;
        }}
        QTableWidget::item:hover {{
            background-color: #f0f0f0;
        }}
        QTableWidget::item:selected {{
            background-color: #e0e0e0;
            color: #1a1a1a;
        }}
        QHeaderView::section {{
            background-color: #2c2c2c;
            color: #ffffff;
            border: none;
            border-bottom: 1px solid #1a1a1a;
            border-right: 1px solid #3a3a3a;
            padding: 10px 12px;
            font-size: 12px;
            font-weight: 700;
        }}
        QTableCornerButton::section {{
            background-color: #2c2c2c;
            border: none;
            border-bottom: 1px solid #1a1a1a;
        }}
        QScrollBar:vertical {{
            background: #f5f5f5;
            width: 10px;
            border: none;
            border-radius: 5px;
        }}
        QScrollBar::handle:vertical {{
            background: #c0c0c0;
            min-height: 24px;
            border-radius: 5px;
        }}
        QScrollBar::handle:vertical:hover {{
            background: #a0a0a0;
        }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0px;
        }}
        QScrollBar:horizontal {{
            background: #f5f5f5;
            height: 10px;
            border: none;
            border-radius: 5px;
        }}
        QScrollBar::handle:horizontal {{
            background: #c0c0c0;
            min-width: 24px;
            border-radius: 5px;
        }}
        QScrollBar::handle:horizontal:hover {{
            background: #a0a0a0;
        }}
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
            width: 0px;
        }}
    """)