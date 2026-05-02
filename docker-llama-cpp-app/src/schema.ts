/**
 * This file handles the initialization and creation of the database schema.
 * It accepts the core query function provided by databaseManager.ts.
 * @param queryFn The promise-returning function used to execute SQL against the DB.
 */

export const setupSchema = async (queryFn: (sql: string, params: any[]) => Promise<any>): Promise<void> => {
    console.log("\n===================================================================");
    console.log("🚀 Running database schema setup...");
    console.log("===================================================================");

    // --- 1. Users Table --- 
    // Stores user information
    const createUserTable = `
    CREATE TABLE IF NOT EXISTS Users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        email TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
`;
    await queryFn(createUserTable, []);

    // --- 2. Events Table --- 
    // Stores details for various events
    const createEventTable = `
    CREATE TABLE IF NOT EXISTS Events (
        event_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        event_date TEXT NOT NULL, -- Store as YYYY-MM-DD for easy sorting
        venue TEXT,
        capacity INTEGER
    );
`;
    await queryFn(createEventTable, []);

    // --- 3. Tickets Table --- 
    // Links users to events they have purchased tickets for
    const createTicketsTable = `
    CREATE TABLE IF NOT EXISTS Tickets (
        ticket_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        event_id INTEGER NOT NULL,
        purchase_date DATETIME DEFAULT CURRENT_TIMESTAMP,
        seat_number TEXT,
        -- Constraint to ensure a user can't buy two tickets for the exact same seat in the same event
        UNIQUE(user_id, event_id, seat_number),
        FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE,
        FOREIGN KEY (event_id) REFERENCES Events(event_id) ON DELETE CASCADE
    );
`;
    await queryFn(createTicketsTable, []);

    console.log("\n✅ Schema setup complete: Users, Events, and Tickets tables are ready.");
};
