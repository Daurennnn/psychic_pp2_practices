import psycopg2
from config import load_config

def create_tables():
    commands = (
        '''
        CREATE TABLE contacts (
                contact_id SERIAL PRIMARY KEY,
                name VARCHAR(25),
                number VARCHAR(20)
        )
        ''',
    )

    try:
        config = load_config()
        with psycopg2.connect(**config) as conn:
            with conn.cursor() as cur:
                # execute the CREATE TABLE statement
                for command in commands:
                    cur.execute(command)
    except (psycopg2.DatabaseError, Exception) as error:
        print(error)

if __name__ == "__main__":
    create_tables()