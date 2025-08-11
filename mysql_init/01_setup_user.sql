-- Force the user to use mysql_native_password authentication
ALTER USER 'n8n_user'@'%' IDENTIFIED WITH mysql_native_password BY 'n8n_password';
FLUSH PRIVILEGES;
