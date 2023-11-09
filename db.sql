-- Create VTSB database
CREATE DATABASE vtsb_db;

SELECT * FROM conversations;

SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
ORDER BY table_name;