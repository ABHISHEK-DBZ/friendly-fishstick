# Setup Vercel Environment Variables
# Run this script to configure environment variables for Vercel deployment

Write-Host "Setting up Vercel environment variables..." -ForegroundColor Cyan

# Load .env file
if (Test-Path ".env") {
    Get-Content ".env" | ForEach-Object {
        if ($_ -match '^GEMINI_API_KEY=(.+)$') {
            $apiKey = $matches[1]
            Write-Host "Found GEMINI_API_KEY in .env" -ForegroundColor Green
            
            # Add to Vercel (you'll need to confirm in the prompts)
            Write-Host "Adding GEMINI_API_KEY to Vercel..." -ForegroundColor Yellow
            Write-Host "Select: production, preview, development (all three)" -ForegroundColor Yellow
            
            # Create a temporary file with the API key
            $apiKey | Out-File -FilePath "temp_key.txt" -NoNewline
            
            # Add to Vercel
            Get-Content "temp_key.txt" | vercel env add GEMINI_API_KEY
            
            # Clean up
            Remove-Item "temp_key.txt" -Force
        }
    }
} else {
    Write-Host "Error: .env file not found" -ForegroundColor Red
    exit 1
}

# Also add SECRET_KEY for Flask
Write-Host ""
Write-Host "Adding SECRET_KEY for Flask..." -ForegroundColor Yellow
$secretKey = -join ((65..90) + (97..122) + (48..57) | Get-Random -Count 32 | ForEach-Object {[char]$_})
Write-Host "Generated SECRET_KEY: $secretKey" -ForegroundColor Green
$secretKey | Out-File -FilePath "temp_secret.txt" -NoNewline
Get-Content "temp_secret.txt" | vercel env add SECRET_KEY
Remove-Item "temp_secret.txt" -Force

# Add FLASK_ENV
Write-Host ""
Write-Host "Adding FLASK_ENV=production..." -ForegroundColor Yellow
"production" | Out-File -FilePath "temp_env.txt" -NoNewline
Get-Content "temp_env.txt" | vercel env add FLASK_ENV
Remove-Item "temp_env.txt" -Force

Write-Host ""
Write-Host "Environment variables setup complete!" -ForegroundColor Green
Write-Host "Now run: vercel --prod" -ForegroundColor Cyan
