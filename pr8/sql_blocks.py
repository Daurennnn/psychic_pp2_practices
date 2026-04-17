import psycopg2
from config import load_config

def sql_block():
    command = '''
        create or replace function count_even(table)
                returns integer
                language plpgsql
            as
        $$
        <<first_block>>
        declare
            count integer := 0;
        begin
            -- get the number of film
            select count(*)
            into film_count
            from film;
            -- display a message
            raise notice 'The number of films is %', film_count;
        end first_block $$;
    '''
    try:
        config = load_config()
        with psycopg2.connect(**config) as conn:
            with conn.cursor() as cur:
                cur.execute(command)
                print(cur.fetchone())
    except (psycopg2.DatabaseError, Exception) as error:
        print(error)

if __name__ == "__main__":
    sql_block()