import sqlite3 from 'sqlite3';
/**
 * Global variable to hold the initialized database connection object.
 * This will now hold the better-sqlite3 instance.
 */
let db: sqlite3.Database;

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
        // better-sqlite3 opens synchronously, so we wrap it in a Promise
        db = new sqlite3.Database(dbPath);
        console.log("✅ Database connection established successfully.");
    } catch (error) {
        console.error("❌ ERROR: Could not connect to the database at", dbPath, error);
        throw error;
    }
}

/**
 * The core query function exported for schema setup and operations. 
 * This wraps the better-sqlite3 connection to execute SQL statements safely.
 * @param sql The SQL query string.
 * @param params An array of parameters for the query.
 * @returns A Promise resolving with the query result (Array of rows).
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

    return new Promise((resolve, reject) => {
        try {
            const rows = db.all(sql, params);
            resolve(rows as unknown as T);
        } catch (error) {
            console.error("🚨 SQL EXECUTION ERROR:", error);
            reject(error);
        }
    });
}

/**
 * Closes the database connection when the application shuts down.
 */
export const closeDatabase = async (): Promise<void> => {
    if (db) {
        try {
            // better-sqlite3 uses a synchronous close method
            db.close();
            console.log("🚪 Database connection closed.");
        } catch (error) {
            console.error("Error closing database:", error);
            throw error;
        }
    }
    return Promise.resolve();
}