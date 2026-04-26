import json
from connect import connect



def add_contact():
    conn = connect()
    cur = conn.cursor()

    name = input("Name: ")
    email = input("Email: ")
    birthday = input("Birthday (YYYY-MM-DD): ")
    group = input("Group (Family/Friend/Work/Other): ")


    cur.execute("""
        INSERT INTO groups(name)
        VALUES (%s)
        ON CONFLICT (name) DO NOTHING
    """, (group,))

    cur.execute("SELECT id FROM groups WHERE name=%s", (group,))
    group_id = cur.fetchone()[0]

    cur.execute("""
        INSERT INTO contacts(name,email,birthday,group_id)
        VALUES (%s,%s,%s,%s)
    """, (name, email, birthday, group_id))

    conn.commit()
    conn.close()
    print("Contact added!")



def add_phone():
    conn = connect()
    cur = conn.cursor()

    name = input("Contact name: ")
    phone = input("Phone: ")
    ptype = input("Type (home/work/mobile): ")

    cur.execute("CALL add_phone(%s,%s,%s)", (name, phone, ptype))

    conn.commit()
    conn.close()
    print("Phone added!")



def search():
    conn = connect()
    cur = conn.cursor()

    q = input("Search: ")

    cur.execute("SELECT * FROM search_contacts(%s)", (q,))

    for row in cur.fetchall():
        print(row)

    conn.close()


def filter_by_group():
    conn = connect()
    cur = conn.cursor()

    group = input("Enter group: ")

    cur.execute("""
        SELECT c.name, c.email
        FROM contacts c
        JOIN groups g ON c.group_id = g.id
        WHERE g.name = %s
    """, (group,))

    for r in cur.fetchall():
        print(r)

    conn.close()



def sort_contacts():
    conn = connect()
    cur = conn.cursor()

    print("Sort by:")
    print("1 - Name")
    print("2 - Birthday")

    choice = input("Enter: ")

    if choice == "1":
        order = "name"
    elif choice == "2":
        order = "birthday"
    else:
        print("Invalid input")
        return

    cur.execute(f"""
        SELECT name, email, birthday
        FROM contacts
        ORDER BY {order}
    """)

    for r in cur.fetchall():
        print(r)

    conn.close()



def paginate():
    conn = connect()
    cur = conn.cursor()

    limit = 5
    offset = 0

    while True:
        cur.execute("""
            SELECT name, email
            FROM contacts
            LIMIT %s OFFSET %s
        """, (limit, offset))

        rows = cur.fetchall()

        print("\n--- PAGE ---")
        for r in rows:
            print(r)

        action = input("next / prev / quit: ")

        if action == "next":
            offset += limit
        elif action == "prev":
            offset = max(0, offset - limit)
        else:
            break

    conn.close()



def export_json():
    conn = connect()
    cur = conn.cursor()

    cur.execute("""
        SELECT c.name, c.email, c.birthday, g.name, p.phone, p.type
        FROM contacts c
        LEFT JOIN groups g ON c.group_id = g.id
        LEFT JOIN phones p ON c.id = p.contact_id
    """)

    data = cur.fetchall()

    with open("contacts.json", "w") as f:
        json.dump(data, f, indent=4, default=str)

    conn.close()
    print("Exported to contacts.json")



import json
from connect import connect

def import_json():
    try:
        with open("contacts.json", "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        print("contacts.json not found!")
        return
    except json.JSONDecodeError:
        print("Invalid JSON file! Make sure it is not empty.")
        return

    if not data:
        print("JSON file is empty. Nothing to import.")
        return

    conn = connect()
    cur = conn.cursor()

    print(f"\nImporting {len(data)} contacts...\n")

    for row in data:
        try:
            name, email, birthday, group, phone, ptype = row
        except ValueError:
            print("Skipping invalid row:", row)
            continue

        print(f"Processing: {name}")


        cur.execute("SELECT id FROM contacts WHERE name=%s", (name,))
        exists = cur.fetchone()

        if exists:
            choice = input(f"{name} exists. skip / overwrite: ").strip().lower()

            if choice == "skip":
                print("Skipped.\n")
                continue
            elif choice == "overwrite":
                cur.execute("DELETE FROM contacts WHERE name=%s", (name,))
                print("Overwritten.\n")
            else:
                print("Invalid choice, skipping.\n")
                continue


        cur.execute("""
            INSERT INTO groups(name)
            VALUES (%s)
            ON CONFLICT (name) DO NOTHING
        """, (group,))

        cur.execute("SELECT id FROM groups WHERE name=%s", (group,))
        group_id = cur.fetchone()[0]


        cur.execute("""
            INSERT INTO contacts(name, email, birthday, group_id)
            VALUES (%s, %s, %s, %s)
            RETURNING id
        """, (name, email, birthday, group_id))

        contact_id = cur.fetchone()[0]


        if phone:
            cur.execute("""
                INSERT INTO phones(contact_id, phone, type)
                VALUES (%s, %s, %s)
            """, (contact_id, phone, ptype))

        print("Added.\n")

    conn.commit()
    conn.close()

    print("Import completed successfully!")

def move_to_group():
    conn = connect()
    cur = conn.cursor()

    name = input("Contact name: ")
    group = input("New group: ")

    cur.execute("CALL move_to_group(%s,%s)", (name, group))

    conn.commit()
    conn.close()
    print("Moved to new group!")



def menu():
    while True:
        print("\n--- PHONEBOOK ---")
        print("1 Add Contact")
        print("2 Add Phone")
        print("3 Search")
        print("4 Filter by Group")
        print("5 Sort")
        print("6 Pagination")
        print("7 Export JSON")
        print("8 Import JSON")
        print("9 Move to Group")
        print("0 Exit")

        choice = input("Choose: ")

        if choice == "1":
            add_contact()
        elif choice == "2":
            add_phone()
        elif choice == "3":
            search()
        elif choice == "4":
            filter_by_group()
        elif choice == "5":
            sort_contacts()
        elif choice == "6":
            paginate()
        elif choice == "7":
            export_json()
        elif choice == "8":
            import_json()
        elif choice == "9":
            move_to_group()
        elif choice == "0":
            break



menu()