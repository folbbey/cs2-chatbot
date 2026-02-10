"""
Account linking module for cross-platform user identification.
"""
import random
import string
from datetime import datetime, timedelta
from util.database import DatabaseConnection
from util.module_registry import module_registry


class AccountLinking:
    """Manage account linking across platforms."""
    
    def __init__(self):
        """Initialize the account linking module."""
        self.code_length = 6
        self.code_expiry_minutes = 10
    
    def generate_code(self, platform: str, identifier: str) -> str:
        """
        Generate a temporary linking code for a user.
        
        :param platform: The platform (e.g., 'discord', 'cs2')
        :param identifier: The user identifier on that platform
        :return: The generated code
        """
        # Generate a random 6-digit code
        code = ''.join(random.choices(string.digits, k=self.code_length))
        
        # Calculate expiration time
        expires_at = datetime.now() + timedelta(minutes=self.code_expiry_minutes)
        
        with DatabaseConnection() as cursor:
            # Remove any existing codes for this user
            cursor.execute("""
                DELETE FROM link_codes
                WHERE platform = %s AND identifier = %s
            """, (platform, identifier))
            
            # Insert the new code
            cursor.execute("""
                INSERT INTO link_codes (code, platform, identifier, expires_at)
                VALUES (%s, %s, %s, %s)
            """, (code, platform, identifier, expires_at))
        
        return code
    
    def use_code(self, code: str, target_platform: str, target_identifier: str) -> dict:
        """
        Use a linking code to link two accounts.
        
        :param code: The linking code
        :param target_platform: The platform of the account using the code
        :param target_identifier: The identifier on that platform
        :return: Dictionary with success/error information
        """
        with DatabaseConnection() as cursor:
            # Find the code
            cursor.execute("""
                SELECT platform, identifier, expires_at
                FROM link_codes
                WHERE code = %s
            """, (code,))
            
            result = cursor.fetchone()
            
            if not result:
                return {"error": "Invalid code. Please check and try again."}
            
            source_platform, source_identifier, expires_at = result
            
            # Check if expired
            if datetime.now() > expires_at:
                cursor.execute("DELETE FROM link_codes WHERE code = %s", (code,))
                return {"error": "Code has expired. Please generate a new one."}
            
            # Check if trying to link the same account
            if source_platform == target_platform and source_identifier == target_identifier:
                return {"error": "Cannot link an account to itself."}
            
            # Check if either account is already linked
            cursor.execute("""
                SELECT account_id FROM account_links
                WHERE (platform = %s AND identifier = %s)
                   OR (platform = %s AND identifier = %s)
            """, (source_platform, source_identifier, target_platform, target_identifier))
            
            existing_links = cursor.fetchall()
            
            if existing_links:
                # Both accounts should share the same account_id
                account_ids = set(link[0] for link in existing_links)
                
                if len(account_ids) > 1:
                    return {"error": "Cannot link accounts that are already linked to different account IDs."}
                
                account_id = account_ids.pop()
                
                # Add the missing link(s)
                existing_platforms = {}
                cursor.execute("""
                    SELECT platform, identifier FROM account_links
                    WHERE account_id = %s
                """, (account_id,))
                for plat, ident in cursor.fetchall():
                    existing_platforms[plat] = ident
                
                # Add source if not exists
                if source_platform not in existing_platforms:
                    # Check if this (platform, identifier) already exists
                    cursor.execute("""
                        SELECT account_id FROM account_links
                        WHERE platform = %s AND identifier = %s
                    """, (source_platform, source_identifier))
                    existing = cursor.fetchone()
                    if not existing:
                        cursor.execute("""
                            INSERT INTO account_links (account_id, platform, identifier)
                            VALUES (%s, %s, %s)
                        """, (account_id, source_platform, source_identifier))
                
                # Add target if not exists
                if target_platform not in existing_platforms:
                    # Check if this (platform, identifier) already exists
                    cursor.execute("""
                        SELECT account_id FROM account_links
                        WHERE platform = %s AND identifier = %s
                    """, (target_platform, target_identifier))
                    existing = cursor.fetchone()
                    if not existing:
                        cursor.execute("""
                            INSERT INTO account_links (account_id, platform, identifier)
                            VALUES (%s, %s, %s)
                        """, (account_id, target_platform, target_identifier))
            else:
                # Neither account is linked, create new account_id
                # Check if source already exists
                cursor.execute("""
                    SELECT account_id FROM account_links
                    WHERE platform = %s AND identifier = %s
                """, (source_platform, source_identifier))
                existing_source = cursor.fetchone()
                
                if existing_source:
                    account_id = existing_source[0]
                else:
                    # Generate a new account_id (get max + 1)
                    cursor.execute("SELECT COALESCE(MAX(account_id), 0) + 1 FROM account_links")
                    account_id = cursor.fetchone()[0]
                    
                    # Insert source account
                    cursor.execute("""
                        INSERT INTO account_links (account_id, platform, identifier)
                        VALUES (%s, %s, %s)
                    """, (account_id, source_platform, source_identifier))
                
                # Check if target already exists
                cursor.execute("""
                    SELECT account_id FROM account_links
                    WHERE platform = %s AND identifier = %s
                """, (target_platform, target_identifier))
                existing_target = cursor.fetchone()
                
                if not existing_target:
                    # Link the target account with the same account_id
                    cursor.execute("""
                        INSERT INTO account_links (account_id, platform, identifier)
                        VALUES (%s, %s, %s)
                    """, (account_id, target_platform, target_identifier))
            
            # Delete the used code
            cursor.execute("DELETE FROM link_codes WHERE code = %s", (code,))
        
        return {
            "success": True,
            "message": f"Successfully linked {target_platform} user \"{target_identifier}\" to {source_platform} user \"{source_identifier}\".",
            "account_id": account_id
        }
    
    def get_linked_accounts(self, platform: str, identifier: str) -> list:
        """
        Get all linked accounts for a user.
        
        :param platform: The platform
        :param identifier: The user identifier
        :return: List of (platform, identifier) tuples
        """
        with DatabaseConnection() as cursor:
            # Find the account_id
            cursor.execute("""
                SELECT account_id FROM account_links
                WHERE platform = %s AND identifier = %s
            """, (platform, identifier))
            
            result = cursor.fetchone()
            
            if not result:
                return []
            
            account_id = result[0]
            
            # Get all linked accounts
            cursor.execute("""
                SELECT platform, identifier
                FROM account_links
                WHERE account_id = %s
            """, (account_id,))
            
            return cursor.fetchall()
    
    def get_unified_user_id(self, platform: str, identifier: str) -> str:
        """
        Get the unified user ID (primary identifier) for cross-platform operations.
        Returns the original identifier if no link exists.
        
        :param platform: The platform
        :param identifier: The user identifier
        :return: The unified user ID (account_id) or original identifier
        """
        with DatabaseConnection() as cursor:
            cursor.execute("""
                SELECT account_id FROM account_links
                WHERE platform = %s AND identifier = %s
            """, (platform, identifier))
            
            result = cursor.fetchone()
            
            if result:
                return f"account_{result[0]}"
            
            return identifier
    
    def cleanup_expired_codes(self):
        """Remove expired linking codes."""
        with DatabaseConnection() as cursor:
            cursor.execute("""
                DELETE FROM link_codes
                WHERE expires_at < NOW()
            """)


# Register the module
module_registry.register("account_linking", AccountLinking)
