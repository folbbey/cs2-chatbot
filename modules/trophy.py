"""
Trophy case module for displaying prized fish.
"""
from util.database import DatabaseConnection
from util.module_registry import module_registry


class Trophy:
    """Manage user trophy fish."""
    
    MAX_TROPHIES = 5
    
    def add_trophy(self, user_id: str, fish_name: str) -> dict:
        """
        Add a fish to the trophy case from caught fish.
        
        :param user_id: The user's identifier
        :param fish_name: The name of the fish to add
        :return: Result dictionary with success status and message
        """
        with DatabaseConnection() as cursor:
            # Check trophy count
            cursor.execute("""
                SELECT COUNT(*) FROM trophy_fish WHERE user_id = %s
            """, (user_id,))
            
            trophy_count = cursor.fetchone()[0]
            
            if trophy_count >= self.MAX_TROPHIES:
                return {
                    "success": False,
                    "message": f"Trophy case is full! Remove a trophy first (max {self.MAX_TROPHIES})."
                }
            
            # Find the fish in caught_fish by name (case-insensitive, partial match)
            cursor.execute("""
                SELECT id, name, weight, price
                FROM caught_fish
                WHERE user_id = %s AND LOWER(name) LIKE LOWER(%s)
                ORDER BY weight DESC
                LIMIT 1
            """, (user_id, f"%{fish_name}%"))
            
            fish = cursor.fetchone()
            
            if not fish:
                return {
                    "success": False,
                    "message": f"No fish matching '{fish_name}' found in your sack."
                }
            
            fish_id, name, weight, price = fish
            
            # Move fish to trophy case
            cursor.execute("""
                INSERT INTO trophy_fish (user_id, name, weight, price)
                VALUES (%s, %s, %s, %s)
            """, (user_id, name, weight, price))
            
            # Remove from caught_fish
            cursor.execute("""
                DELETE FROM caught_fish WHERE id = %s
            """, (fish_id,))
            
            return {
                "success": True,
                "message": f"Added {name} ({weight:.2f} lbs) to your trophy case!"
            }
    
    def remove_trophy(self, user_id: str, trophy_number: int) -> dict:
        """
        Remove a trophy fish by number and return it to caught_fish.
        
        :param user_id: The user's identifier
        :param trophy_number: The trophy number (1-5)
        :return: Result dictionary with success status and message
        """
        with DatabaseConnection() as cursor:
            # Get all trophies for the user
            cursor.execute("""
                SELECT id, name, weight, price
                FROM trophy_fish
                WHERE user_id = %s
                ORDER BY added_at ASC
            """, (user_id,))
            
            trophies = cursor.fetchall()
            
            if not trophies:
                return {
                    "success": False,
                    "message": "You don't have any trophies."
                }
            
            if trophy_number < 1 or trophy_number > len(trophies):
                return {
                    "success": False,
                    "message": f"Invalid trophy number. You have {len(trophies)} trophies."
                }
            
            # Get the trophy to remove (0-indexed)
            trophy = trophies[trophy_number - 1]
            trophy_id, name, weight, price = trophy
            
            # Return fish to caught_fish
            cursor.execute("""
                INSERT INTO caught_fish (user_id, name, weight, price, bait)
                VALUES (%s, %s, %s, %s, 0)
            """, (user_id, name, weight, price))
            
            # Remove from trophy case
            cursor.execute("""
                DELETE FROM trophy_fish WHERE id = %s
            """, (trophy_id,))
            
            return {
                "success": True,
                "message": f"Removed {name} ({weight:.2f} lbs) from your trophy case."
            }
    
    def get_trophies(self, user_id: str) -> list:
        """
        Get all trophy fish for a user.
        
        :param user_id: The user's identifier
        :return: List of trophy fish tuples (name, weight, price)
        """
        with DatabaseConnection() as cursor:
            cursor.execute("""
                SELECT name, weight, price
                FROM trophy_fish
                WHERE user_id = %s
                ORDER BY added_at ASC
            """, (user_id,))
            
            return cursor.fetchall()


# Register the module
module_registry.register("trophy", Trophy)
