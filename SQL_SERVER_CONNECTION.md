# SQL Server Connection Guide

This guide shows how to connect the ETU Results Management System to a SQL Server database.

## Prerequisites

1. **SQL Server** installed and running (SQL Server 2019 or later recommended)
2. **ODBC Driver 17 for SQL Server** installed on your machine
   - Download from: https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server
3. **Python packages**: pyodbc and django-mssql-backend

## Installation Steps

### Step 1: Install Python Packages

From the project root, install the required packages:

```powershell
pip install pyodbc "django-mssql-backend>=2.8.1"
```

### Step 2: Gather SQL Server Connection Details

You'll need:
- **Server name**: e.g., `localhost`, `.\SQLEXPRESS`, or `192.168.1.100`
- **Port**: default is `1433`
- **Username**: e.g., `sa` (SQL Server admin)
- **Password**: your SQL Server password
- **Database name**: e.g., `eturesults`

### Step 3: Create the Database (if needed)

Open SQL Server Management Studio (SSMS) or use sqlcmd:

```sql
CREATE DATABASE eturesults;
GO
```

### Step 4: Set Environment Variable

Set the `MSSQL_DATABASE_URL` environment variable with your connection string.

**Format:**
```
mssql://username:password@server:port/database
```

**Example (SQL Server on localhost with SQLEXPRESS):**
```powershell
$env:MSSQL_DATABASE_URL = 'mssql://sa:YourPassword@localhost\SQLEXPRESS:1433/eturesults'
```

Or make it permanent (requires new PowerShell window):
```powershell
setx MSSQL_DATABASE_URL "mssql://sa:YourPassword@localhost\SQLEXPRESS:1433/eturesults"
```

### Step 5: Run Migrations

Create the database tables:

```powershell
python manage.py migrate
```

This will create all necessary tables for Django and the ETU Results app.

### Step 6: Start the Server

```powershell
python manage.py runserver
```

Or use the helper script (which does steps 5-6 automatically):

```powershell
$env:MSSQL_DATABASE_URL = 'mssql://sa:YourPassword@localhost\SQLEXPRESS:1433/eturesults'
.\scripts\connect_mssql.ps1
```

## Using the Helper Script

The `scripts/connect_mssql.ps1` script automates the connection setup:

```powershell
# Set the connection string in your current PowerShell session
$env:MSSQL_DATABASE_URL = 'mssql://sa:YourPassword@localhost\SQLEXPRESS:1433/eturesults'

# Run the helper script
.\scripts\connect_mssql.ps1
```

The script will:
1. Check that pyodbc and django-mssql-backend are installed
2. Verify the SQL Server connection
3. Run migrations to create tables
4. Display next steps

## Troubleshooting

### Issue: "ODBC Driver 17 for SQL Server not found"
**Solution**: Download and install the ODBC Driver from Microsoft:
https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server

### Issue: "Login failed for user 'sa'"
**Solution**: 
- Verify your password is correct
- Check that SQL Server is running
- Ensure the user account has permission to create databases

### Issue: "Connection timeout" or "Cannot connect"
**Solution**:
- Verify SQL Server is running: Open SQL Server Configuration Manager
- Check firewall: Allow port 1433 (or your custom port) in Windows Firewall
- Try connecting with SSMS first to confirm connectivity

### Issue: "Database 'eturesults' does not exist"
**Solution**: Create the database manually via SSMS or using the `CREATE DATABASE` command shown in Step 3

### Issue: Migrations fail
**Solution**:
- Check the error message for specific details
- Ensure the database user has permission to create tables
- Verify the database is empty or has compatible schema

## Environment Variable Examples

### Local SQL Server with SQLEXPRESS:
```powershell
mssql://sa:YourPassword@localhost\SQLEXPRESS:1433/eturesults
```

### Local SQL Server named instance:
```powershell
mssql://sa:YourPassword@COMPUTER_NAME\INSTANCE:1433/eturesults
```

### Remote SQL Server:
```powershell
mssql://username:password@192.168.1.100:1433/eturesults
```

### SQL Server with Windows Authentication (not yet supported; use SQL auth for now):
Currently, only SQL Server Authentication (username/password) is supported via connection strings.

## Production Considerations

- Set `DEBUG = False` in `settings.py` before deploying
- Use strong passwords for database users
- Restrict database user permissions (avoid using `sa` account in production)
- Use a proper WSGI server (gunicorn, etc.) behind nginx
- Configure SSL/TLS for database connections
- Regularly backup your database
- Enable SQL Server firewall rules appropriately

## More Information

- Django MSSQL Backend: https://github.com/ESSolutions/django-mssql-backend
- SQL Server ODBC Driver: https://learn.microsoft.com/en-us/sql/connect/odbc/windows/
- Django Database Documentation: https://docs.djangoproject.com/en/5.2/ref/settings/#databases
