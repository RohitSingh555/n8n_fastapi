-- Ensure the user exists with mysql_native_password authentication
-- Drop user if exists and recreate with correct auth method
DROP USER IF EXISTS 'n8n_user'@'%';
CREATE USER 'n8n_user'@'%' IDENTIFIED WITH mysql_native_password BY 'n8n_password';
GRANT ALL PRIVILEGES ON n8n_feedback.* TO 'n8n_user'@'%';
FLUSH PRIVILEGES;
