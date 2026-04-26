### How to use sqlite3

```
# create database with defined schema in code.
npx tsx src/setupDatabase.ts

# export schema
sqlite3 tickets.db .schema
```