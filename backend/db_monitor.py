import time
from dotenv import load_dotenv
from main import create_app
from datetime import datetime, timedelta, timezone

# A module that will check what remains of the databases storage
# Notifies admins when getting full and deletes notifications from db as a preventative measure

load_dotenv()

CHECK_INTERVAL = 10  # This is 60 seconds
MAX_STORAGE_BYTES = (
    512 * 1024 * 1024
)  # this is equal to 512MB which is the limit of our mongo storage
PERCENTAGE_OF_DB = 0.9
ONE_WEEK_AGO = datetime.now(timezone.utc) - timedelta(weeks=1)

# Different app fields to keep track of for db size
def get_size_and_count(db):
    count = db.db.command("collStats", "notifications")["count"]
    note_size = db.db.command("collStats", "notifications")["size"]
    equip_size = db.db.command("collStats", "equipment")["size"]
    user_size = db.db.command("collStats", "users")["size"]
    pass_size = db.db.command("collStats", "password_resets")["size"]
    return (note_size + equip_size + user_size +pass_size), count

def monitor():
    print("Starting monitor...")
    app = create_app()  # this is just a new creation of the app to track DB storage

    with app.app_context():
        db = app.db
        nm = app.nm

        while True:
            try:
                size, count = get_size_and_count(db)
                print("Size:", size, "Count:", count)

                if (
                    size > MAX_STORAGE_BYTES * PERCENTAGE_OF_DB
                ):  # if it is above 80% full
                    
                    collection = db.notifications_db
                    res = collection.delete_many({"read": True, "date": {"$lt": ONE_WEEK_AGO}})
                    print(res.deleted_count)
                    time.sleep(CHECK_INTERVAL)
                    
                    size = db.db.command("dbStats")["storageSize"]
                    if size > MAX_STORAGE_BYTES * PERCENTAGE_OF_DB:
                        print("DATABASE IS OVER SET LIMIT")
                        # Notify admins of database reaching size limits
                        for admin in db.get_administrators():
                            nm.send_email(
                                receiver=admin.email,
                                subject="Database Getting Too Full",
                                message=(
                                    "Your Database is getting too full. Please either delete some of the older users or equipment that is no longer used."
                                    "If this is not an option, please contact the capstone group in order to upgrade your database"
                                ),
                            )
                   
                    else:
                        print(
                            f"Deleted {res.deleted_count} notifications from the database"
                        )
                        # Notify users of notification removal to preserve database
                        for user in db.get_all_users():
                            nm.send_inform_notification(
                                sender="System",
                                receiver=user,
                                message="All notifications that were unread and over a week old have been deleted to save database space",
                            )
            except Exception as e:
                print("Monitor error", e)

            time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    monitor()
