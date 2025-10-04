Write-Host "=== Testing Backend Security Headers (http://localhost:8000) ===" -ForegroundColor Cyan
Write-Host ""

try {
    $response = Invoke-WebRequest -Method Head -Uri http://localhost:8000/ -ErrorAction Stop
    
    Write-Host "Status Code:" $response.StatusCode -ForegroundColor Green
    Write-Host ""
    Write-Host "Security Headers:" -ForegroundColor Yellow
    Write-Host "  Content-Security-Policy:" $response.Headers['Content-Security-Policy']
    Write-Host "  X-Frame-Options:" $response.Headers['X-Frame-Options']
    Write-Host "  X-Content-Type-Options:" $response.Headers['X-Content-Type-Options']
    Write-Host "  Referrer-Policy:" $response.Headers['Referrer-Policy']
    Write-Host ""
    
    Write-Host "All Headers:" -ForegroundColor Yellow
    $response.Headers | Format-Table -AutoSize
    
} catch {
    Write-Host "Error connecting to backend:" $_.Exception.Message -ForegroundColor Red
}

Write-Host ""
Write-Host "=== Testing API Endpoint ===" -ForegroundColor Cyan
try {
    $apiResponse = Invoke-WebRequest -Method Get -Uri http://localhost:8000/docs -ErrorAction Stop
    Write-Host "API Docs Status:" $apiResponse.StatusCode -ForegroundColor Green
} catch {
    Write-Host "Error:" $_.Exception.Message -ForegroundColor Red
}
