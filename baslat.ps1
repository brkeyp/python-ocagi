#=======================================================
# Python Ocağı - Windows Başlatma ve Güncelleme Betiği
# Her çift tıklamada çalışır: günceller + uygulamayı başlatır
#
# Bu betik tam bağımsızdır (Self-Sufficient Launcher):
# - Uygulama dosyalarını günceller
# - Python yoksa tespit edip yükleme teklif eder
# - Offline durumda mevcut sürümle devam eder
# - Hata durumunda terminali açık tutar
#=======================================================

# TLS 1.2 Zorunlulugu (Geriye Donuk Uyumluluk)
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

# Pencere başlığı
$Host.UI.RawUI.WindowTitle = "PYTHON OCAGI - YAZARAK OGRENME"

# Repo bilgileri
$REPO_OWNER = "brkeyp"
$REPO_NAME = "python-ocagi"
$BRANCH = "main"

$ZIP_URL = "https://github.com/$REPO_OWNER/$REPO_NAME/archive/refs/heads/$BRANCH.zip"
$AppFolder = Join-Path ([Environment]::GetFolderPath("Desktop")) "Python Ocagi"
$TempZip = Join-Path $env:TEMP "app_update.zip"
$TempExtract = Join-Path $env:TEMP "app_extracted"

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

function Show-ManualPythonInstructions {
    Write-Host ""
    Write-Host "Python'u manuel olarak yuklemek icin:" -ForegroundColor Yellow
    Write-Host "  python.org/downloads adresinden Python 3.13 indirin." -ForegroundColor White
    Write-Host "  Kurulum sirasinda 'Add to PATH' secenegini isaretleyin." -ForegroundColor White
    Write-Host ""
    Write-Host "Yukledikten sonra bu kisayolu tekrar acin." -ForegroundColor DarkGray
}

#=======================================================
# PYTHON KONTROL VE KURULUM
#=======================================================

function Test-PythonAvailable {
    <# Python'un gercekten yuklu ve calisir durumda oldugunu dogrular.
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

            # Hicbiri bulunamadi — oturum yenilemesi gerekebilir
            Write-Host ""
            Write-Host "Python kurulumu tamamlandi ancak bu oturumda aktif edilemedi." -ForegroundColor Yellow
            Write-Host "Lutfen bu pencereyi kapatip kisayolu tekrar acin." -ForegroundColor Yellow
            pause
            exit 0
        }
        catch {
            Write-Host ""
            Write-Host "Python indirme/kurulum hatasi: $_" -ForegroundColor Red
            Write-Host ""
            Write-Host "Olasi nedenler:" -ForegroundColor Yellow
            Write-Host "  - Internet baglantisi sorunu" -ForegroundColor White
            Write-Host "  - Kurumsal bilgisayar kisitlamasi" -ForegroundColor White
            Write-Host "  - Antiviruks yazilimi engeli" -ForegroundColor White
            Write-Host ""
            Write-Host "Cozum:" -ForegroundColor Yellow
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

#=======================================================
# GUNCELLEME
#=======================================================

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Python Ocagi Guncelleniyor..."            -ForegroundColor Cyan
Write-Host "Lutfen bekleyin... (Internet baglantisina gore degisir)" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan

$TempKur = Join-Path $env:TEMP "kur_windows_update.ps1"
$KurUrl = "https://raw.githubusercontent.com/$REPO_OWNER/$REPO_NAME/$BRANCH/kur_windows.ps1"

try {
    $ProgressPreference = 'SilentlyContinue'
    Invoke-WebRequest -Uri $KurUrl -OutFile $TempKur -UseBasicParsing
    
    # Eger basariliysa, auto-update modunda scripti asenkron baslat ve KENDINI KAPAT
    Start-Process powershell.exe -ArgumentList "-NoProfile -ExecutionPolicy Bypass -File `"$TempKur`" -AutoUpdate"
    exit 0
}
catch {
    Write-Host ""
    Write-Host "==========================================" -ForegroundColor Yellow
    Write-Host "Internet baglantisi kurulamadi."            -ForegroundColor Yellow
    Write-Host "Guncellemeler alinamadi ama sorun degil!"   -ForegroundColor White
    Write-Host ""                                           
    Write-Host "Ilerlemeniz kaybolmadi, kurulu olan en son" -ForegroundColor White
    Write-Host "surumle kaldiginiz yerden devam edebilirsiniz." -ForegroundColor White
    Write-Host "==========================================" -ForegroundColor Yellow
    Write-Host ""
    Write-Host -NoNewline "Devam etmek icin ENTER'a basin... " -ForegroundColor Cyan
    Read-Host
}

#=======================================================
# PYTHON KONTROL
#=======================================================

if (-not (Test-PythonAvailable)) {
    # Internet yoksa ve Python da yoksa: cikis mesaji goster
    Write-Host ""
    Write-Host "=========================================" -ForegroundColor Red
    Write-Host "Python bulunamadi ve internet baglantisi yok." -ForegroundColor Red
    Write-Host "=========================================" -ForegroundColor Red
    Write-Host ""
    Write-Host "Uygulama baslatilabilmesi icin Python 3.13 gereklidir." -ForegroundColor White
    Write-Host "Internet baglantinizi saglayip tekrar deneyin veya" -ForegroundColor White
    Write-Host "python.org/downloads adresinden Python 3.13 indirin." -ForegroundColor White
    Write-Host ""
    pause
    exit 1

    # Normalde internet var ama Python yoksa: kurulum teklif etmesi baslat.ps1 de gerekli degil
    # cunku o isleri de kur_windows.ps1 yapecek. Sadece cevrimdisi kaldiysa baslatmaya calismali.
}

#=======================================================
# UYGULAMA BASLAT (CEVRIMDISI MOD)
#=======================================================

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
