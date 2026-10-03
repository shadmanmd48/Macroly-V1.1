import logging
from backend.database import data_store

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("macroly.migration")

def run_migration():
    if not data_store.use_postgres:
        logger.info("Using SQLite - skipping PostgreSQL foreign key migration.")
        return

    conn = data_store.get_connection()
    cur = conn.cursor()
    elena_uid = "86759b8f-d1fd-4f9a-9e3d-a93bf143c10b"

    logger.info("1. Updating test and Elena records to real auth UID: %s", elena_uid)
    cur.execute("DELETE FROM users WHERE id = 'test-shadman-user'")
    cur.execute("UPDATE meal_logs SET user_id = %s WHERE user_id IN ('Elena', 'elena-demo-account-000000000001')", (elena_uid,))
    cur.execute("UPDATE user_vitals SET user_id = %s WHERE user_id IN ('Elena', 'elena-demo-account-000000000001')", (elena_uid,))
    cur.execute("UPDATE users SET id = %s WHERE id IN ('Elena', 'elena-demo-account-000000000001')", (elena_uid,))

    logger.info("2. Dropping default 'Elena' on meal_logs.user_id")
    try:
        cur.execute("ALTER TABLE meal_logs ALTER COLUMN user_id DROP DEFAULT")
    except Exception as e:
        logger.warning("DROP DEFAULT: %s", e)

    logger.info("3. Altering users.id to UUID")
    try:
        cur.execute("ALTER TABLE users ALTER COLUMN id TYPE uuid USING id::uuid")
    except Exception as e:
        logger.warning("ALTER COLUMN TYPE: %s", e)

    logger.info("4. Adding Foreign Key from public.users(id) to auth.users(id)")
    cur.execute("""
    SELECT count(*) FROM pg_constraint WHERE conname = 'fk_users_auth_users'
    """)
    row = cur.fetchone()
    count = row['count'] if isinstance(row, dict) else row[0]
    if count == 0:
        cur.execute("""
        ALTER TABLE public.users
        ADD CONSTRAINT fk_users_auth_users
        FOREIGN KEY (id) REFERENCES auth.users(id) ON DELETE CASCADE
        """)
        logger.info("Foreign key constraint fk_users_auth_users added successfully!")
    else:
        logger.info("Foreign key constraint fk_users_auth_users already exists.")

    logger.info("5. Verifying indexes on user_id across tables")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_meal_logs_user_id ON meal_logs(user_id);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);")

    conn.commit()
    conn.close()
    logger.info("✅ Database schema migration complete!")

if __name__ == "__main__":
    run_migration()
