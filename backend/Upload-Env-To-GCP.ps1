# =======================================================
# CONFIGURATION
# =======================================================

$EnvFilePath = ".\.env"
$SecretName = "hotel-agent-secret-001"   # Change if needed


# =======================================================
# STEP 1 — Validate .env file
# =======================================================

if (-not (Test-Path $EnvFilePath)) {
    Write-Host "ERROR: .env file not found at $EnvFilePath"
    exit 1
}

Write-Host ".env file found. Reading..."

$envContent = Get-Content $EnvFilePath -Raw

if (-not $envContent) {
    Write-Host "ERROR: .env file is empty."
    exit 1
}


# =======================================================
# STEP 2 — Ensure secret exists (if not, create it)
# =======================================================

$existingSecret = gcloud secrets list --filter="name:$SecretName" --format="value(name)"

if (-not $existingSecret) {
    Write-Host "Secret does not exist. Creating: $SecretName"
    gcloud secrets create $SecretName --replication-policy="automatic"
}
else {
    Write-Host "Secret exists: $SecretName"
}


# =======================================================
# STEP 3 — Upload .env as a NEW secret version
# =======================================================

Write-Host "Uploading .env as a new secret version..."

$envContent | Out-File -FilePath "temp-secret.txt" -Encoding ascii

gcloud secrets versions add $SecretName --data-file="temp-secret.txt"

Remove-Item "temp-secret.txt"

Write-Host "Upload complete. Secret updated successfully."


# =======================================================
# STEP 4 — Test reading the secret (for localhost application)
# =======================================================

Write-Host "`nTesting secret read-back:"

$secretData = gcloud secrets versions access latest --secret=$SecretName

Write-Host $secretData
