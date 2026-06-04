# PowerShell script to clean credentials from markdown files
$secrets = @(
    'gpU8Q~4CyGLlKlObUg24hHZ9A8oy8-GVZlqAIbQx',
    '5f727fa8-91c0-441f-b9b2-231aaec4ddce',
    'cff32a4b-02d9-486b-8305-813c570ceb7e',
    'ae9011ed-d52f-44fe-ad7b-1a138904ccf6'
)

Get-ChildItem *.md -File | ForEach-Object {
    $content = Get-Content $_.FullName -Raw
    $modified = $false
    
    if ($content -match 'gpU8Q~4CyGLlKlObUg24hHZ9A8oy8-GVZlqAIbQx') {
        $content = $content -replace 'gpU8Q~4CyGLlKlObUg24hHZ9A8oy8-GVZlqAIbQx', '<REDACTED>'
        $modified = $true
    }
    if ($content -match '5f727fa8-91c0-441f-b9b2-231aaec4ddce') {
        $content = $content -replace '5f727fa8-91c0-441f-b9b2-231aaec4ddce', '<APP_ID>'
        $modified = $true
    }
    if ($content -match 'cff32a4b-02d9-486b-8305-813c570ceb7e') {
        $content = $content -replace 'cff32a4b-02d9-486b-8305-813c570ceb7e', '<SUB_ID>'
        $modified = $true
    }
    if ($content -match 'ae9011ed-d52f-44fe-ad7b-1a138904ccf6') {
        $content = $content -replace 'ae9011ed-d52f-44fe-ad7b-1a138904ccf6', '<TENANT_ID>'
        $modified = $true
    }
    
    if ($modified) {
        Set-Content $_.FullName $content -NoNewline
        Write-Host "[OK] Cleaned $($_.Name)"
    }
}
