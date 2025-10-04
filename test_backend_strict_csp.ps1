Write-Host "=== Testing Backend Strict CSP (http://localhost:8000) ===" -ForegroundColor Cyan
Write-Host ""

try {
    Write-Host "1. Testing ROOT path (should have STRICT CSP):" -ForegroundColor Yellow
    $response = Invoke-WebRequest -Method Head -Uri http://localhost:8000/ -ErrorAction Stop
    Write-Host "  Status Code:" $response.StatusCode -ForegroundColor Green
    Write-Host "  CSP:" $response.Headers['Content-Security-Policy']
    Write-Host "  X-Frame-Options:" $response.Headers['X-Frame-Options']
    Write-Host "  X-Content-Type-Options:" $response.Headers['X-Content-Type-Options']
    Write-Host "  Referrer-Policy:" $response.Headers['Referrer-Policy']
    
    # Verificar que NO tiene unsafe-inline ni unsafe-eval
    $csp = $response.Headers['Content-Security-Policy']
    if ($csp -match "unsafe-inline" -or $csp -match "unsafe-eval") {
        Write-Host "  WARNING: CSP contains unsafe-* directives!" -ForegroundColor Red
    } else {
        Write-Host "  OK: CSP is strict (no unsafe-inline/unsafe-eval)" -ForegroundColor Green
    }
    
    Write-Host ""
    Write-Host "2. Testing /docs path (should have RELAXED CSP for Swagger):" -ForegroundColor Yellow
    $docsResponse = Invoke-WebRequest -Method Head -Uri http://localhost:8000/docs -ErrorAction Stop
    Write-Host "  Status Code:" $docsResponse.StatusCode -ForegroundColor Green
    Write-Host "  CSP:" $docsResponse.Headers['Content-Security-Policy']
    
    $docsCsp = $docsResponse.Headers['Content-Security-Policy']
    if ($docsCsp -match "unsafe-inline") {
        Write-Host "  OK: /docs CSP allows unsafe-inline for Swagger UI" -ForegroundColor Green
    } else {
        Write-Host "  WARNING: /docs CSP should allow unsafe-inline" -ForegroundColor Yellow
    }
    
} catch {
    Write-Host "Error:" $_.Exception.Message -ForegroundColor Red
}

Write-Host ""
Write-Host "=== CSP Directives Check ===" -ForegroundColor Cyan
Write-Host "Looking for required directives in ROOT CSP..."
$rootCsp = $response.Headers['Content-Security-Policy']
$requiredDirectives = @('default-src', 'script-src', 'style-src', 'img-src', 'font-src', 'connect-src', 'object-src', 'base-uri', 'form-action', 'frame-ancestors', 'frame-src')

foreach ($directive in $requiredDirectives) {
    if ($rootCsp -match $directive) {
        Write-Host "  [OK] $directive" -ForegroundColor Green
    } else {
        Write-Host "  [MISSING] $directive" -ForegroundColor Red
    }
}
