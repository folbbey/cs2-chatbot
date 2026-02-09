from util.database import DatabaseConnection

class Economy:
    def __init__(self):
        # Database schema is managed by init.sql
        pass

    def get_balance(self, user_id):
        """Retrieve the balance of a user."""
        with DatabaseConnection() as cursor:
            cursor.execute("""
                SELECT balance
                FROM user_balances
                WHERE user_id = %s
            """, (user_id,))
            result = cursor.fetchone()
        
        # round to nearest 0.01
        if result:
            result = round(float(result[0]), 2)
        else:
            result = 0.0
        return result

    def add_balance(self, user_id, amount):
        """Add an amount to the user's balance."""
        current_balance = self.get_balance(user_id)
        new_balance = round(current_balance + amount, 2)
        
        with DatabaseConnection() as cursor:
            cursor.execute("""
                INSERT INTO user_balances (user_id, balance)
                VALUES (%s, %s)
                ON CONFLICT(user_id) DO UPDATE SET balance = EXCLUDED.balance
            """, (user_id, new_balance))
        
        return new_balance

    def deduct_balance(self, user_id, amount):
        """Deduct an amount from the user's balance."""
        current_balance = self.get_balance(user_id)
        if current_balance < amount:
            return {"error": "Insufficient funds."}
        
        new_balance = round(current_balance - amount, 2)
        
        with DatabaseConnection() as cursor:
            cursor.execute("""
                UPDATE user_balances
                SET balance = %s
                WHERE user_id = %s
            """, (new_balance, user_id))
        
        return new_balance

    def get_top_balances(self, limit=5):
        """Retrieve the top users with the highest balances."""
        with DatabaseConnection() as cursor:
            cursor.execute("""
                SELECT user_id, balance
                FROM user_balances
                ORDER BY balance DESC
                LIMIT %s
            """, (limit,))
            top_players = cursor.fetchall()
        
        new_top_players = []
        for player in top_players:
            new_top_players.append((player[0], round(float(player[1]), 2)))
        top_players = sorted(new_top_players, key=lambda x: x[1], reverse=True)
        top_players = [{"name": player[0], "balance": player[1]} for player in top_players]
        return top_players