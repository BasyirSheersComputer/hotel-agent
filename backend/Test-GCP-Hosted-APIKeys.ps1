# =======================================================
# FUNCTION: Load multi-key secret from Google Secret Manager
# =======================================================

function Load-GCPSecretFile {
    param(
        [string]$SecretName
    )

    try {
        # Retrieve full secret content
        $raw = gcloud secrets versions access latest --secret=$SecretName 2>$null

        if (-not $raw) {
            Write-Host "Failed to load secret: $SecretName"
            exit 1
        }

        Write-Host "Loaded secret: $SecretName"
        return $raw
    }
    catch {
        Write-Host "Error retrieving secret $SecretName : $($_.Exception.Message)"
        exit 1
    }
}


# =======================================================
# FUNCTION: Parse KEY=VALUE pairs from secret text
# =======================================================

function Parse-SecretContent {
    param([string]$Content)

    $lines = $Content -split "`n"

    $dict = @{}

    foreach ($line in $lines) {
        if ($line -match "=") {
            $pair = $line -split "=", 2
            $key = $pair[0].Trim()
            $val = $pair[1].Trim()
            $dict[$key] = $val
        }
    }

    return $dict
}


# =======================================================
# TEST OPENAI KEY
# =======================================================

function Test-OpenAIKey {
    param([string]$Key)

    Write-Host "`n=== Testing OpenAI API Key ==="

    $headers = @{
        "Authorization" = "Bearer $Key"
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
            Write-Host ("Response: " + $response.choices[0].message.content)
        }
        else {
            Write-Host "OpenAI returned unexpected response."
        }
    }
    catch {
        $err = $_.Exception.Message

        if ($err -match "401") {
            Write-Host "OpenAI Key INVALID (401 Unauthorized)"
        }
        elseif ($err -match "429") {
            Write-Host "OpenAI Key VALID but rate limited (429)"
        }
        else {
            Write-Host "OpenAI Test Failed: $err"
        }
    }
}


# =======================================================
# TEST GOOGLE MAPS API KEY
# =======================================================

function Test-GoogleMapsKey {
    param([string]$Key)

    Write-Host "`n=== Testing Google Maps Places API Key ==="

    $query = [System.Web.HttpUtility]::UrlEncode("pharmacy near Cherating")
    $location = "4.1291,103.4057"

    $url = "https://maps.googleapis.com/maps/api/place/textsearch/json?query=$query`&location=$location`&radius=5000`&key=$Key"

    try {
        $response = Invoke-RestMethod -Uri $url -Method Get

        if ($response.status -eq "OK") {
            Write-Host "Google Maps Key VALID"
            Write-Host ("Top result: " + $response.results[0].name)
        }
        elseif ($response.status -eq "REQUEST_DENIED") {
            Write-Host "Google Maps Key INVALID (REQUEST_DENIED)"
            Write-Host ("Error: " + $response.error_message)
        }
        elseif ($response.status -eq "OVER_QUERY_LIMIT") {
            Write-Host "Google Maps Key VALID but over query limit"
        }
        else {
            Write-Host ("Unexpected Google API Status: " + $response.status)
        }
    }
    catch {
        Write-Host "Google Maps Test Failed: $($_.Exception.Message)"
    }
}


# =======================================================
# MAIN EXECUTION
# =======================================================

Write-Host "`n=== Loading hotel-agent-secret-001 ==="

$secretText = Load-GCPSecretFile -SecretName "hotel-agent-secret-001"

$secretDict = Parse-SecretContent -Content $secretText

$OPENAI_KEY  = $secretDict["OPENAI_API_KEY"]
$MAPS_KEY    = $secretDict["GOOGLE_MAPS_API_KEY"]

if (-not $OPENAI_KEY) {
    Write-Host "OPENAI_API_KEY missing in secret."
    exit 1
}

if (-not $MAPS_KEY) {
    Write-Host "GOOGLE_MAPS_API_KEY missing in secret."
    exit 1
}

Write-Host "Secrets parsed successfully."


# Run tests
Test-OpenAIKey -Key $OPENAI_KEY
Test-GoogleMapsKey -Key $MAPS_KEY

Write-Host "`n=== All Tests Complete ==="
