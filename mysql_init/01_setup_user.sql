-- Create user if it doesn't exist and grant privileges
CREATE USER IF NOT EXISTS 'n8n_user'@'%' IDENTIFIED WITH mysql_native_password BY 'n8n_password';
GRANT ALL PRIVILEGES ON n8n_feedback.* TO 'n8n_user'@'%';
FLUSH PRIVILEGES;
