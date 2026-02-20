#=======================================================
# Python Ocağı - Windows Otomatik Kurulum ve Başlatma Betiği
#=======================================================

# NOT: Bu dosyayı GitHub'a yüklemeden önce kendi GitHub bilgilerinizi aşağıya giriniz.
$REPO_OWNER = "python-ocagi"  # <-- KENDI KULLANICI ADINIZI BURAYA YAZIN
$REPO_NAME = "python-ocagi"   # <-- GITHUB REPO ADINIZ
$BRANCH = "main"              # Default şube adı

# Değiştirmemeniz gereken URL ve Dizinler
$ZIP_URL = "https://github.com/$REPO_OWNER/$REPO_NAME/archive/refs/heads/$BRANCH.zip"
$DesktopPath = [Environment]::GetFolderPath("Desktop")
$AppFolder = Join-Path $DesktopPath "Python Ocagi"
$ShortcutPath = Join-Path $DesktopPath "PYTHON OCAGINA GIR.bat"
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

# 3. Kisa Yol Olustur (Masaustu `.bat`)
Write-Host "Masaustu kisayolu ayarlaniyor..." -ForegroundColor Cyan
$ShortcutContent = @"
@echo off
color 0B
echo =========================================
echo Python Ocagi Guncelleniyor...
echo Lutfen bekleyin... (Internet baglantisina gore degisir)
echo =========================================
powershell -Command "`$ProgressPreference = 'SilentlyContinue'; Invoke-WebRequest -Uri '$ZIP_URL' -OutFile '%TEMP%\app_update.zip' -UseBasicParsing; if (Test-Path '%TEMP%\app_extracted') { Remove-Item -Path '%TEMP%\app_extracted' -Recurse -Force }; Expand-Archive -Path '%TEMP%\app_update.zip' -DestinationPath '%TEMP%\app_extracted' -Force; Copy-Item -Path '%TEMP%\app_extracted\$REPO_NAME-$BRANCH\*' -Destination '%USERPROFILE%\Desktop\Python Ocagi' -Recurse -Force | Out-Null"
echo.
echo Guncelleme tamamlandi. Uygulama baslatiliyor!
echo.
cd /d "%USERPROFILE%\Desktop\Python Ocagi"
py -3.13 main.py
if errorlevel 1 (
   echo Baslatma hatasi! Python 3.13 launcher calismadi, genel isimle deneniyor...
   python main.py
)
"@

Set-Content -Path $ShortcutPath -Value $ShortcutContent -Encoding UTF8

# 4. Kaldirma Dosyasi Olustur
Write-Host "Kaldırma aracı hazirlaniyor..." -ForegroundColor Cyan
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
echo Siliniyor...
rd /s /q "%USERPROFILE%\Desktop\Python Ocagi"
del "%USERPROFILE%\Desktop\PYTHON OCAGINA GIR.bat"
rd /s /q "%APPDATA%\python_ocagi"
rd /s /q "%USERPROFILE%\.python_ocagi"
echo.
echo Kaldirma islemei tamamanlandi. Bu pencere otomatik kapanacak.
ping 127.0.0.1 -n 3 > nul
(goto) 2>nul & del "%~f0" & rd /s /q "%~dp0"
"@
Set-Content -Path $UninstallPath -Value $UninstallScript -Encoding UTF8

Write-Host ""
Write-Host "=========================================" -ForegroundColor Green
Write-Host "KURULUM TAMAMLANDI!" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Green
Write-Host "Uygulamayi hemen baslatmak uzere masaustunuzdeki dosyaya ulasiliyor..." -ForegroundColor Cyan
Start-Sleep -Seconds 2

# 5. Ilk Indirme (Kisa yolu cagirarak yapalim)
Start-Process -FilePath $ShortcutPath
