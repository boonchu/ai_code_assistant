-- =================================================================
-- 💾 DATASET INSERTION SCRIPT FOR TICKET SYSTEM
-- NOTE: This script assumes the schema (Users, Events, Tickets) has already been created.
-- =================================================================

-- 1. INSERT DATA INTO Users Table
-- We insert a few sample users.
INSERT INTO Users (username, email, password_hash) VALUES
('alice_wonder', 'alice@example.com', 'hashed_password_alice'),
('bob_builder', 'bob@example.com', 'hashed_password_bob'),
('charlie_coder', 'charlie@example.com', 'hashed_password_charlie');

-- 2. INSERT DATA INTO Events Table
-- We insert a few sample events.
INSERT INTO Events (name, description, event_date, venue, capacity) VALUES
('Annual Tech Summit', 'A conference on the latest in software development.', '2024-11-15', 'Convention Center Hall A', 500),
('Local Music Festival', 'A weekend celebration of local arts and music.', '2024-10-20', 'City Park Grounds', 1500),
('Product Launch Gala', 'Exclusive launch party for our new flagship product.', '2024-12-01', 'Grand Ballroom', 200);

-- 3. INSERT DATA INTO Tickets Table
-- We link users to events they have purchased tickets for.
-- IMPORTANT: These inserts rely on the user_id and event_id generated above.
-- Assuming the IDs generated are 1, 2, 3 for users, and 1, 2, 3 for events.

-- Alice buys tickets for the Tech Summit (Event 1) and Gala (Event 3)
INSERT INTO Tickets (user_id, event_id, seat_number) VALUES
(1, 1, 'A1'),
(1, 3, 'B5');

-- Bob buys tickets for the Music Festival (Event 2)
INSERT INTO Tickets (user_id, event_id, seat_number) VALUES
(2, 2, 'C10');

-- Charlie buys tickets for the Tech Summit (Event 1) and the Music Festival (Event 2)
INSERT INTO Tickets (user_id, event_id, seat_number) VALUES
(3, 1, 'A2'),
(3, 2, 'D3');

-- Optional: If you want to clear all data for a fresh start, uncomment the following lines:
/*
DELETE FROM Tickets;
DELETE FROM Users;
DELETE FROM Events;
*/