### How to use sqlite3

* setup database

```
# create database with defined schema in code.
npx tsx src/setupDatabase.ts

# export schema
sqlite3 tickets.db .schema

# append new dataset
sqlite3 tickets.db < ./data/data.sql 
```

* search from dataset

```
# Charlie buys tickets for the Tech Summit
SELECT
    T.seat_number,
    T.purchase_date
FROM
    Tickets T
JOIN
    Users U ON T.user_id = U.user_id
JOIN
    Events E ON T.event_id = E.event_id
WHERE
    U.username = 'charlie_coder' AND E.name = 'Annual Tech Summit';

# who attend Music Festival
SELECT
    U.username AS user_name,
    E.name AS event_name,
    T.seat_number,
    T.purchase_date
FROM
    Tickets T
JOIN
    Users U ON T.user_id = U.user_id
JOIN
    Events E ON T.event_id = E.event_id
WHERE
    E.name = 'Local Music Festival';

# never attend Music Festival
SELECT
    username,
    email
FROM
    Users
WHERE
    user_id NOT IN (
        SELECT
            T.user_id
        FROM
            Tickets T
        JOIN
            Events E ON T.event_id = E.event_id
        WHERE
            E.name = 'Local Music Festival'
    );
```
