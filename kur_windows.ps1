#=======================================================
# Python Ocağı - Windows Kurulum ve Başlatma Betiği
# İnteraktif menü ile kurulum, direkt kullanım ve kaldırma
#=======================================================

# TLS 1.2 Zorunlulugu (Geriye Donuk Uyumluluk)
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

# GitHub Repo Bilgileri
$REPO_OWNER = "brkeyp"
$REPO_NAME  = "python-ocagi"
$BRANCH     = "main"

# URL ve Dizin Tanimlari
$ZIP_URL      = "https://github.com/$REPO_OWNER/$REPO_NAME/archive/refs/heads/$BRANCH.zip"
$DesktopPath  = [Environment]::GetFolderPath("Desktop")
$AppFolder    = Join-Path $DesktopPath "Python Ocagi"
$ShortcutPath = Join-Path $DesktopPath "PYTHON OCAGINA GIR.lnk"
$UninstallPath = Join-Path $AppFolder "Uygulamayi Kaldir.bat"
$HiddenAppDir = Join-Path $env:APPDATA "python_ocagi\app"

# Gecici dosya yollari
$TempZip     = Join-Path $env:TEMP "python_ocagi_update.zip"
$TempExtract = Join-Path $env:TEMP "python_ocagi_extracted"

# Script-scope Python komutu
$script:PythonCmd = ""

#=======================================================
# YARDIMCI FONKSIYONLAR
#=======================================================

function Read-SingleKey {
    $key = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    return $key
}

function Download-AppTo {
    param([string]$TargetDir)

    if (-not (Test-Path $TargetDir)) {
        New-Item -ItemType Directory -Force -Path $TargetDir | Out-Null
    }

    Write-Host ""
    Write-Host "Uygulama indiriliyor..." -ForegroundColor Cyan
    Write-Host "   (Internet hiziniza gore degisir)" -ForegroundColor DarkGray

    $ProgressPreference = 'SilentlyContinue'

    try {
        Invoke-WebRequest -Uri $ZIP_URL -OutFile $TempZip -UseBasicParsing

        if (Test-Path $TempExtract) {
            Remove-Item -Path $TempExtract -Recurse -Force
        }

        Expand-Archive -Path $TempZip -DestinationPath $TempExtract -Force
        Copy-Item -Path (Join-Path $TempExtract "$REPO_NAME-$BRANCH\*") -Destination $TargetDir -Recurse -Force | Out-Null

        # Temizlik
        Remove-Item -Path $TempZip -Force -ErrorAction SilentlyContinue
        Remove-Item -Path $TempExtract -Recurse -Force -ErrorAction SilentlyContinue

        Write-Host "Indirme tamamlandi." -ForegroundColor Green
    }
    catch {
        Write-Host "Indirme sirasinda hata olustu: $_" -ForegroundColor Yellow
        Write-Host "Mevcut surumle devam ediliyor..." -ForegroundColor Yellow
    }
}

#=======================================================
# PYTHON KONTROL VE KURULUM
#=======================================================

function Show-ManualPythonInstructions {
    Write-Host ""
    Write-Host "Python'u manuel olarak yuklemek icin:" -ForegroundColor Yellow
    Write-Host "  python.org/downloads adresinden Python 3.13 indirin." -ForegroundColor White
    Write-Host "  Kurulum sirasinda 'Add to PATH' secenegini isaretleyin." -ForegroundColor White
    Write-Host ""
    Write-Host "Yukledikten sonra bu komutu tekrar calistirin." -ForegroundColor DarkGray
}

function Install-PythonWithPermission {
    Write-Host ""
    Write-Host "=========================================" -ForegroundColor Red
    Write-Host "Python bulunamadi!" -ForegroundColor Yellow
    Write-Host "=========================================" -ForegroundColor Red
    Write-Host ""
    Write-Host "Bu uygulama calismak icin Python 3.13 gerektirir." -ForegroundColor White
    Write-Host ""
    Write-Host "Otomatik olarak yuklemek ister misiniz?" -ForegroundColor White
    Write-Host ""
    Write-Host "  [E]  Evet, yukle" -ForegroundColor Green
    Write-Host "  [H]  Hayir, kendim yukleyecegim" -ForegroundColor Red
    Write-Host ""
    Write-Host -NoNewline "Seciminiz: " -ForegroundColor Cyan

    $key = Read-SingleKey
    Write-Host ""

    if ($key.Character -match '[EeYy]' -or $key.VirtualKeyCode -eq 13) {
        Write-Host ""
        Write-Host "Python 3.13 internetten indiriliyor..." -ForegroundColor Cyan
        Write-Host "(Bu islem internet hizina bagli olarak birkac dakika surebilir)" -ForegroundColor DarkGray

        # Mimari tespiti
        try {
            $arch = [System.Runtime.InteropServices.RuntimeInformation]::ProcessArchitecture
            if ($arch -eq 'Arm64') {
                $InstallerUrl = "https://www.python.org/ftp/python/3.13.11/python-3.13.11-arm64.exe"
                $InstallerFile = "python-3.13.11-arm64.exe"
            } else {
                $InstallerUrl = "https://www.python.org/ftp/python/3.13.11/python-3.13.11-amd64.exe"
                $InstallerFile = "python-3.13.11-amd64.exe"
            }
        }
        catch {
            # Eski PowerShell surumleri icin fallback
            $InstallerUrl = "https://www.python.org/ftp/python/3.13.11/python-3.13.11-amd64.exe"
            $InstallerFile = "python-3.13.11-amd64.exe"
        }

        $InstallerPath = Join-Path $env:TEMP $InstallerFile

        try {
            $ProgressPreference = 'SilentlyContinue'
            Invoke-WebRequest -Uri $InstallerUrl -OutFile $InstallerPath -UseBasicParsing

            Write-Host ""
            Write-Host "Python sessizce kuruluyor. Lutfen pencereyi kapatmayin..." -ForegroundColor Yellow
            Start-Process -FilePath $InstallerPath -ArgumentList "/quiet InstallAllUsers=0 PrependPath=0 Include_launcher=1 Include_pip=1" -Wait

            # Dogrulama
            $PyCheck = Get-Command "py" -ErrorAction SilentlyContinue
            if ($PyCheck) {
                $script:PythonCmd = "py"
                Write-Host ""
                Write-Host "Python basariyla yuklendi!" -ForegroundColor Green
                return $true
            }

            $PyCheck = Get-Command "python" -ErrorAction SilentlyContinue
            if ($PyCheck) {
                $script:PythonCmd = "python"
                Write-Host ""
                Write-Host "Python basariyla yuklendi!" -ForegroundColor Green
                return $true
            }

            Write-Host "Python kurulumu tamamlandi ancak dogrulanamadi." -ForegroundColor Yellow
            Write-Host "Bu pencereyi kapatip komutu tekrar calistirin." -ForegroundColor Yellow
            pause
            exit 0
        }
        catch {
            Write-Host "Python indirme/kurulum hatasi: $_" -ForegroundColor Red
            Show-ManualPythonInstructions
            pause
            exit 1
        }
    }
    else {
        Show-ManualPythonInstructions
        pause
        exit 0
    }
}

function Test-PythonAvailable {
    # py launcher ile dene
    $PyLauncher = Get-Command "py" -ErrorAction SilentlyContinue
    if ($PyLauncher) {
        $script:PythonCmd = "py"
        return $true
    }

    # python komutu ile dene
    $PythonExe = Get-Command "python" -ErrorAction SilentlyContinue
    if ($PythonExe) {
        $script:PythonCmd = "python"
        return $true
    }

    return $false
}

#=======================================================
# KARSILAMA EKRANLARI
#=======================================================

function Show-Welcome {
    Clear-Host
    Write-Host ""
    Write-Host "==================================================" -ForegroundColor Cyan
    Write-Host "   P Y T H O N   O C A G I" -ForegroundColor White
    Write-Host "       Yazarak Ogrenme Platformu" -ForegroundColor DarkGray
    Write-Host "       Veri Analizi Okulu - VAO" -ForegroundColor Magenta
    Write-Host "==================================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Hos geldin! Python Ocagi, terminal tabanli"
    Write-Host "interaktif bir Python ogrenme platformudur."
    Write-Host ""
    Write-Host "  96 interaktif ders (16 bolum)" -ForegroundColor Cyan
    Write-Host "  Kodun guvenli sandbox ortaminda calisir" -ForegroundColor Green
    Write-Host "  Gercek zamanli syntax highlighting" -ForegroundColor Yellow
    Write-Host "  Ilerleme otomatik kaydedilir" -ForegroundColor Magenta
    Write-Host ""
    Write-Host "  Ilerleme verilerin bilgisayarinda guvenle saklanir." -ForegroundColor DarkGray
    Write-Host "  Silmedigin veya uygulama icinden sifirlamedigin" -ForegroundColor DarkGray
    Write-Host "  surece kaldigin yerden devam edersin." -ForegroundColor DarkGray
    Write-Host ""
    Write-Host "--------------------------------------------------" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "  [Enter]  Hemen Basla" -ForegroundColor Green
    Write-Host "  [K]      Bilgisayarima Kur" -ForegroundColor Yellow
    Write-Host "  [Q]      Cikis" -ForegroundColor Red
    Write-Host ""
    Write-Host -NoNewline "Seciminiz: " -ForegroundColor Cyan
}

function Show-InstalledMenu {
    Clear-Host
    Write-Host ""
    Write-Host "==================================================" -ForegroundColor Cyan
    Write-Host "   P Y T H O N   O C A G I" -ForegroundColor White
    Write-Host "==================================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "  Python Ocagi zaten bilgisayariniza kurulu." -ForegroundColor Green
    Write-Host "  Masaustunuzdeki kisayol ile de acabilirsiniz." -ForegroundColor DarkGray
    Write-Host ""
    Write-Host "--------------------------------------------------" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "  [Enter]  Guncelle ve Basla" -ForegroundColor Green
    Write-Host "  [K]      Uygulamayi Kaldir" -ForegroundColor Red
    Write-Host "  [Q]      Cikis" -ForegroundColor Red
    Write-Host ""
    Write-Host -NoNewline "Seciminiz: " -ForegroundColor Cyan
}

#=======================================================
# ANA FONKSIYONLAR
#=======================================================

function Invoke-DirectRun {
    Download-AppTo -TargetDir $HiddenAppDir

    Write-Host ""
    Write-Host "Baslatiliyor..." -ForegroundColor Green
    Start-Sleep -Seconds 1
    Clear-Host

    Set-Location $HiddenAppDir

    if ($script:PythonCmd -eq "py") {
        & py -3.13 main.py
        if ($LASTEXITCODE -ne 0) {
            Write-Host "py -3.13 calismadi, python ile deneniyor..." -ForegroundColor Yellow
            & python main.py
        }
    } else {
        & python main.py
    }
}

function Invoke-Install {
    Write-Host ""
    Write-Host "=========================================" -ForegroundColor Cyan
    Write-Host "Kurulum basliyor..." -ForegroundColor Cyan
    Write-Host "=========================================" -ForegroundColor Cyan
    Write-Host ""

    # 1. Klasoru Olustur
    if (-not (Test-Path -Path $AppFolder)) {
        New-Item -ItemType Directory -Force -Path $AppFolder | Out-Null
        Write-Host "Masaustunde 'Python Ocagi' klasoru olusturuldu." -ForegroundColor Green
    }

    # 2. Baslatma motorunu indir
    Write-Host "Baslatma motoru indiriliyor..." -ForegroundColor Cyan
    $BaslatUrl = "https://raw.githubusercontent.com/$REPO_OWNER/$REPO_NAME/$BRANCH/baslat.ps1"
    $BaslatPath = Join-Path $AppFolder "baslat.ps1"
    $ProgressPreference = 'SilentlyContinue'
    Invoke-WebRequest -Uri $BaslatUrl -OutFile $BaslatPath -UseBasicParsing

    # 3. Kisa Yol Olustur (Masaustu .lnk)
    Write-Host "Masaustu kisayolu ayarlaniyor..." -ForegroundColor Cyan
    $WScriptShell = New-Object -ComObject WScript.Shell
    $Shortcut = $WScriptShell.CreateShortcut($ShortcutPath)
    $Shortcut.TargetPath = "powershell.exe"
    $Shortcut.Arguments = "-NoProfile -ExecutionPolicy Bypass -File `"$AppFolder\baslat.ps1`""
    $Shortcut.WorkingDirectory = $AppFolder
    $Shortcut.Description = "Python Ocagi - Yazarak Ogrenme"
    $Shortcut.Save()

    # 4. Kaldirma Dosyasi Olustur
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
    # BOM'suz yaz (kritik! BOM .bat dosyalarini bozar)
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

    # Kurulum penceresini temiz kapat
    exit 0
}

function Invoke-Uninstall {
    Write-Host ""
    Write-Host "=========================================" -ForegroundColor Red
    Write-Host "DIKKAT: Python Ocagi tamamen kaldirilacak!" -ForegroundColor Red
    Write-Host "Ilerlemeniz ve tum dosyalar silinecek." -ForegroundColor Red
    Write-Host "=========================================" -ForegroundColor Red
    Write-Host ""
    Write-Host "Iptal etmek icin bu pencereyi kapatin." -ForegroundColor White
    Write-Host -NoNewline "Devam etmek icin ENTER'a basin... " -ForegroundColor White
    Read-Host

    # Her seyi sil
    Remove-Item -Path $AppFolder -Recurse -Force -ErrorAction SilentlyContinue
    Remove-Item -Path $ShortcutPath -Force -ErrorAction SilentlyContinue
    Remove-Item -Path (Join-Path $env:APPDATA "python_ocagi") -Recurse -Force -ErrorAction SilentlyContinue
    Remove-Item -Path (Join-Path $HOME ".python_ocagi") -Recurse -Force -ErrorAction SilentlyContinue

    Write-Host ""
    Write-Host "Uygulama basariyla kaldirildi. Tum izler silindi." -ForegroundColor Green
    Write-Host ""
    pause
}

function Invoke-UpdateAndLaunch {
    Download-AppTo -TargetDir $AppFolder

    Write-Host ""
    Write-Host "Baslatiliyor..." -ForegroundColor Green
    Start-Sleep -Seconds 1
    Clear-Host

    Set-Location $AppFolder

    if ($script:PythonCmd -eq "py") {
        & py -3.13 main.py
        if ($LASTEXITCODE -ne 0) {
            Write-Host "py -3.13 calismadi, python ile deneniyor..." -ForegroundColor Yellow
            & python main.py
        }
    } else {
        & python main.py
    }
}

#=======================================================
# ANA PROGRAM
#=======================================================

# 1. Python kontrolu
if (-not (Test-PythonAvailable)) {
    Install-PythonWithPermission
}

# 2. Kurulum tespit
if (Test-Path $ShortcutPath) {
    # Daha once kurulmus — "Zaten Kurulu" menusu
    Show-InstalledMenu
    $key = Read-SingleKey
    Write-Host ""

    if ($key.Character -match '[kK]') {
        Invoke-Uninstall
    }
    elseif ($key.Character -match '[qQ]') {
        Write-Host ""
        Write-Host "Cikis yapildi." -ForegroundColor DarkGray
        exit 0
    }
    else {
        # Enter veya baska tus → Guncelle ve Baslat
        Invoke-UpdateAndLaunch
    }
}
else {
    # Ilk kullanim veya kurulum yapilmamis — Karsilama menusu
    Show-Welcome
    $key = Read-SingleKey
    Write-Host ""

    if ($key.Character -match '[kK]') {
        Invoke-Install
    }
    elseif ($key.Character -match '[qQ]') {
        Write-Host ""
        Write-Host "Cikis yapildi. Tekrar bekleriz!" -ForegroundColor DarkGray
        exit 0
    }
    else {
        # Enter veya baska tus → Direkt Kullan
        Invoke-DirectRun
    }
}
