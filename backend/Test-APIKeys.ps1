# ============================
# FUNCTION: Load .env file
# ============================
function Load-EnvFile {
    param([string]$Path)

    if (-Not (Test-Path $Path)) {
        Write-Host ".env file not found at $Path"
        exit 1
    }

    $lines = Get-Content $Path | Where-Object { $_ -match "=" -and $_ -notmatch "^#" }

    foreach ($line in $lines) {
        $parts = $line -split "=", 2
        $name = $parts[0].Trim()
        $value = $parts[1].Trim()
        Set-Item -Path "Env:$name" -Value $value
    }

    Write-Host ".env loaded successfully."
}

# ============================
# FUNCTION: Test OpenAI Key
# ============================
function Test-OpenAIKey {
    $key = $env:OPENAI_API_KEY
    if (-not $key) {
        Write-Host "OPENAI_API_KEY is missing in .env"
        return
    }

    Write-Host "`n=== Testing OpenAI API Key ==="

    $headers = @{
        "Authorization" = "Bearer $key"
        "Content-Type"  = "application/json"
    }

    $body = @{
        model = "gpt-4o-mini"
        messages = @(
            @{
                role = "user"
                content = "Test message"
            }
        )
    } | ConvertTo-Json -Depth 5

    try {
        $response = Invoke-RestMethod `
            -Uri "https://api.openai.com/v1/chat/completions" `
            -Method Post `
            -Headers $headers `
            -Body $body

        if ($response.id) {
            Write-Host "OpenAI Key VALID"
        }
    }
    catch {
        $msg = $_.Exception.Message
        if ($msg -match "401") {
            Write-Host "OpenAI Key INVALID (401 Unauthorized)"
        }
        elseif ($msg -match "429") {
            Write-Host "OpenAI Key VALID but rate limited (429)"
        }
        else {
            Write-Host "OpenAI Test Failed: $msg"
        }
    }
}

# ============================
# FUNCTION: Test Google Maps Key
# ============================
function Test-GoogleMapsKey {
    $key = $env:GOOGLE_MAPS_API_KEY
    if (-not $key) {
        Write-Host "GOOGLE_MAPS_API_KEY is missing in .env"
        return
    }

    Write-Host "`n=== Testing Google Maps API Key ==="

    $query = [System.Web.HttpUtility]::UrlEncode("pharmacy near Cherating")
    $location = "4.1291,103.4057"  # Club Med Cherating

    $url = "https://maps.googleapis.com/maps/api/place/textsearch/json?query=$query`&location=$location`&radius=5000`&key=$key"

    try {
        $response = Invoke-RestMethod -Uri $url -Method Get

        if ($response.status -eq "OK") {
            Write-Host "Google Maps Key VALID"
            Write-Host ("Top result: " + $response.results[0].name)
        }
        elseif ($response.status -eq "REQUEST_DENIED") {
            Write-Host "Google Key INVALID (REQUEST_DENIED)"
            Write-Host ("Error: " + $response.error_message)
        }
        elseif ($response.status -eq "OVER_QUERY_LIMIT") {
            Write-Host "Google Key VALID but over query limit"
        }
        else {
            Write-Host ("Unexpected Google API Status: " + $response.status)
        }
    }
    catch {
        Write-Host "Google Maps Test Failed: $($_.Exception.Message)"
    }
}

# ============================
# MAIN EXECUTION
# ============================

$envPath = ".\.env"

Load-EnvFile -Path $envPath

Test-OpenAIKey
Test-GoogleMapsKey

Write-Host "`n=== API Key Tests Complete ==="
