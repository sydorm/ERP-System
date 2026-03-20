"""
Script to reset user password
"""
import sys
import os

# Add the necessary directories to sys.path
root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
backend_dir = os.path.join(root_dir, "backend")
sys.path.append(root_dir)
sys.path.append(backend_dir)

from app.db.session import SessionLocal
from app.models.user import User
from app.core.security import get_password_hash

def reset_password(email, new_password):
    db = SessionLocal()
    try:
        # Case insensitive search if needed, but the screenshot showed 'Admin@gmail.com'
        user = db.query(User).filter(User.email == email).first()
        
        if not user:
            # Try lower case if not found
            user = db.query(User).filter(User.email == email.lower()).first()
            
        if user:
            user.hashed_password = get_password_hash(new_password)
            db.commit()
            print(f"✓ Password for user {user.email} has been reset successfully.")
        else:
            print(f"✗ User with email {email} not found.")
            # List some users to help debug
            users = db.query(User).limit(5).all()
            if users:
                print("Available users:")
                for u in users:
                    print(f" - {u.email}")
    except Exception as e:
        db.rollback()
        print(f"✗ Error resetting password: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    target_email = "Admin@gmail.com"
    target_password = "Admin123456"
    print(f"Attempting to reset password for {target_email}...")
    reset_password(target_email, target_password)
