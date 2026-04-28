#!/usr/bin/env python3
"""Check and create test user for login"""
import sys
sys.path.insert(0, '.')

from app.repositories.user_repository import UserRepository
from app.utils.auth import PasswordManager

def main():
    email = 'adiabhiraj141@gmail.com'
    password = 'asdfghjkl'
    username = 'adiabhiraj'
    
    print(f"Checking for user: {email}")
    
    # Check if user exists
    user = UserRepository.get_user_by_email(email)
    if user:
        print(f'✅ User found: {user["email"]} (ID: {user["id"]})')
        print(f'Username: {user["username"]}')
        
        # Test password verification
        if PasswordManager.verify_password(password, user['password_hash']):
            print(f'✅ Password verification SUCCESSFUL')
            print(f'\n🎉 User is ready to login!')
        else:
            print(f'❌ Password verification FAILED')
            print(f'Hash in DB: {user["password_hash"][:60]}...')
            print(f'\nRe-creating user with correct password...')
            # Delete and recreate
            UserRepository.delete_user(user['id'])
            hashed_pwd = PasswordManager.hash_password(password)
            user_id = UserRepository.create_user(email, username, hashed_pwd)
            if user_id:
                print(f'✅ User re-created successfully with ID: {user_id}')
            else:
                print('❌ Failed to re-create user')
    else:
        print('❌ User NOT found in database')
        print('Creating test user...')
        # Create the user
        hashed_pwd = PasswordManager.hash_password(password)
        user_id = UserRepository.create_user(email, username, hashed_pwd)
        if user_id:
            print(f'✅ User created successfully with ID: {user_id}')
            print(f'\n🎉 You can now login with:')
            print(f'   Email: {email}')
            print(f'   Password: {password}')
        else:
            print('❌ Failed to create user')

if __name__ == '__main__':
    main()
