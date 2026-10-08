# Render a .qmd (or .md) working document to a self-contained HTML file next to the source.
# Usage: .\scripts\render_doc.ps1 Docs\working_doc_example.qmd [-To html|pdf|docx]
param(
    [Parameter(Mandatory = $true)][string]$Path,
    [string]$To = "html"
)
$repo = Split-Path -Parent $PSScriptRoot
$env:QUARTO_PYTHON = Join-Path $repo ".venv\Scripts\python.exe"
Push-Location $repo
try {
    quarto render $Path --to $To
} finally {
    Pop-Location
}
