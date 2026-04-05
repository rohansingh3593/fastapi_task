$ENV_NAME = "venv"
$REQ_FILE = "requirements.txt"

Write-Host "Setting up Stealth Environment..."

if (!(Test-Path $ENV_NAME)) {
    Write-Host "Creating virtual environment..."
    py -3.10 -m venv $ENV_NAME
} else {
    Write-Host "Virtual environment already exists. Skipping creation."
}

Write-Host "Activating virtual environment..."
& "$ENV_NAME\Scripts\Activate.ps1"

Write-Host "Upgrading pip (only first time needed)..."
python -m pip install --upgrade pip

if (Test-Path $REQ_FILE) {
    Write-Host "Installing dependencies..."
    pip install -r $REQ_FILE `
        --no-build-isolation
} else {
    Write-Host "$REQ_FILE not found. Skipping."
}


Write-Host ""
Write-Host "Environment ready."