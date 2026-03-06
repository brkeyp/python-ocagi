#=======================================================
# Python Ocağı - Windows Kurulum ve Başlatma Betiği
# İnteraktif menü ile kurulum, direkt kullanım ve kaldırma
#=======================================================

# TLS 1.2 Zorunlulugu (Geriye Donuk Uyumluluk)
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

# GitHub Repo Bilgileri
$REPO_OWNER = "brkeyp"
$REPO_NAME = "python-ocagi"
$BRANCH = "main"

# URL ve Dizin Tanimlari
$ZIP_URL = "https://github.com/$REPO_OWNER/$REPO_NAME/archive/refs/heads/$BRANCH.zip"
$DesktopPath = [Environment]::GetFolderPath("Desktop")
$AppFolder = Join-Path $DesktopPath "Python Ocagi"
$ShortcutPath = Join-Path $DesktopPath "PYTHON OCAGINA GIR.lnk"
$UninstallPath = Join-Path $AppFolder "Uygulamayi Kaldir.bat"
$TempAppDir = Join-Path $env:TEMP "python_ocagi_hemenbasla"

# Gecici dosya yollari
$TempZip = Join-Path $env:TEMP "python_ocagi_update.zip"
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

function Refresh-SessionPath {
    <# Registry'den guncel PATH degerlerini okuyup mevcut oturuma uygular.
       Python kurulumu sonrasi py/python komutlarinin bulunabilmesi icin gereklidir. #>
    try {
        $machinePath = [Environment]::GetEnvironmentVariable("Path", "Machine")
        $userPath = [Environment]::GetEnvironmentVariable("Path", "User")
        $env:Path = "$machinePath;$userPath"
    }
    catch {}
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
            }
            else {
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

            # PATH'i yenile (yeni kurulan Python'u bulsun)
            Refresh-SessionPath

            # Dogrulama — gercek calisip calismadigini kontrol et
            $PyCheck = Get-Command "py" -ErrorAction SilentlyContinue
            if ($PyCheck) {
                try {
                    $ver = & py --version 2>&1
                    if ($ver -match "Python 3\.") {
                        $script:PythonCmd = "py"
                        Write-Host ""
                        Write-Host "Python basariyla yuklendi!" -ForegroundColor Green
                        return $true
                    }
                }
                catch {}
            }

            $PyCheck = Get-Command "python" -ErrorAction SilentlyContinue
            if ($PyCheck) {
                try {
                    $ver = & python --version 2>&1
                    if ($ver -match "Python 3\.") {
                        $script:PythonCmd = "python"
                        Write-Host ""
                        Write-Host "Python basariyla yuklendi!" -ForegroundColor Green
                        return $true
                    }
                }
                catch {}
            }

            # Son care: varsayilan kurulum konumunu kontrol et
            $defaultPyLauncher = Join-Path $env:LOCALAPPDATA "Programs\Python\Launcher\py.exe"
            if (Test-Path $defaultPyLauncher) {
                $script:PythonCmd = $defaultPyLauncher
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
    <# Python'un gercekten yuklu ve calisir durumda olduğunu dogrular.
       Windows 10/11'deki Microsoft Store 'python.exe' alias'i
       Get-Command ile bulunur ama gercek Python degildir.
       Bu yuzden komut bulunduktan sonra --version ile dogrulama yapilir. #>

    # 1. py launcher ile dene (en guvenilir)
    $PyLauncher = Get-Command "py" -ErrorAction SilentlyContinue
    if ($PyLauncher) {
        try {
            $ver = & py --version 2>&1
            if ($ver -match "Python 3\.") {
                $script:PythonCmd = "py"
                return $true
            }
        }
        catch {}
    }

    # 2. python komutu ile dene (Store alias kontrollu)
    $PythonExe = Get-Command "python" -ErrorAction SilentlyContinue
    if ($PythonExe) {
        try {
            $ver = & python --version 2>&1
            if ($ver -match "Python 3\.") {
                $script:PythonCmd = "python"
                return $true
            }
        }
        catch {}
    }

    # 3. Son care: varsayilan kurulum konumunu kontrol et
    $defaultPyLauncher = Join-Path $env:LOCALAPPDATA "Programs\Python\Launcher\py.exe"
    if (Test-Path $defaultPyLauncher) {
        try {
            $ver = & $defaultPyLauncher --version 2>&1
            if ($ver -match "Python 3\.") {
                $script:PythonCmd = $defaultPyLauncher
                return $true
            }
        }
        catch {}
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
    Download-AppTo -TargetDir $TempAppDir

    Write-Host ""
    Write-Host "Baslatiliyor..." -ForegroundColor Green
    Start-Sleep -Seconds 1
    Clear-Host

    Set-Location $TempAppDir

    $launched = $false
    try {
        if ($script:PythonCmd -eq "py" -or $script:PythonCmd -like "*py.exe") {
            & $script:PythonCmd -3.13 main.py
            if ($LASTEXITCODE -eq 0) { $launched = $true }
            if (-not $launched) {
                Write-Host "py -3.13 calismadi, python ile deneniyor..." -ForegroundColor Yellow
                & $script:PythonCmd main.py
                if ($LASTEXITCODE -eq 0) { $launched = $true }
            }
        }
        else {
            & $script:PythonCmd main.py
            if ($LASTEXITCODE -eq 0) { $launched = $true }
        }
    }
    catch {
        Write-Host "Hata: $_" -ForegroundColor Red
    }

    if (-not $launched) {
        Write-Host "" 
        Write-Host "=========================================" -ForegroundColor Red
        Write-Host "Uygulama baslatilirken bir sorun olustu." -ForegroundColor Red
        Write-Host "=========================================" -ForegroundColor Red
        Write-Host ""
        Write-Host "Python 3.13 yuklu ve calisir durumda oldugundan" -ForegroundColor Yellow
        Write-Host "emin olun. python.org/downloads adresinden" -ForegroundColor Yellow
        Write-Host "Python 3.13 indirip kurabilirsiniz." -ForegroundColor Yellow
        Write-Host ""
        pause
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
echo DIKKAT: Python Ocagi sisteminizden kaldirilacaktir.
echo.
set /p DEL_PROG="Ilerlemenizi (cozdugunuz sorular ve puanlar) silmek istiyor musunuz? (E/H): "
echo =======================================================
echo Kaldirma islemi baslatildi...

:: Klasor kilidini kirmak icin dizini ev dizinine (USERPROFILE) degistir
cd /d "%USERPROFILE%"

start "" powershell -NoProfile -ExecutionPolicy Bypass -Command "`$del_prog='%DEL_PROG%'; Start-Sleep -Seconds 2; Write-Host 'Uygulama dosyalari siliniyor...' -ForegroundColor Red; Remove-Item -Path (Join-Path ([Environment]::GetFolderPath('Desktop')) 'Python Ocagi') -Recurse -Force -ErrorAction SilentlyContinue; Remove-Item -Path (Join-Path ([Environment]::GetFolderPath('Desktop')) '$LnkName') -Force -ErrorAction SilentlyContinue; if (`$del_prog -match '^[EeYy]') { Write-Host 'Ilerleme verileri siliniyor...' -ForegroundColor Red; Remove-Item -Path (Join-Path `$env:APPDATA 'python_ocagi') -Recurse -Force -ErrorAction SilentlyContinue; Remove-Item -Path (Join-Path `$HOME '.python_ocagi') -Recurse -Force -ErrorAction SilentlyContinue; Write-Host 'Her sey silindi.' -ForegroundColor DarkGray } else { Write-Host 'Ilerleme verileri SAKLANDI.' -ForegroundColor Green }; Write-Host ''; Write-Host 'Kaldirma tamamlandi! Bu pencere kapanacak.' -ForegroundColor Green; Start-Sleep -Seconds 3"
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
    Write-Host "DIKKAT: Python Ocagi kaldirilacak!" -ForegroundColor Red
    Write-Host "Uygulama dosyalari silinecek." -ForegroundColor Red
    Write-Host "=========================================" -ForegroundColor Red
    Write-Host ""
    Write-Host "Iptal etmek icin bu pencereyi kapatin." -ForegroundColor White
    Write-Host -NoNewline "Devam etmek icin ENTER'a basin... " -ForegroundColor White
    Read-Host

    Write-Host ""
    Write-Host "Ilerlemeniz (cozdugunuz sorular ve puanlar) silinsin mi?" -ForegroundColor Yellow
    Write-Host "  [E] Evet, her seyi sil" -ForegroundColor Red
    Write-Host "  [H] Hayir, ilerlememi sakla (Hemen Basla ile devam edilebilir)" -ForegroundColor Green
    Write-Host ""
    Write-Host -NoNewline "Seciminiz: " -ForegroundColor Cyan
    $key = Read-SingleKey
    Write-Host ""

    # Klasor kilidini kirmak icin dizini ev dizinine degistir
    Set-Location -Path $env:USERPROFILE

    # Her seyi sil
    Remove-Item -Path $AppFolder -Recurse -Force -ErrorAction SilentlyContinue
    Remove-Item -Path $ShortcutPath -Force -ErrorAction SilentlyContinue
    
    if ($key.Character -match '[EeYy]') {
        Remove-Item -Path (Join-Path $env:APPDATA "python_ocagi") -Recurse -Force -ErrorAction SilentlyContinue
        Remove-Item -Path (Join-Path $HOME ".python_ocagi") -Recurse -Force -ErrorAction SilentlyContinue
        Write-Host ""
        Write-Host "Uygulama ve ilerleme verileriniz tamamen silindi." -ForegroundColor Green
    } else {
        Write-Host ""
        Write-Host "Uygulama verileri silindi. Ilerleme verileriniz SAKLANDI." -ForegroundColor Green
    }
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

    $launched = $false
    try {
        if ($script:PythonCmd -eq "py" -or $script:PythonCmd -like "*py.exe") {
            & $script:PythonCmd -3.13 main.py
            if ($LASTEXITCODE -eq 0) { $launched = $true }
            if (-not $launched) {
                Write-Host "py -3.13 calismadi, python ile deneniyor..." -ForegroundColor Yellow
                & $script:PythonCmd main.py
                if ($LASTEXITCODE -eq 0) { $launched = $true }
            }
        }
        else {
            & $script:PythonCmd main.py
            if ($LASTEXITCODE -eq 0) { $launched = $true }
        }
    }
    catch {
        Write-Host "Hata: $_" -ForegroundColor Red
    }

    if (-not $launched) {
        Write-Host "" 
        Write-Host "=========================================" -ForegroundColor Red
        Write-Host "Uygulama baslatilirken bir sorun olustu." -ForegroundColor Red
        Write-Host "=========================================" -ForegroundColor Red
        Write-Host ""
        Write-Host "Python 3.13 yuklu ve calisir durumda oldugundan" -ForegroundColor Yellow
        Write-Host "emin olun. python.org/downloads adresinden" -ForegroundColor Yellow
        Write-Host "Python 3.13 indirip kurabilirsiniz." -ForegroundColor Yellow
        Write-Host ""
        pause
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
