

class ExpenseManager:
    """Handles expense data and calculations."""
    def __init__(self , cursor , conn ):
        # let's start by connecting to the database 
        self.cursor = cursor 
        self.conn = conn 
        self.cursor.execute ("CREATE TABLE IF NOT EXISTS expenses ( expense TEXT,Price INTEGER , month INTEGER , day INTEGER , year INTEGER)")

    def add_expense(self, name, price , day , month ,year ):
        """Adds an expense to the list and returns the updated total."""
        self.cursor.execute ("INSERT INTO expenses (expense , Price , day , month , year ) VALUES (? ,?,?,?,?)", (name,price, day , month , year ))
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
    def get_by_month (self , month , year ) : 
        """Get The expenses within the month """
        self.cursor.execute ("SELECT * from expenses WHERE year = ? AND month = ? " , (year , month))
        return self.cursor.fetchall()
    
    def get_by_year (self , year ) : 
        """Get the expenses within the year """
        self.cursor.execute ("SELECT * from expenses WHERE year = ? " , (year,))
        return self.cursor.fetchall() 

