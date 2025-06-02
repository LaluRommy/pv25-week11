import sys
import sqlite3
import csv
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, 
                            QTableWidgetItem, QTableWidget, QMessageBox, QFileDialog, QInputDialog, QFormLayout,
                            QScrollArea, QDockWidget)
from PyQt5.QtCore import Qt

class task11(QMainWindow):
    def __init__(self):
        super().__init__()
        self.statusBar().showMessage("Lalu Rommy Rahmad Amarta Putra - F1D022058")
        self.setWindowTitle("Lalu Rommy Rahmad Amarta Putra - F1D022058")
        self.setGeometry(100, 100, 600,400)
        self.initUI()
        self.createDB()
        self.loadData()
        
    def initUI(self):
        widget = QWidget()
        self.setCentralWidget(widget)
        layout = QVBoxLayout()

        form_container = QWidget()
        form_layout = QFormLayout(form_container)

        self.name_input = QLineEdit()
        self.role_input = QLineEdit()
        self.age_input = QLineEdit()
        self.region_input = QLineEdit()

        clipboard_btn = QPushButton("Paste from Clipboard")
        clipboard_btn.clicked.connect(self.pasteFromClipboard)

        name_layout = QHBoxLayout()
        name_layout.addWidget(self.name_input)
        name_layout.addWidget(clipboard_btn)

        form_layout.addRow("Name: ", name_layout)
        form_layout.addRow("Role: ", self.role_input)
        form_layout.addRow("Age: ", self.age_input)
        form_layout.addRow("Region: ", self.region_input)

        self.save_btn = QPushButton("Simpan")
        self.save_btn.clicked.connect(self.saveData)
        form_layout.addRow(self.save_btn)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(form_container)

        layout.addWidget(scroll_area)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "Name", "Role", "Age", "Region"])
        self.table.cellDoubleClicked.connect(self.editData)
        layout.addWidget(self.table)

        self.delete_btn = QPushButton("Hapus Data")
        self.delete_btn.clicked.connect(self.deleteData)
        layout.addWidget(self.delete_btn)

        widget.setLayout(layout)

        self.initDockWidget()
        
    def initDockWidget(self):
        dock = QDockWidget("Search", self)
        dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        dock.setFeatures(QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetFloatable)

        search_widget = QWidget()
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by name....")
        self.search_input.textChanged.connect(self.searchData)
        self.export_btn = QPushButton("Export to CSV")
        self.export_btn.clicked.connect(self.exportCSV)

        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.export_btn)
        search_widget.setLayout(search_layout)

        dock.setWidget(search_widget)
        self.addDockWidget(Qt.RightDockWidgetArea, dock)
        
    def pasteFromClipboard(self):
        clipboard = QApplication.clipboard()
        self.name_input.setText(clipboard.text())
        
    def createDB(self):
        self.conn = sqlite3.connect("data.db")
        self.c = self.conn.cursor()
        self.c.execute("""
            CREATE TABLE IF NOT EXISTS records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                role TEXT,
                age INTEGER,
                region TEXT
            )
        """)
        self.conn.commit()
    
    def saveData(self):
        name = self.name_input.text()
        role = self.role_input.text()
        age = self.age_input.text()
        region = self.region_input.text()

        if not (name and role and age.isdigit() and region):
            QMessageBox.warning(self, "Input Error", "Please fill all fields correctly.")
            return

        self.c.execute("INSERT INTO records (name, role, age, region) VALUES (?, ?, ?, ?)",
                       (name, role, int(age), region))
        self.conn.commit()
        self.clearInputs()
        self.loadData()
        
    def loadData(self):
        self.table.setRowCount(0)
        for row_idx, row_data in enumerate(self.c.execute("SELECT * FROM records")):
            self.table.insertRow(row_idx)
            for col_idx, item in enumerate(row_data):
                self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(item)))
                
    def searchData(self):
        query = self.search_input.text()
        self.table.setRowCount(0)
        for row_idx, row_data in enumerate(
                self.c.execute("SELECT * FROM records WHERE name LIKE ?", ('%' + query + '%',))):
            self.table.insertRow(row_idx)
            for col_idx, item in enumerate(row_data):
                self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(item)))

    def deleteData(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Selection Error", "No row selected.")
            return
        record_id = int(self.table.item(row, 0).text())
        self.c.execute("DELETE FROM records WHERE id = ?", (record_id,))
        self.conn.commit()
        self.loadData()

    def editData(self, row):
        record_id = int(self.table.item(row, 0).text())
        name, role, age, region = [self.table.item(row, i).text() for i in range(1, 5)]

        name, ok = QInputDialog.getText(self, "Edit Name", "Name:", text=name)
        if not ok: return
        role, ok = QInputDialog.getText(self, "Edit Role", "Role:", text=role)
        if not ok: return
        age, ok = QInputDialog.getText(self, "Edit Age", "Age:", text=age)
        if not ok or not age.isdigit(): return
        region, ok = QInputDialog.getText(self, "Edit Region", "Region:", text=region)
        if not ok: return

        self.c.execute("""
            UPDATE records SET name = ?, role = ?, age = ?, region = ? WHERE id = ?
        """, (name, role, int(age), region, record_id))
        self.conn.commit()
        self.loadData()

    def exportCSV(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save CSV", "data.csv", "CSV files (*.csv)")
        if path:
            with open(path, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(["ID", "Name", "Role", "Age", "Region"])
                for row in self.c.execute("SELECT * FROM records"):
                    writer.writerow(row)
            QMessageBox.information(self, "Export Berhasil", "Data berhasil diekspor!")

    def clearInputs(self):
        self.name_input.clear()
        self.role_input.clear()
        self.age_input.clear()
        self.region_input.clear()

    def closeEvent(self, event):
        self.conn.close()
        event.accept()
        
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = task11()
    window.show()
    sys.exit(app.exec())
