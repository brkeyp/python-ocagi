#=======================================================
# Python Ocağı - Windows Otomatik Kurulum ve Başlatma Betiği
#=======================================================

# TLS 1.2 Zorunlulugu (Geriye Donuk Uyumluluk)
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

# NOT: Bu dosyayı GitHub'a yüklemeden önce kendi GitHub bilgilerinizi aşağıya giriniz.
$REPO_OWNER = "brkeyp"  # <-- KENDI KULLANICI ADINIZI BURAYA YAZIN
$REPO_NAME = "python-ocagi"   # <-- GITHUB REPO ADINIZ
$BRANCH = "main"              # Default şube adı

# Değiştirmemeniz gereken URL ve Dizinler
$ZIP_URL = "https://github.com/$REPO_OWNER/$REPO_NAME/archive/refs/heads/$BRANCH.zip"
$DesktopPath = [Environment]::GetFolderPath("Desktop")
$AppFolder = Join-Path $DesktopPath "Python Ocagi"
$ShortcutPath = Join-Path $DesktopPath "PYTHON OCAGINA GIR.lnk"
$UninstallPath = Join-Path $AppFolder "Uygulamayi Kaldir.bat"

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Python Ocagi Kurulumu Basliyor...        " -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

# 1. Klasoru Olustur
if (-not (Test-Path -Path $AppFolder)) {
    New-Item -ItemType Directory -Force -Path $AppFolder | Out-Null
    Write-Host "Masaustunde 'Python Ocagi' klasoru olusturuldu." -ForegroundColor Green
}

# Baslatma motorunu (baslat.ps1) indir (Ilk calistirma icin sart)
Write-Host "Baslatma motoru indiriliyor..." -ForegroundColor Cyan
$BaslatUrl = "https://raw.githubusercontent.com/$REPO_OWNER/$REPO_NAME/$BRANCH/baslat.ps1"
$BaslatPath = Join-Path $AppFolder "baslat.ps1"
Invoke-WebRequest -Uri $BaslatUrl -OutFile $BaslatPath -UseBasicParsing

# 2. Python Kontrolu
$PythonExists = Get-Command "py" -ErrorAction SilentlyContinue
if (-not $PythonExists) {
    $PythonExists = Get-Command "python" -ErrorAction SilentlyContinue
}

if (-not $PythonExists) {
    Write-Host "Python bulunamadi! Resmi sürüm (3.13) internetten indiriliyor..." -ForegroundColor Yellow
    Write-Host "(Bu islem internet hizina bagli olarak birkac dakika surebilir)" -ForegroundColor Yellow
    $InstallerPath = "$env:TEMP\python-3.13.11-amd64.exe"
    Invoke-WebRequest -Uri "https://www.python.org/ftp/python/3.13.11/python-3.13.11-amd64.exe" -OutFile $InstallerPath -UseBasicParsing
    
    Write-Host "Python sessizce kuruluyor. Lutfen pencereyi kapatmayin..." -ForegroundColor Yellow
    # Sessiz kurulum (Path'e ekleme yapmaz, baslaticiyi (py) kurar)
    Start-Process -FilePath $InstallerPath -ArgumentList "/quiet InstallAllUsers=0 PrependPath=0 Include_launcher=1 Include_pip=1" -Wait
    Write-Host "Python basariyla kuruldu!" -ForegroundColor Green
} else {
    Write-Host "Sisteminizde Python yuklu, harika!" -ForegroundColor Green
}

# 3. Kisa Yol Olustur (Masaustu .lnk)
# .lnk dosyası PowerShell'i doğrudan açar → cmd.exe devre dışı
# → BOM sorunu yok, "Terminate batch job" sorunu yok
Write-Host "Masaustu kisayolu ayarlaniyor..." -ForegroundColor Cyan
$WScriptShell = New-Object -ComObject WScript.Shell
$Shortcut = $WScriptShell.CreateShortcut($ShortcutPath)
$Shortcut.TargetPath = "powershell.exe"
$Shortcut.Arguments = "-NoProfile -ExecutionPolicy Bypass -File `"$AppFolder\baslat.ps1`""
$Shortcut.WorkingDirectory = $AppFolder
$Shortcut.Description = "Python Ocagi - Yazarak Ogrenme"
$Shortcut.Save()

# 4. Kaldirma Dosyasi Olustur
# Strateji: .bat → PowerShell'e silme işini devreder → exit ile cmd kapanır
# → klasör kilidi açılır → PowerShell 1 sn sonra siler
Write-Host "Kaldirma araci hazirlaniyor..." -ForegroundColor Cyan
$LnkName = "PYTHON OCAGINA GIR.lnk"
$UninstallScript = @"
@echo off
title Python Ocagi - Kaldirma
color 4F
echo =======================================================
echo DIKKAT: Python Ocagi tamamen siliniyor!
echo Ilerlemeniz, skorlariniz ve projenin butun dosyalari yok olacak.
echo.
echo IPTAL ETMEK ICIN SU AN BU PENCEREYI KAPATIN.
echo DEVAM ETMEK ICIN:
pause
echo =======================================================
echo Kaldirma islemi baslatildi...
start "" powershell -NoProfile -ExecutionPolicy Bypass -Command "Start-Sleep -Seconds 1; Write-Host 'Dosyalar siliniyor...' -ForegroundColor Red; Remove-Item -Path (Join-Path ([Environment]::GetFolderPath('Desktop')) 'Python Ocagi') -Recurse -Force -ErrorAction SilentlyContinue; Remove-Item -Path (Join-Path ([Environment]::GetFolderPath('Desktop')) '$LnkName') -Force -ErrorAction SilentlyContinue; Remove-Item -Path (Join-Path `$env:APPDATA 'python_ocagi') -Recurse -Force -ErrorAction SilentlyContinue; Remove-Item -Path (Join-Path `$HOME '.python_ocagi') -Recurse -Force -ErrorAction SilentlyContinue; Write-Host '' ; Write-Host 'Kaldirma tamamlandi! Bu pencere kapanacak.' -ForegroundColor Green; Start-Sleep -Seconds 3"
exit
"@
# BOM'suz yaz (kritik! BOM .bat dosyalarını bozar)
[System.IO.File]::WriteAllText($UninstallPath, $UninstallScript, [System.Text.UTF8Encoding]::new($false))

Write-Host ""
Write-Host "=========================================" -ForegroundColor Green
Write-Host "KURULUM TAMAMLANDI!" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Green
Write-Host "Uygulamayi hemen baslatmak uzere masaustunuzdeki dosyaya ulasiliyor..." -ForegroundColor Cyan
Start-Sleep -Seconds 2

# 5. Ilk Indirme (Kisayolu cagirarak yapalim)
Start-Process -FilePath $ShortcutPath
Start-Sleep -Seconds 1

# Kurulum penceresini temiz kapat (Stop-Process yerine exit → "process exited" hatası yok)
exit 0
