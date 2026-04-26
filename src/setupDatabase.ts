import { initializeDatabase, query, closeDatabase } from './databaseManager';
import { setupSchema } from './schema';

// Define the path for the database file
const DB_PATH = './tickets.db';

/**
 * Main function to initialize the database and set up all necessary schemas.
 */
export const setupDatabase = async (): Promise<void> => {
    console.log('==============================================================');
    console.log('🚀 setup Tickets Database...');
    console.log('==============================================================');

    try {
        // 1. Initialize the connection
        await initializeDatabase(DB_PATH);

        // 2. Set up the schema using the query function
        await setupSchema(query);

        console.log(`✅ Database initialization sequence completed successfully.`);

        // 3. Example: Run an initial check or seed data here
        // Example: Verify connection by getting the current timestamp
        const checkSql = "SELECT datetime('now') AS current_time;";
        // We must cast the result type to ensure TypeScript knows the structure
        const result: { current_time: string } = await query(checkSql);
        console.log(`✨ System Check: Current time recorded in DB: ${result.current_time}`);

    } catch (error) {
        console.error(`🔴 FATAL ERROR: Failed to start the application due to database setup failure.`);
        // Log the specific error object if it exists
        if (error instanceof Error) {
            console.error('Error Details:', error.message);
        } else {
            console.error('Error Details:', error);
        }
        // Re-throw to signal failure to the calling process
        throw error;
    } finally {
        console.log('--- Cleanup Complete ---');
    }
};

// Standard execution block for running the script directly
(async () => {
    try {
        await setupDatabase();
    } catch (e) {
        console.log('==============================================================');
        console.log('🛑 Application terminated with a critical error.');
        console.log('==============================================================');
        process.exit(1);
    }
})();
