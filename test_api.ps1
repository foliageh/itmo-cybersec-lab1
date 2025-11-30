# PowerShell скрипт для тестирования API
# Использование: .\test_api.ps1

$BASE_URL = "http://localhost:5000"

Write-Host "=== Тестирование защищенного REST API ===" -ForegroundColor Cyan
Write-Host ""

# 1. Регистрация нового пользователя
Write-Host "1. Регистрация пользователя 'testuser'..." -ForegroundColor Yellow
$registerBody = @{
    username = "testuser"
    password = "testpass123"
} | ConvertTo-Json

$registerResponse = Invoke-RestMethod -Uri "$BASE_URL/auth/register" -Method POST -Body $registerBody -ContentType "application/json"
Write-Host "Ответ: $($registerResponse | ConvertTo-Json)" -ForegroundColor Green
Write-Host ""

# 2. Попытка регистрации с тем же именем
Write-Host "2. Попытка регистрации с существующим именем..." -ForegroundColor Yellow
try {
    $registerDuplicate = Invoke-RestMethod -Uri "$BASE_URL/auth/register" -Method POST -Body $registerBody -ContentType "application/json" -ErrorAction Stop
    Write-Host "Ответ: $($registerDuplicate | ConvertTo-Json)" -ForegroundColor Green
} catch {
    Write-Host "Ошибка (ожидаемо): $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# 3. Логин с правильными учетными данными
Write-Host "3. Логин пользователя 'testuser'..." -ForegroundColor Yellow
$loginBody = @{
    username = "testuser"
    password = "testpass123"
} | ConvertTo-Json

$loginResponse = Invoke-RestMethod -Uri "$BASE_URL/auth/login" -Method POST -Body $loginBody -ContentType "application/json"
$token = $loginResponse.token
Write-Host "Ответ: $($loginResponse | ConvertTo-Json)" -ForegroundColor Green
Write-Host "Полученный токен: $($token.Substring(0, [Math]::Min(50, $token.Length)))..." -ForegroundColor Cyan
Write-Host ""

# 4. Попытка доступа к защищенному эндпоинту без токена
Write-Host "4. Попытка доступа к /api/data без токена (должна вернуть ошибку)..." -ForegroundColor Yellow
try {
    $noTokenResponse = Invoke-RestMethod -Uri "$BASE_URL/api/data" -Method GET -ErrorAction Stop
    Write-Host "Ответ: $($noTokenResponse | ConvertTo-Json)" -ForegroundColor Green
} catch {
    Write-Host "Ошибка (ожидаемо): $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# 5. Доступ к защищенному эндпоинту с токеном
Write-Host "5. Доступ к /api/data с токеном..." -ForegroundColor Yellow
$headers = @{
    Authorization = "Bearer $token"
}
$withTokenResponse = Invoke-RestMethod -Uri "$BASE_URL/api/data" -Method GET -Headers $headers
Write-Host "Ответ: $($withTokenResponse | ConvertTo-Json)" -ForegroundColor Green
Write-Host ""

# 6. Попытка логина с неправильным паролем
Write-Host "6. Попытка логина с неправильным паролем (должна вернуть ошибку)..." -ForegroundColor Yellow
$wrongPassBody = @{
    username = "testuser"
    password = "wrongpass"
} | ConvertTo-Json

try {
    $wrongPassResponse = Invoke-RestMethod -Uri "$BASE_URL/auth/login" -Method POST -Body $wrongPassBody -ContentType "application/json" -ErrorAction Stop
    Write-Host "Ответ: $($wrongPassResponse | ConvertTo-Json)" -ForegroundColor Green
} catch {
    Write-Host "Ошибка (ожидаемо): $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# 7. Попытка доступа с невалидным токеном
Write-Host "7. Попытка доступа с невалидным токеном (должна вернуть ошибку)..." -ForegroundColor Yellow
$invalidHeaders = @{
    Authorization = "Bearer invalid_token_here"
}
try {
    $invalidTokenResponse = Invoke-RestMethod -Uri "$BASE_URL/api/data" -Method GET -Headers $invalidHeaders -ErrorAction Stop
    Write-Host "Ответ: $($invalidTokenResponse | ConvertTo-Json)" -ForegroundColor Green
} catch {
    Write-Host "Ошибка (ожидаемо): $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

Write-Host "=== Тестирование завершено ===" -ForegroundColor Cyan

