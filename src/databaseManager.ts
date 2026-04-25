import { open, Database } from 'sqlite'; // Assuming you use the wrapper for async/await

/**
 * Global variable to hold the initialized database connection object.
 */
let db: Database | null = null;

/**
 * Initializes the connection to the SQLite database using the provided path.
 * @param dbPath The file path to the SQLite database file.
 * @returns A Promise that resolves when the connection is successful.
 */
export async function initializeDatabase(dbPath: string): Promise<void> {
    if (db) {
        console.warn("Database already initialized. Skipping connection setup.");
        return;
    }

    console.log(`Attempting to open database connection at: ${dbPath}`);
    try {
        db = await open({ filename: dbPath, driver: Database });
        console.log("✅ Database connection established successfully.");
    } catch (error) {
        console.error("❌ ERROR: Could not connect to the database at", dbPath, error);
        throw error;
    }
}

/**
 * The core query function exported for schema setup and operations. 
 * This wraps the sqlite3 connection to execute SQL statements safely.
 * @param sql The SQL query string.
 * @param params An array of parameters for the query.
 * @returns A Promise resolving with the query result.
 */
export const query = async <T>(sql: string, params: any[] = []): Promise<T> => {
    if (!db) {
        throw new Error("Database connection is not initialized. Call initializeDatabase() first.");
    }
    console.log(`
[QUERY EXECUTING]:
  SQL: ${sql}
  Params: ${JSON.stringify(params)}
`);

    try {
        const result = await db.all(sql, params);
        return result as unknown as T;
    } catch (error) {
        console.error("🚨 SQL EXECUTION ERROR:", error);
        throw error;
    }
};

/**
 * Closes the database connection when the application shuts down.
 */
export const closeDatabase = async (): Promise<void> => {
    if (db) {
        await db.close();
        db = null;
        console.log("🚪 Database connection closed.");
    }
}
