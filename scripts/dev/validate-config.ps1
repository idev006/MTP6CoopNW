[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
$repoRoot = Resolve-Path (Join-Path $PSScriptRoot '..\..')
Push-Location $repoRoot

try {
    @'
from pathlib import Path
import tomllib

paths = sorted(Path("config").glob("*.example.toml"))
if not paths:
    raise SystemExit("No example TOML files found.")

for path in paths:
    with path.open("rb") as handle:
        data = tomllib.load(handle)
    if data.get("schema_version") != 1:
        raise SystemExit(f"{path}: expected schema_version = 1")
    print(f"OK {path}")
'@ | python -

    if ($LASTEXITCODE -ne 0) {
        throw "TOML validation failed."
    }
}
finally {
    Pop-Location
}
