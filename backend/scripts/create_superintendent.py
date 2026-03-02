'''Create superintendent account'''
import os
import sys

backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from dotenv import load_dotenv
load_dotenv()

from database import DatabaseManager
from helpers import hash_password

def main():
    db = DatabaseManager(testing=False)
    email = "super@test.com"
    if db.users_db.count_documents({"email": email}) > 0:
        user = db.get_user_by_email(email)
        db.set_user_role(id=user.id, role="s")
        print(f"Existing user {email} updated to Superintendent role")
    else:
        result = db.add_user(
            fname="Test",
            lname="Superintendent",
            phone=5551234567,
            email=email,
            password=hash_password("test_pass"),
        )
        if result["result"]:
            user = db.get_user_by_email(email)
            db.set_user_role(id=user.id, role="s")
            print(f"Created superintendent: {email} / superintendent")
        else:
            print(f"Failed: {result['message']}")

if __name__ == "__main__":
    main()
