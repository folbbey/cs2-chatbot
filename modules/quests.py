import json
import os
from datetime import datetime, timedelta
from psycopg2.extras import RealDictCursor
import random
from util.database import get_connection, return_connection

class QuestModule:
    def __init__(self):
        # Load quest data
        quest_file = os.path.join(os.path.dirname(__file__), 'data', 'quests.json')
        with open(quest_file, 'r') as f:
            self.all_quests = json.load(f)
    
    def get_daily_quest(self, user_id):
        """Get or assign the current daily quest for a user using weighted random selection."""
        conn = get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Check if user has an active daily quest
                cur.execute("""
                    SELECT quest_id, assigned_at, completed
                    FROM daily_quests
                    WHERE user_id = %s
                    ORDER BY assigned_at DESC
                    LIMIT 1
                """, (user_id,))
                
                result = cur.fetchone()
                
                # If no quest or quest is expired (>24h) or already completed, assign new one
                if not result or result['completed'] or \
                   (datetime.now() - result['assigned_at']) > timedelta(hours=24):
                    # Pick a weighted random quest
                    weights = [q['weight'] for q in self.all_quests]
                    new_quest = random.choices(self.all_quests, weights=weights, k=1)[0]
                    
                    cur.execute("""
                        INSERT INTO daily_quests (user_id, quest_id, assigned_at, completed)
                        VALUES (%s, %s, %s, FALSE)
                    """, (user_id, new_quest['id'], datetime.now()))
                    conn.commit()
                    
                    return new_quest
                else:
                    # Return existing active quest
                    quest_id = result['quest_id']
                    return next((q for q in self.all_quests if q['id'] == quest_id), None)
        finally:
            return_connection(conn)
    
    def get_time_until_next_quest(self, user_id):
        """Get time remaining until user can get a new quest."""
        conn = get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT assigned_at, completed
                    FROM daily_quests
                    WHERE user_id = %s
                    ORDER BY assigned_at DESC
                    LIMIT 1
                """, (user_id,))
                
                result = cur.fetchone()
                
                if not result:
                    return None  # No previous quest, can get one now
                
                if result['completed']:
                    # Calculate time until 24h from completion
                    time_elapsed = datetime.now() - result['assigned_at']
                    time_remaining = timedelta(hours=24) - time_elapsed
                    
                    if time_remaining.total_seconds() <= 0:
                        return None  # Can get new quest now
                    
                    return time_remaining
                
                return None  # Has active uncompleted quest
        finally:
            return_connection(conn)
    
    def check_requirements(self, user_id, requirements):
        """Check if user has all required items/fish."""
        conn = get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                for req in requirements:
                    item_name = req['name']
                    required_qty = req['quantity']
                    
                    # Check in caught_fish (sack)
                    cur.execute("""
                        SELECT COUNT(*) as count
                        FROM caught_fish
                        WHERE user_id = %s AND name = %s
                    """, (user_id, item_name))
                    fish_count = cur.fetchone()['count']
                    
                    # Check in user_inventory
                    cur.execute("""
                        SELECT quantity
                        FROM user_inventory
                        WHERE user_id = %s AND item_name = %s
                    """, (user_id, item_name))
                    inv_result = cur.fetchone()
                    inv_count = inv_result['quantity'] if inv_result else 0
                    
                    total = fish_count + inv_count
                    
                    if total < required_qty:
                        return False, item_name, total, required_qty
                
                return True, None, None, None
        finally:
            return_connection(conn)
    
    def remove_items(self, user_id, requirements):
        """Remove required items from user's inventory/sack."""
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                for req in requirements:
                    item_name = req['name']
                    qty_needed = req['quantity']
                    
                    # Remove from caught_fish first
                    cur.execute("""
                        DELETE FROM caught_fish
                        WHERE id IN (
                            SELECT id FROM caught_fish
                            WHERE user_id = %s AND name = %s
                            LIMIT %s
                        )
                        RETURNING id
                    """, (user_id, item_name, qty_needed))
                    removed_from_fish = len(cur.fetchall())
                    
                    qty_remaining = qty_needed - removed_from_fish
                    
                    # Remove rest from inventory if needed
                    if qty_remaining > 0:
                        cur.execute("""
                            UPDATE user_inventory
                            SET quantity = quantity - %s
                            WHERE user_id = %s AND item_name = %s
                        """, (qty_remaining, user_id, item_name))
                        
                        # Clean up zero quantity items
                        cur.execute("""
                            DELETE FROM user_inventory
                            WHERE user_id = %s AND quantity <= 0
                        """, (user_id,))
                
                conn.commit()
        finally:
            return_connection(conn)
    
    def claim_daily_quest(self, user_id):
        """Attempt to claim the daily quest reward."""
        quest = self.get_daily_quest(user_id)
        if not quest:
            return False, "No daily quest available."
        
        # Check if already completed
        conn = get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT completed FROM daily_quests
                    WHERE user_id = %s AND quest_id = %s
                    ORDER BY assigned_at DESC
                    LIMIT 1
                """, (user_id, quest['id']))
                result = cur.fetchone()
                
                if result and result['completed']:
                    return False, "Daily quest already completed. New quest in 24h."
        finally:
            return_connection(conn)
        
        # Check requirements
        has_items, missing_item, has_qty, needs_qty = self.check_requirements(
            user_id, quest['requirements']
        )
        
        if not has_items:
            return False, f"Missing items: need {needs_qty}x {missing_item}, you have {has_qty}."
        
        # Remove items and give reward
        self.remove_items(user_id, quest['requirements'])
        
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                # Give money reward
                cur.execute("""
                    INSERT INTO user_balances (user_id, balance)
                    VALUES (%s, %s)
                    ON CONFLICT (user_id)
                    DO UPDATE SET balance = user_balances.balance + %s
                """, (user_id, quest['reward_money'], quest['reward_money']))
                
                # Mark as completed
                cur.execute("""
                    UPDATE daily_quests
                    SET completed = TRUE, completed_at = %s
                    WHERE user_id = %s AND quest_id = %s
                """, (datetime.now(), user_id, quest['id']))
                
                conn.commit()
        finally:
            return_connection(conn)
        
        return True, f"Quest completed! Earned ${quest['reward_money']:,}"
