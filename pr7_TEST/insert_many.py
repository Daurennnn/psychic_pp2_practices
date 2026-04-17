import psycopg2
from config import load_config

def insert_vendors(vendors_list):
    """ Insert a new vendor into the vendors table """

    sql = """INSERT INTO vendors(vendor_name)
             VALUES(%s) RETURNING vendor_id;"""
    vendor_id = None
    config = load_config()
    try:
        with  psycopg2.connect(**config) as conn:
            with  conn.cursor() as cur:
                # execute the INSERT statement
                cur.executemany(sql, (vendors_list))
                # commit the changes to the database
                conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print("!!!" + error)
    finally:
        return vendor_id
if __name__ == '__main__':
    vendors_list = (
        ("Rakhat",),
        ("Samsung",),
        ("Lenovo",),
        ("Apple",)
    )
    insert_vendors(vendors_list)