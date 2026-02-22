#=======================================================
# Python Ocağı - Windows Başlatma ve Güncelleme Betiği
# Her çift tıklamada çalışır: günceller + uygulamayı başlatır
#=======================================================

# TLS 1.2 Zorunlulugu (Geriye Donuk Uyumluluk)
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

# Pencere başlığı
$Host.UI.RawUI.WindowTitle = "PYTHON OCAGI - YAZARAK OGRENME"

# Repo bilgileri
$REPO_OWNER = "brkeyp"
$REPO_NAME  = "python-ocagi"
$BRANCH     = "main"

$ZIP_URL     = "https://github.com/$REPO_OWNER/$REPO_NAME/archive/refs/heads/$BRANCH.zip"
$AppFolder   = Join-Path ([Environment]::GetFolderPath("Desktop")) "Python Ocagi"
$TempZip     = Join-Path $env:TEMP "app_update.zip"
$TempExtract = Join-Path $env:TEMP "app_extracted"

# --- GÜNCELLEME ---
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Python Ocagi Guncelleniyor..."            -ForegroundColor Cyan
Write-Host "Lutfen bekleyin... (Internet baglantisina gore degisir)" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan

try {
    $ProgressPreference = 'SilentlyContinue'
    Invoke-WebRequest -Uri $ZIP_URL -OutFile $TempZip -UseBasicParsing

    if (Test-Path $TempExtract) {
        Remove-Item -Path $TempExtract -Recurse -Force
    }

    Expand-Archive -Path $TempZip -DestinationPath $TempExtract -Force
    
    # File Lock (Kilit) hatasini onlemek icin calisan baslat.ps1'in uzerine yazmayi engelle
    Remove-Item -Path (Join-Path $TempExtract "$REPO_NAME-$BRANCH\baslat.ps1") -Force -ErrorAction SilentlyContinue
    
    Copy-Item -Path (Join-Path $TempExtract "$REPO_NAME-$BRANCH\*") -Destination $AppFolder -Recurse -Force | Out-Null

    Write-Host ""
    Write-Host "Guncelleme tamamlandi. Uygulama baslatiliyor!" -ForegroundColor Green
    Write-Host ""
} catch {
    Write-Host ""
    Write-Host "Guncelleme sirasinda hata olustu: $_" -ForegroundColor Yellow
    Write-Host "Mevcut surumle devam ediliyor..." -ForegroundColor Yellow
    Write-Host ""
}

# --- UYGULAMA BAŞLAT ---
Set-Location $AppFolder

# Önce py launcher ile Python 3.13'ü dene, başarısız olursa genel python'u dene
& py -3.13 main.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "py -3.13 calismadi, python ile deneniyor..." -ForegroundColor Yellow
    & python main.py
}
