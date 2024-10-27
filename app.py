import sys
from reportlab.lib.pagesizes import landscape, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
import sqlite3
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QHBoxLayout, QTableWidget, QTableWidgetItem,
    QLineEdit, QLabel, QPushButton, QMenuBar, QMenu, QMessageBox
)
from PyQt5.QtCore import Qt
from expensemanager import ExpenseManager  # Import the ExpenseManager class

# Set up the database connection
conn = sqlite3.connect("expensemanager.db")
cursor = conn.cursor()

class MenuBar(QMenuBar):
    """Creates a menu bar with File, Edit, and Help menus."""
    def __init__(self, parent=None):
        super().__init__(parent)
        file_menu = QMenu("File", self)
        edit_menu = QMenu("Edit", self)
        help_menu = QMenu("Help", self)

        # Adding Generate PDF Report option to the File menu
        self.generate_pdf_action = file_menu.addAction("Generate PDF Report")
        self.addMenu(file_menu)
        self.addMenu(edit_menu)
        self.addMenu(help_menu)

class InputPanel(QWidget):
    """Panel with input fields for expense name and price."""
    def __init__(self):
        super().__init__()
        layout = QHBoxLayout(self)
        
        self.expense_input = QLineEdit()
        self.expense_input.setFixedWidth(150)
        self.price_input = QLineEdit()
        self.price_input.setFixedWidth(100)
        self.add_button = QPushButton("Add Expense")
        self.delete_button = QPushButton("Delete Expense")

        layout.addWidget(QLabel("Expense:"))
        layout.addWidget(self.expense_input)
        layout.addWidget(QLabel("Price:"))
        layout.addWidget(self.price_input)
        layout.addWidget(self.add_button)
        layout.addWidget(self.delete_button)

    def get_inputs(self):
        """Returns the entered expense name and price."""
        return self.expense_input.text().strip(), self.price_input.text().strip()

    def clear_inputs(self):
        """Clears the input fields."""
        self.expense_input.clear()
        self.price_input.clear()

class ExpenseTable(QTableWidget):
    """Displays the expense list in a table format."""
    def __init__(self):
        super().__init__(0, 2)
        self.setHorizontalHeaderLabels(["Expense", "Price"])

    def add_row(self, expense, price):
        """Adds a new row to the table with the given expense and price."""
        row_position = self.rowCount()
        self.insertRow(row_position)
        self.setItem(row_position, 0, QTableWidgetItem(expense))
        self.setItem(row_position, 1, QTableWidgetItem(f"{price:.2f}"))

    def remove_row(self, expense_name):
        """Removes a row with the given expense name."""
        for row in range(self.rowCount()):
            item = self.item(row, 0)
            if item and item.text() == expense_name:
                self.removeRow(row)
                return

class TotalDisplay(QWidget):
    """Displays the total expense."""
    def __init__(self):
        super().__init__()
        layout = QHBoxLayout(self)
        
        self.total_label = QLabel("Total:")
        self.total_value = QLabel("0.00")
        
        layout.addWidget(self.total_label)
        layout.addWidget(self.total_value)

    def update_total(self, total):
        """Updates the displayed total value."""
        self.total_value.setText(f"{total:.2f}")

class ExpenseApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Expense Tracker")
        self.setGeometry(100, 100, 600, 300)

        # Expense data manager
        self.manager = ExpenseManager(cursor, conn)

        # Central widget and layout
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Components
        self.menu_bar = MenuBar(self)
        self.setMenuBar(self.menu_bar)

        self.input_panel = InputPanel()
        self.table = ExpenseTable()
        self.total_display = TotalDisplay()

        # Add PDF export button
        self.export_button = QPushButton("Export to PDF")
        self.export_button.clicked.connect(self.generate_pdf_report)

        # Add components to main layout
        main_layout.addWidget(self.input_panel)
        main_layout.addWidget(self.table)
        main_layout.addWidget(self.total_display)
        main_layout.addWidget(self.export_button)

        # Connect button click to add expense
        self.input_panel.add_button.clicked.connect(self.add_expense)
        self.input_panel.delete_button.clicked.connect(self.delete_expense)

        # Load initial data
        self.load_initial_data()

    def add_expense(self):
        """Method to add an expense."""
        expense = self.input_panel.expense_input.text()
        price = self.input_panel.price_input.text()

        if expense and price:
            try:
                # Insert into the manager (database)
                self.manager.add_expense(expense, float(price))

                # Refresh the table and total display
                self.load_initial_data()
            except ValueError:
                QMessageBox.warning(self, "Input Error", "Please enter a valid price.")
        else:
            QMessageBox.warning(self, "Input Error", "Please fill in all fields.")

    def delete_expense(self):
        """Method to delete an expense."""
        selected_items = self.table.selectedItems()
        if selected_items:
            expense = selected_items[0].text()
            self.manager.delete_expense(expense)

            # Refresh the table and total display
            self.load_initial_data()
        else:
            QMessageBox.warning(self, "Delete Error", "No expense selected.")

    def load_initial_data(self):
        """Load data from the manager (database) into the table."""
        expenses = self.manager.fetch_all_expenses()
        self.table.setRowCount(0)  # Clear the table
        total = 0

        for expense, price in expenses:
            row_position = self.table.rowCount()
            self.table.insertRow(row_position)
            self.table.setItem(row_position, 0, QTableWidgetItem(expense))
            self.table.setItem(row_position, 1, QTableWidgetItem(str(price)))
            total += price

        self.total_display.update_total(total)

    def generate_pdf_report(self):
        """Generates a PDF report of all expenses."""
        expenses = self.manager.fetch_all_expenses()

        pdf_file = "Expense_Report.pdf"
        doc = SimpleDocTemplate(pdf_file, pagesize=landscape(A4))
        elements = []

        style_sheet = getSampleStyleSheet()  # Call the function to get the style sheet
        title = Paragraph("Expense Report", style_sheet['Title'])  # Access the 'Title' style
        elements.append(title)

        # Add a table for the expenses
        data = [["Expense", "Price"]]  # Table header
        data.extend(expenses)  # Add expense rows

        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.gray),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))

        elements.append(table)

        doc.build(elements)

        QMessageBox.information(self, "PDF Report", f"Report saved as {pdf_file}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ExpenseApp()
    window.show()
    sys.exit(app.exec_())
