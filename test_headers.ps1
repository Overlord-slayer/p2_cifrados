$response = Invoke-WebRequest -Method Head -Uri http://localhost:3000
Write-Host "=== Security Headers Test ==="
Write-Host ""
Write-Host "Content-Security-Policy:" $response.Headers['Content-Security-Policy']
Write-Host "X-Frame-Options:" $response.Headers['X-Frame-Options']
Write-Host "X-Content-Type-Options:" $response.Headers['X-Content-Type-Options']
Write-Host ""
Write-Host "=== Testing /@vite/client route (should be blocked) ==="
try {
    $viteResponse = Invoke-WebRequest -Uri http://localhost:3000/@vite/client -ErrorAction Stop
    Write-Host "Status Code:" $viteResponse.StatusCode
} catch {
    Write-Host "Error (Expected):" $_.Exception.Response.StatusCode.value__
}
