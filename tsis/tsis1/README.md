# PhoneBook - Practice 9

A single-file console phonebook application using Python and PostgreSQL.

## Requirements

- Python 3.10 or higher
- PostgreSQL 13 or higher
- psycopg2 driver

Install the driver:

```
pip install psycopg2-binary
```

## Setup

**1. Create the database in PostgreSQL:**

```sql
CREATE DATABASE phonebook;
```

**2. Edit the connection string at the top of `phonebook.py`:**

```python
DB_DSN = "host=localhost dbname=phonebook user=postgres password=yourpassword"
```

| Part       | Description                                      |
|------------|--------------------------------------------------|
| `host`     | Where PostgreSQL is running (`localhost` for your own machine) |
| `dbname`   | Name of the database (`phonebook`)               |
| `user`     | Your PostgreSQL username (usually `postgres`)    |
| `password` | Your PostgreSQL password                         |

**3. Run the app:**

```
python phonebook.py
```

The app creates all tables and stored procedures automatically on first run.

## Database Schema

The app creates three tables:

- `contacts` - stores name, email, birthday, and group
- `phones` - stores phone numbers linked to a contact (one contact can have many phones)
- `groups` - stores categories (Family, Work, Friend, Other)

## Menu Options

```
 1. Browse all (paginated)
 2. Search (name / email / phone)
 3. Filter by group
 4. Search by email
 5. Add contact
 6. Update contact
 7. Delete contact
 8. Add phone to contact [proc]
 9. Move contact to group [proc]
10. Export to JSON
11. Import from JSON
12. Import from CSV
13. Exit
```

Options 8 and 9 run stored procedures directly on the database side.

## CSV Import

The CSV file must use these column headers:

```
first_name,last_name,phone,phone_type,email,birthday,group
```

Example:

```
first_name,last_name,phone,phone_type,email,birthday,group
Alice,Smith,+1-555-0101,mobile,alice@gmail.com,1990-03-15,Friend
Bob,Jones,+1-555-0202,work,bob@company.com,,Work
Carol,White,,,,,
```

Rules:
- `first_name` and `last_name` are required, all other columns are optional
- `phone_type` must be `mobile`, `home`, or `work` (defaults to `mobile` if blank)
- `birthday` must be in `YYYY-MM-DD` format or left blank
- `group` will be created automatically if it does not already exist
- Each CSV row supports one phone number only; add more phones through the menu after importing

## JSON Import and Export

Exporting writes a JSON file with full contact data including all phone numbers and group.

The JSON format for importing:

```json
[
  {
    "first_name": "Alice",
    "last_name": "Smith",
    "email": "alice@gmail.com",
    "birthday": "1990-03-15",
    "group_name": "Friend",
    "phones": [
      {"phone": "+1-555-0101", "type": "mobile"},
      {"phone": "+1-555-0102", "type": "home"}
    ]
  }
]
```

When a duplicate name is found during import, the app can skip it, overwrite it, or ask you each time.

## Stored Procedures

| Procedure / Function | What it does                                               |
|----------------------|------------------------------------------------------------|
| `add_phone`          | Adds a phone number to an existing contact                 |
| `move_to_group`      | Moves a contact to a group; creates the group if it is new |
| `search_contacts`    | Searches across name, email, and all phone numbers         |
