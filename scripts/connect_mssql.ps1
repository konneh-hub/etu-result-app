# Connect Django project to SQL Server and run migrations
# SQL Server format examples:
#   mssql://username:password@server:port/database
#   mssql://username:password@server/database (uses default port 1433)
#
# USAGE (as Administrator):
#   $env:MSSQL_DATABASE_URL = 'mssql://sa:YourPassword@localhost/eturesults'
#   .\scripts\connect_mssql.ps1

param(
    [string]$MssqlUrl = $env:MSSQL_DATABASE_URL,
    [string]$Driver = $env:MSSQL_DRIVER,
    [switch]$SkipMigrate = $false,
    [switch]$StartServer = $false
)

if (-not $MssqlUrl) {
    Write-Host "ERROR: MSSQL_DATABASE_URL environment variable not set."
    Write-Host ""
    Write-Host "Usage:"
    Write-Host '  $env:MSSQL_DATABASE_URL = "mssql://username:password@server:port/database"'
    Write-Host "  .\scripts\connect_mssql.ps1"
    Write-Host ""
    Write-Host "Example:"
    Write-Host '  $env:MSSQL_DATABASE_URL = "mssql://sa:MyPassword@localhost/eturesults"'
    Write-Host "  .\scripts\connect_mssql.ps1"
    Exit 1
}

Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "ETU Results - SQL Server Connection Setup" -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan

Write-Host ""
Write-Host "[1] Checking dependencies..." -ForegroundColor Yellow

# Check if pyodbc and django-mssql-backend are installed
try {
    python -c "import pyodbc; import mssql" -ErrorAction Stop 2>$null
    Write-Host "    ✓ pyodbc and django-mssql-backend are installed" -ForegroundColor Green
} catch {
    Write-Host "    ✗ Dependencies not found. Installing..." -ForegroundColor Yellow
    pip install pyodbc "django-mssql-backend>=2.8.1"
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to install dependencies."
        Exit 1
    }
    Write-Host "    ✓ Dependencies installed" -ForegroundColor Green
}

Write-Host ""
Write-Host "[2] Verifying SQL Server connection..." -ForegroundColor Yellow
Write-Host "    URL: $MssqlUrl" -ForegroundColor Gray

# Parse the connection string and test connectivity
$testScript = @"
import os
os.environ['MSSQL_DATABASE_URL'] = r'$MssqlUrl'
import django
from django.conf import settings
if not settings.configured:
    import sys
    sys.path.insert(0, '.')
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ETU_Ruslts.settings')
    django.setup()

from django.db import connection
try:
    with connection.cursor() as cursor:
        cursor.execute('SELECT 1')
    print('✓ Connection successful')
except Exception as e:
    print(f'✗ Connection failed: {e}')
    sys.exit(1)
"@

python -c $testScript
if ($LASTEXITCODE -ne 0) {
    Write-Error "Could not connect to SQL Server. Check the connection string and server."
    Exit 1
}
Write-Host "    ✓ SQL Server is reachable" -ForegroundColor Green

Write-Host ""
Write-Host "[3] Running migrations..." -ForegroundColor Yellow

# Run migrations
if (-not $SkipMigrate) {
    python manage.py migrate --settings=ETU_Ruslts.settings
    if ($LASTEXITCODE -eq 0) {
        Write-Host "    ✓ Migrations completed successfully" -ForegroundColor Green
    } else {
        Write-Error "Migrations failed. Check the error messages above."
        Exit 1
    }
} else {
    Write-Host "    (skipped per request)" -ForegroundColor Gray
}

Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "✓ SQL Server connection setup completed successfully!" -ForegroundColor Green
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan

Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Start the dev server:"
Write-Host "     python manage.py runserver"
Write-Host ""
Write-Host "  2. To make the env var persistent (optional):"
Write-Host "     setx MSSQL_DATABASE_URL `"$MssqlUrl`""
Write-Host ""
Write-Host "  3. Open the app: http://etusl_resultapp:8000"
Write-Host ""
