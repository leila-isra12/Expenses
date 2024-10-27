class ExpenseManager:
    """Handles expense data and calculations."""
    def __init__(self, cursor, conn):
        self.cursor = cursor
        self.conn = conn
        # Create the table if it doesn't exist
        self.cursor.execute("CREATE TABLE IF NOT EXISTS expenses (expense TEXT, Price REAL)")
        self.conn.commit()

    def add_expense(self, name, price):
        """Adds an expense to the list and returns the updated total."""
        self.cursor.execute("INSERT INTO expenses (expense, Price) VALUES (?, ?)", (name, price))
        self.conn.commit()
        return self.calculate_total()

    def calculate_total(self):
        """Calculates the total price of all expenses."""
        self.cursor.execute("SELECT SUM(Price) FROM expenses")
        total = self.cursor.fetchone()[0]
        return total if total is not None else 0

    def fetch_all_expenses(self):
        """Fetches all expenses from the expenses table."""
        self.cursor.execute("SELECT * FROM expenses")
        return self.cursor.fetchall()

    def delete_expense(self, name):
        """Deletes an expense from the list based on its name."""
        self.cursor.execute("DELETE FROM expenses WHERE expense = ?", (name,))
        self.conn.commit()
