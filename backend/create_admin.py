"""
Script to create admin user with password test123
"""
import os
import sys

# Set environment variable
os.environ['ADMIN_PASSWORD'] = 'test123'
os.environ['ADMIN_USERNAME'] = 'admin'

# Try to use a workaround for bcrypt
try:
    from models import init_db, SessionLocal, User
    from auth import get_password_hash, verify_password
    
    # Initialize database
    init_db()
    
    db = SessionLocal()
    try:
        # Check if admin user exists
        admin_user = db.query(User).filter(User.username == 'admin').first()
        
        if admin_user:
            # Update existing user
            print("Admin user exists. Updating password...")
            try:
                # Try to hash the password
                hashed = get_password_hash('test123')
                admin_user.hashed_password = hashed
                db.commit()
                print("Password updated successfully!")
            except Exception as e:
                print(f"Error updating password: {e}")
                # Use a simple hash as fallback
                import hashlib
                simple_hash = hashlib.sha256('test123'.encode()).hexdigest()
                admin_user.hashed_password = f"sha256${simple_hash}"
                db.commit()
                print("Password set using fallback method")
        else:
            # Create new user
            print("Creating admin user...")
            try:
                hashed = get_password_hash('test123')
                admin_user = User(username='admin', hashed_password=hashed)
                db.add(admin_user)
                db.commit()
                print("Admin user created successfully!")
            except Exception as e:
                print(f"Error creating user with bcrypt: {e}")
                # Use simple hash as fallback
                import hashlib
                simple_hash = hashlib.sha256('test123'.encode()).hexdigest()
                admin_user = User(username='admin', hashed_password=f"sha256${simple_hash}")
                db.add(admin_user)
                db.commit()
                print("Admin user created with fallback method")
        
        # Verify
        user = db.query(User).filter(User.username == 'admin').first()
        if user:
            print(f"Admin user found: {user.username}")
            print("Login credentials: admin / test123")
        else:
            print("ERROR: Admin user not found after creation")
            
    finally:
        db.close()
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

