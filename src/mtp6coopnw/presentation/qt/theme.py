APP_STYLESHEET = """
QMainWindow, QWidget {
    background: #f5f7fa;
    color: #172033;
    font-family: "Segoe UI", "Noto Sans Thai", sans-serif;
    font-size: 13px;
}
QFrame#Sidebar { background: #111827; border: 0; }
QLabel#Brand { color: white; font-size: 20px; font-weight: 700; padding: 6px 4px 0 4px; }
QLabel#BrandSubtitle { color: #98a2b3; padding: 0 4px 16px 4px; }
QLabel#SidebarFooter { color: #98a2b3; padding: 8px 4px; }
QPushButton#NavButton {
    color: #d1d5db; background: transparent; border: 0; text-align: left;
    padding: 11px 14px; border-radius: 8px;
}
QPushButton#NavButton:hover { background: #1f2937; color: white; }
QPushButton#NavButton:checked { background: #263449; color: white; font-weight: 600; }
QFrame#Card, QFrame#InfoCard {
    background: white; border: 1px solid #e5e7eb; border-radius: 12px;
}
QFrame#InfoCard { border-left: 4px solid #1d4ed8; }
QLabel#CardTitle { color: #667085; font-size: 12px; }
QLabel#CardValue { color: #101828; font-size: 26px; font-weight: 700; }
QLabel#PageTitle { font-size: 24px; font-weight: 700; color: #101828; }
QLabel#PageSubtitle, QLabel#HintText { color: #667085; }
QLabel#HintText { font-size: 11px; }
QTableWidget {
    background: white; border: 1px solid #e5e7eb; border-radius: 10px;
    gridline-color: #eef2f7; selection-background-color: #eff4ff;
    selection-color: #101828;
}
QHeaderView::section {
    background: #f9fafb; color: #475467; padding: 8px; border: 0;
    border-bottom: 1px solid #e5e7eb; font-weight: 600;
}
QLineEdit {
    background: white; border: 1px solid #d0d5dd; border-radius: 8px; padding: 9px 11px;
}
QGroupBox {
    background: white; border: 1px solid #e5e7eb; border-radius: 10px;
    margin-top: 12px; padding: 12px;
}
QGroupBox::title { subcontrol-origin: margin; left: 12px; padding: 0 4px; font-weight: 600; }
QPushButton#PrimaryButton {
    background: #1d4ed8; color: white; border: 0; border-radius: 8px;
    padding: 9px 14px; font-weight: 600;
}
QPushButton#PrimaryButton:disabled { background: #9ca3af; }
QPushButton#SecondaryButton {
    background: white; color: #344054; border: 1px solid #d0d5dd;
    border-radius: 8px; padding: 9px 14px;
}
QCheckBox { spacing: 8px; padding: 3px 0; }
QStatusBar { background: white; border-top: 1px solid #e5e7eb; }
"""
