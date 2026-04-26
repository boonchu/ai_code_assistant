import { query } from './databaseManager';
import { setupDatabase } from './setupDatabase'; // Assuming schema.ts exports setupSchema

// --- Configuration ---
// The database name is implicitly handled by databaseManager.ts connecting to the correct file.
// We will use the function provided by databaseManager.ts to execute queries.

/**
 * Helper function to execute a query and return results as a JSON string.
 * @param sql The SQL query string.
 * @param params Optional parameters for the query.
 * @returns A promise that resolves to a JSON string representation of the results.
 */
async function runQueryAndFormat(sql: string, params: any[] = []): Promise<string> {
    console.log(`\n--- Executing Query ---\nSQL: ${sql.trim()}`);
    console.log(`Params: ${JSON.stringify(params)}`);

    try {
        // Use the queryDB function from databaseManager.ts
        const results = await query(sql, params);
        // Format results as JSON string
        return JSON.stringify(results, null, 2);
    } catch (error) {
        console.error("Error executing query:", error);
        return JSON.stringify({ error: "Query execution failed", details: (error as Error).message });
    }
}

/**
 * Main function to run demonstration queries.
 */
async function main() {
    console.log("=====================================================================");
    console.log("🚀 Starting Ticket Database Query Application (app.ts)");
    console.log("=====================================================================");

    // 1. Ensure Schema is set up (Optional, but good for testing)
    // We use the function imported from schema.ts, which expects a query function.
    // We pass the queryDB function from databaseManager.ts as the queryFn.

    try {
        await setupDatabase();
    } catch (e) {
        console.log('==============================================================');
        console.log('🛑 Application terminated with a critical error.');
        console.log('==============================================================');
        process.exit(1);
    }

    // =================================================================================
    // 🎯 DEMO 1: Find tickets for the Music Festival (Using the query developed previously)
    // =================================================================================
    const musicFestivalQuery = `
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
    `;
    const musicFestivalJson = await runQueryAndFormat(musicFestivalQuery);
    console.log("\n=====================================================================");
    console.log("✨ RESULTS: Tickets for Local Music Festival (JSON Output)");
    console.log("=====================================================================");
    console.log(musicFestivalJson);


    // =================================================================================
    // 🎯 DEMO 2: Find users who never attended the Music Festival (Using the NOT IN logic)
    // =================================================================================
    const neverAttendedQuery = `
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
    `;
    const neverAttendedJson = await runQueryAndFormat(neverAttendedQuery);
    console.log("\n=====================================================================");
    console.log("✨ RESULTS: Users who never attended the Music Festival (JSON Output)");
    console.log("=====================================================================");
    console.log(neverAttendedJson);

    console.log("\n=====================================================================");
    console.log("✨ Demonstration Complete.");
    console.log("=====================================================================");
}

// Execute the main function
main();