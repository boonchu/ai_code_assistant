import { initializeDatabase, query, closeDatabase } from './databaseManager.js';
import { setupSchema } from './schema.js';

// Define the path for the database file
const DB_PATH = './database.sqlite';

/**
 * Main function to initialize the database and set up all necessary schemas.
 */
export const startDatabase = async (): Promise<void> => {
    console.log('--- Application Startup ---');

    try {
        // 1. Initialize the connection
        await initializeDatabase(DB_PATH);

        // 2. Set up the schema using the query function
        await setupSchema(query);

        console.log('\n✅ Database initialization sequence completed successfully.');

        // 3. (Optional) Example: Run an initial check or seed data here
        // Example: Verify connection by getting the current timestamp
        const checkSql = "SELECT datetime('now') AS current_time;";
        // We must cast the result type to ensure TypeScript knows the structure
        const result: { current_time: string }[] = await query(checkSql);
        console.log(`System Check: Current time recorded in DB: ${result[0].current_time}`);

    } catch (error) {
        console.error('\n🔴 FATAL ERROR: Failed to start the application due to database setup failure.', error);
        // Re-throw to signal failure to the calling process
        throw error;
    } finally {
        // IMPORTANT: If this script runs and finishes, we close the connection.
        // In a long-running service, this cleanup would happen on SIGINT/SIGTERM.
        await closeDatabase();
    }
};

// Standard execution block for running the script directly
(async () => {
    try {
        await startDatabase();
    } catch (e) {
        console.log('\nApplication terminated with an error.');
        process.exit(1);
    }
})();
