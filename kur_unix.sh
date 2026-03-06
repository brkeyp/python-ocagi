#!/bin/bash
#=======================================================
# Python Ocağı - Mac/Linux Kurulum ve Başlatma Betiği
# İnteraktif menü ile kurulum, direkt kullanım ve kaldırma
#=======================================================

# GitHub Repo Bilgileri
REPO_OWNER="brkeyp"
REPO_NAME="python-ocagi"
BRANCH="main"

ZIP_URL="https://github.com/$REPO_OWNER/$REPO_NAME/archive/refs/heads/$BRANCH.zip"

#=======================================================
# PIPE UYUMLULUK — curl | bash desteği
#=======================================================
# curl | bash ile çalıştırıldığında stdin pipe olur (terminal değil).
# Bu durumda script kendini temp dosyaya kaydedip terminal stdin ile
# yeniden çalıştırır. Homebrew ve rustup aynı kalıbı kullanır.

SCRIPT_URL="https://raw.githubusercontent.com/$REPO_OWNER/$REPO_NAME/$BRANCH/kur_unix.sh"

if [ ! -t 0 ]; then
    _KUR_TMP=$(mktemp /tmp/python_ocagi_kur_XXXXXX)
    curl -sL "$SCRIPT_URL" -o "$_KUR_TMP"
    export _KUR_CLEANUP="$_KUR_TMP"
    exec bash "$_KUR_TMP" < /dev/tty
fi

# Pipe'dan yeniden çalıştırıldıysa, çıkışta temp dosyayı temizle
if [ -n "$_KUR_CLEANUP" ]; then
    trap 'rm -f "$_KUR_CLEANUP" 2>/dev/null' EXIT
    unset _KUR_CLEANUP
fi

# Dizin Tanımları
DESKTOP_DIR="$HOME/Desktop"

# MacOS Arkaplan Temizlik Botu (Daemon)
cleanup_mac_daemon() {
    if [[ "$OSTYPE" == "darwin"* ]]; then
        local target_pid=$$
        local win_id=$(osascript -e 'tell application "Terminal" to id of front window' 2>/dev/null)
        
        nohup bash -c "
            while kill -0 $target_pid 2>/dev/null; do
                sleep 0.5
            done
            osascript -e '
                tell application \"Terminal\"
                    try
                        if \"$win_id\" is not \"\" then
                            close (every window whose id is $win_id)
                        end if
                    end try
                    repeat with w in windows
                        try
                            set t to selected tab of w
                            if not busy of t then
                                if (count of paragraphs of (history of t as string)) ≤ 5 then close w
                            end if
                        end try
                    end repeat
                    if (count of windows) is 0 then quit
                end tell
            ' >/dev/null 2>&1
        " >/dev/null 2>&1 &
        disown
    fi
}
# Ana script kapandığında Terminal temizliği yapmak için daimonu başlat
cleanup_mac_daemon
APP_DIR="$DESKTOP_DIR/Python Ocağı"
SHORTCUT_FILE="$DESKTOP_DIR/PYTHON OCAĞINA GİR.command"
UNINSTALL_FILE="$APP_DIR/Uygulamayı Kaldır.command"
HIDDEN_APP_DIR="$HOME/.python_ocagi/app"
PYTHON_CMD=""

# Renk Tanımları
C_RESET="\033[0m"
C_RED="\033[0;31m"
C_GREEN="\033[0;32m"
C_YELLOW="\033[0;33m"
C_CYAN="\033[0;36m"
C_WHITE="\033[1;37m"
C_DIM="\033[0;90m"
C_MAGENTA="\033[0;35m"

#=======================================================
# PYTHON KONTROL VE KURULUM
#=======================================================

show_manual_python_instructions() {
    echo ""
    echo -e "${C_YELLOW}Python'u manuel olarak yüklemek için:${C_RESET}"
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo -e "  • ${C_WHITE}brew install python${C_RESET}"
        echo -e "  • veya ${C_WHITE}python.org/downloads${C_RESET} adresinden indirin"
    else
        echo -e "  • ${C_WHITE}sudo apt install python3${C_RESET}   (Debian/Ubuntu)"
        echo -e "  • ${C_WHITE}sudo dnf install python3${C_RESET}   (Fedora)"
        echo -e "  • ${C_WHITE}sudo pacman -S python${C_RESET}      (Arch)"
    fi
    echo ""
    echo -e "${C_DIM}Yükledikten sonra bu komutu tekrar çalıştırın.${C_RESET}"
}

install_python_macos() {
    # Önce Homebrew dene (sudo gerektirmez)
    if command -v brew &>/dev/null; then
        echo -e "${C_CYAN}🍺 Homebrew ile Python yükleniyor...${C_RESET}"
        brew install python3
        if command -v python3 &>/dev/null; then
            PYTHON_CMD="python3"
            echo -e "${C_GREEN}✅ Python başarıyla yüklendi!${C_RESET}"
            return 0
        fi
    fi

    # Homebrew yoksa → Xcode Command Line Tools
    echo -e "${C_CYAN}📦 Xcode Command Line Tools yükleniyor...${C_RESET}"
    echo -e "${C_DIM}   (Apple'ın kurulum penceresi açılacak)${C_RESET}"
    echo ""
    xcode-select --install 2>/dev/null
    echo ""
    echo -e "${C_YELLOW}⏳ Apple kurulum penceresi açıldı.${C_RESET}"
    echo -e "${C_YELLOW}   Kurulum tamamlandıktan sonra bu komutu tekrar çalıştırın.${C_RESET}"
    echo ""
    read -n 1 -s -r -p "Çıkmak için herhangi bir tuşa basın..." < /dev/tty
    echo ""
    exit 0
}

install_python_linux() {
    if command -v apt &>/dev/null; then
        echo -e "${C_CYAN}📦 APT ile Python yükleniyor...${C_RESET}"
        sudo apt update && sudo apt install -y python3
    elif command -v dnf &>/dev/null; then
        echo -e "${C_CYAN}📦 DNF ile Python yükleniyor...${C_RESET}"
        sudo dnf install -y python3
    elif command -v pacman &>/dev/null; then
        echo -e "${C_CYAN}📦 Pacman ile Python yükleniyor...${C_RESET}"
        sudo pacman -S --noconfirm python
    elif command -v zypper &>/dev/null; then
        echo -e "${C_CYAN}📦 Zypper ile Python yükleniyor...${C_RESET}"
        sudo zypper install -y python3
    else
        echo -e "${C_RED}❌ Paket yöneticisi tespit edilemedi.${C_RESET}"
        show_manual_python_instructions
        exit 1
    fi

    # Doğrulama
    if command -v python3 &>/dev/null; then
        PYTHON_CMD="python3"
        echo -e "${C_GREEN}✅ Python başarıyla yüklendi!${C_RESET}"
    else
        echo -e "${C_RED}❌ Python kurulumu başarısız oldu.${C_RESET}"
        show_manual_python_instructions
        exit 1
    fi
}

check_python() {
    # python3 komutunu ara
    if command -v python3 &>/dev/null; then
        PYTHON_CMD="python3"
        return 0
    fi

    # python komutunu dene (Python 3 mü kontrol et)
    if command -v python &>/dev/null; then
        PY_VER=$(python --version 2>&1 | head -1)
        if echo "$PY_VER" | grep -q "Python 3"; then
            PYTHON_CMD="python"
            return 0
        fi
    fi

    # Python bulunamadı — izin iste
    echo ""
    echo -e "${C_RED}═══════════════════════════════════════════${C_RESET}"
    echo -e "${C_YELLOW}⚠️  Python bulunamadı!${C_RESET}"
    echo -e "${C_RED}═══════════════════════════════════════════${C_RESET}"
    echo ""
    echo -e "Bu uygulama çalışmak için ${C_WHITE}Python 3${C_RESET} gerektirir."
    echo ""

    if [[ "$OSTYPE" == "darwin"* ]]; then
        if command -v brew &>/dev/null; then
            echo -e "Homebrew ile otomatik olarak yüklenebilir."
        else
            echo -e "Xcode Command Line Tools ile yüklenebilir."
        fi
    else
        echo -e "Paket yöneticiniz ile otomatik olarak yüklenebilir."
    fi

    echo ""
    echo -e "${C_WHITE}Otomatik olarak yüklemek ister misiniz?${C_RESET}"
    echo ""
    echo -e "  ${C_GREEN}[E]${C_RESET}  Evet, yükle"
    echo -e "  ${C_RED}[H]${C_RESET}  Hayır, kendim yükleyeceğim"
    echo ""
    echo -ne "${C_CYAN}Seçiminiz: ${C_RESET}"
    read -n 1 -r REPLY < /dev/tty
    echo ""

    if [[ "$REPLY" =~ ^[EeYy]$ ]] || [[ -z "$REPLY" ]]; then
        echo ""
        # Platform-spesifik kurulum
        if [[ "$OSTYPE" == "darwin"* ]]; then
            install_python_macos
        else
            install_python_linux
        fi
    else
        show_manual_python_instructions
        exit 0
    fi
}

#=======================================================
# KARŞILAMA EKRANLARI
#=======================================================

show_welcome() {
    clear
    echo ""
    echo -e "${C_CYAN}══════════════════════════════════════════════════${C_RESET}"
    echo -e "${C_WHITE}🐍  P Y T H O N   O C A Ğ I${C_RESET}"
    echo -e "${C_DIM}    Yazarak Öğrenme Platformu${C_RESET}"
    echo -e "${C_MAGENTA}    Veri Analizi Okulu - VAO 💜${C_RESET}"
    echo -e "${C_CYAN}══════════════════════════════════════════════════${C_RESET}"
    echo ""
    echo -e "Hoş geldin! Python Ocağı, terminal tabanlı"
    echo -e "interaktif bir Python öğrenme platformudur."
    echo ""
    echo -e "${C_CYAN}📚${C_RESET}  96 interaktif ders (16 bölüm)"
    echo -e "${C_GREEN}🔒${C_RESET}  Kodun güvenli sandbox ortamında çalışır"
    echo -e "${C_YELLOW}🎨${C_RESET}  Gerçek zamanlı syntax highlighting"
    echo -e "${C_MAGENTA}📊${C_RESET}  İlerleme otomatik kaydedilir"
    echo ""
    echo -e "${C_DIM}💾 İlerleme verilerin bilgisayarında güvenle saklanır.${C_RESET}"
    echo -e "${C_DIM}   Silmediğin veya uygulama içinden sıfırlamadığın${C_RESET}"
    echo -e "${C_DIM}   sürece kaldığın yerden devam edersin.${C_RESET}"
    echo ""
    echo -e "${C_CYAN}──────────────────────────────────────────────────${C_RESET}"
    echo ""
    echo -e "  ${C_GREEN}[Enter]${C_RESET}  🚀  Hemen Başla"
    echo -e "  ${C_YELLOW}[K]${C_RESET}      🔧  Bilgisayarıma Kur"
    echo -e "  ${C_RED}[Q]${C_RESET}      ❌  Çıkış"
    echo ""
    echo -ne "${C_CYAN}Seçiminiz: ${C_RESET}"
}

show_installed_menu() {
    clear
    echo ""
    echo -e "${C_CYAN}══════════════════════════════════════════════════${C_RESET}"
    echo -e "${C_WHITE}🐍  P Y T H O N   O C A Ğ I${C_RESET}"
    echo -e "${C_CYAN}══════════════════════════════════════════════════${C_RESET}"
    echo ""
    echo -e "${C_GREEN}✅ Python Ocağı zaten bilgisayarınıza kurulu.${C_RESET}"
    echo -e "${C_DIM}   Masaüstünüzdeki kısayol ile de açabilirsiniz.${C_RESET}"
    echo ""
    echo -e "${C_CYAN}──────────────────────────────────────────────────${C_RESET}"
    echo ""
    echo -e "  ${C_GREEN}[Enter]${C_RESET}  🔄  Güncelle ve Başla"
    echo -e "  ${C_RED}[K]${C_RESET}      🗑️   Uygulamayı Kaldır"
    echo -e "  ${C_RED}[Q]${C_RESET}      ❌  Çıkış"
    echo ""
    echo -ne "${C_CYAN}Seçiminiz: ${C_RESET}"
}

#=======================================================
# ANA FONKSİYONLAR
#=======================================================

download_app() {
    # Ortak indirme fonksiyonu — hedef dizini parametre olarak alır
    local TARGET_DIR="$1"
    mkdir -p "$TARGET_DIR"

    echo -e "${C_CYAN}🔄 Uygulama indiriliyor...${C_RESET}"
    echo -e "${C_DIM}   (İnternet hızınıza göre değişir)${C_RESET}"

    curl -sL -o /tmp/python_ocagi_update.zip "$ZIP_URL"
    rm -rf /tmp/python_ocagi_extracted
    unzip -qo /tmp/python_ocagi_update.zip -d /tmp/python_ocagi_extracted
    cp -R "/tmp/python_ocagi_extracted/$REPO_NAME-$BRANCH/"* "$TARGET_DIR/"
    rm -rf /tmp/python_ocagi_update.zip /tmp/python_ocagi_extracted

    echo -e "${C_GREEN}✅ İndirme tamamlandı.${C_RESET}"
}

direkt_kullan() {
    echo ""
    download_app "$HIDDEN_APP_DIR"

    echo -e "${C_GREEN}Başlatılıyor...${C_RESET}"
    sleep 1
    clear
    cd "$HIDDEN_APP_DIR"

    # Bash'in cooperative SIGINT mekanizması iptal edilmiyor, hata düzeltildi
    $PYTHON_CMD main.py < /dev/tty
}

kur() {
    echo ""
    echo -e "${C_CYAN}═══════════════════════════════════════════${C_RESET}"
    echo -e "${C_CYAN}Kurulum başlıyor...${C_RESET}"
    echo -e "${C_CYAN}═══════════════════════════════════════════${C_RESET}"
    echo ""

    # 1. Klasörü Oluştur
    mkdir -p "$APP_DIR"

    # 2. Kısa Yol Oluştur (.command)
    cat << 'EOF' > "$SHORTCUT_FILE"
#!/bin/bash

# MacOS Arkaplan Temizlik Botu (Daemon)
cleanup_mac_daemon() {
    if [[ "$OSTYPE" == "darwin"* ]]; then
        local target_pid=$$
        local win_id=$(osascript -e 'tell application "Terminal" to id of front window' 2>/dev/null)
        
        nohup bash -c "
            while kill -0 $target_pid 2>/dev/null; do
                sleep 0.5
            done
            osascript -e '
                tell application \"Terminal\"
                    try
                        if \"$win_id\" is not \"\" then
                            close (every window whose id is $win_id)
                        end if
                    end try
                    repeat with w in windows
                        try
                            set t to selected tab of w
                            if not busy of t then
                                if (count of paragraphs of (history of t as string)) ≤ 5 then close w
                            end if
                        end try
                    end repeat
                    if (count of windows) is 0 then quit
                end tell
            ' >/dev/null 2>&1
        " >/dev/null 2>&1 &
        disown
    fi
}
cleanup_mac_daemon
echo -e "\033[0;36m=========================================\033[0m"
echo -e "\033[0;36mPython Ocağı Güncelleniyor...\033[0m"
echo -e "\033[0;36mLütfen bekleyin (İnternet hızınıza göre değişir)\033[0m"
echo -e "\033[0;36m=========================================\033[0m"

ZIP_URL="PLACEHOLDER_ZIP"
REPO_DIR="PLACEHOLDER_DIR"

curl -sL -o /tmp/app_update.zip "$ZIP_URL"
rm -rf /tmp/app_extracted
unzip -qo /tmp/app_update.zip -d /tmp/app_extracted
cp -R "/tmp/app_extracted/$REPO_DIR/"* "$HOME/Desktop/Python Ocağı/"

echo -e "\033[0;32mGüncelleme tamamlandı. Başlatılıyor...\033[0m"
sleep 1
clear
cd "$HOME/Desktop/Python Ocağı"
python3 main.py || python main.py

exit 0
EOF

    # Placeholder'ları değiştir
    sed -i.bak "s|PLACEHOLDER_ZIP|$ZIP_URL|g" "$SHORTCUT_FILE"
    rm -f "$SHORTCUT_FILE.bak"
    sed -i.bak "s|PLACEHOLDER_DIR|$REPO_NAME-$BRANCH|g" "$SHORTCUT_FILE"
    rm -f "$SHORTCUT_FILE.bak"

    chmod +x "$SHORTCUT_FILE"

    # 3. Kaldırma Dosyası Oluştur
    cat << 'EOF' > "$UNINSTALL_FILE"
#!/bin/bash

# MacOS Arkaplan Temizlik Botu (Daemon)
cleanup_mac_daemon() {
    if [[ "$OSTYPE" == "darwin"* ]]; then
        local target_pid=$$
        local win_id=$(osascript -e 'tell application "Terminal" to id of front window' 2>/dev/null)
        
        nohup bash -c "
            while kill -0 $target_pid 2>/dev/null; do
                sleep 0.5
            done
            osascript -e '
                tell application \"Terminal\"
                    try
                        if \"$win_id\" is not \"\" then
                            close (every window whose id is $win_id)
                        end if
                    end try
                    repeat with w in windows
                        try
                            set t to selected tab of w
                            if not busy of t then
                                if (count of paragraphs of (history of t as string)) ≤ 5 then close w
                            end if
                        end try
                    end repeat
                    if (count of windows) is 0 then quit
                end tell
            ' >/dev/null 2>&1
        " >/dev/null 2>&1 &
        disown
    fi
}
cleanup_mac_daemon

echo -e "\033[0;31m=======================================================\033[0m"
echo -e "\033[0;31mDİKKAT: Python Ocağı sisteminizden kaldırılacaktır.\033[0m"
echo -e ""
read -p "İlerlemeyi (çözdüğünüz sorular ve puanlar) silmek istiyor musunuz? (E/H): " DEL_PROG
echo -e "\033[0;31m=======================================================\033[0m"

echo -e "\033[0;31mUygulama dosyaları siliniyor...\033[0m"
rm -rf "$HOME/Desktop/Python Ocağı"
rm -f "$HOME/Desktop/PYTHON OCAĞINA GİR.command"

if [[ "$DEL_PROG" =~ ^[EeYy] ]]; then
    echo -e "\033[0;31mİlerleme verileri siliniyor...\033[0m"
    rm -rf "$HOME/.python_ocagi"
    echo -e ""
    echo -e "\033[0;32mUygulama ve ilerleme verileriniz tamamen silindi.\033[0m"
else
    echo -e ""
    echo -e "\033[0;32mUygulama dosyaları silindi. İlerleme verileriniz SAKLANDI.\033[0m"
fi

echo -e ""
read -n 1 -s -r -p "Bu ekranı kapatmak için herhangi bir tuşa basın..."
echo -e ""

exit 0
EOF
    chmod +x "$UNINSTALL_FILE"

    echo ""
    echo -e "${C_GREEN}═══════════════════════════════════════════${C_RESET}"
    echo -e "${C_GREEN}KURULUM TAMAMLANDI!${C_RESET}"
    echo -e "${C_GREEN}═══════════════════════════════════════════${C_RESET}"
    echo -e "${C_CYAN}Uygulamayı hemen başlatmak üzere masaüstünüzdeki kısayola ulaşılıyor...${C_RESET}"
    sleep 2

    # 4. İlk İndirme ve Başlatma
    # Çift terminal açılmasını önlemek için doğrudan mevcut terminalde çalıştırıyoruz.
    exec "$SHORTCUT_FILE"
}

kaldir() {
    echo ""
    echo -e "${C_RED}═══════════════════════════════════════════${C_RESET}"
    echo -e "${C_RED}⚠️  DİKKAT: Python Ocağı kaldırılacak!${C_RESET}"
    echo -e "${C_RED}   Uygulama dosyaları silinecek.${C_RESET}"
    echo -e "${C_RED}═══════════════════════════════════════════${C_RESET}"
    echo ""
    echo -e "İptal etmek için ${C_WHITE}Ctrl+C${C_RESET} yapın."
    echo ""
    echo -e "${C_YELLOW}İlerlemeniz (çözdüğünüz sorular ve puanlar) silinsin mi?${C_RESET}"
    echo -e "  ${C_RED}[E] Evet, her şeyi sil${C_RESET}"
    echo -e "  ${C_GREEN}[H] Hayır, ilerlememi sakla (Hemen Başla ile devam edilebilir)${C_RESET}"
    echo ""
    echo -ne "${C_CYAN}Seçiminiz: ${C_RESET}"
    read -n 1 -r DEL_PROG < /dev/tty
    echo ""

    rm -rf "$APP_DIR"
    rm -f "$SHORTCUT_FILE"
    
    if [[ "$DEL_PROG" =~ ^[EeYy] ]]; then
        rm -rf "$HOME/.python_ocagi"
        echo ""
        echo -e "${C_GREEN}✅ Uygulama ve ilerleme verileriniz tamamen silindi.${C_RESET}"
    else
        echo ""
        echo -e "${C_GREEN}✅ Uygulama silindi. İlerleme verileriniz SAKLANDI.${C_RESET}"
    fi
    echo ""
}

guncelle_ve_baslat() {
    echo ""
    download_app "$APP_DIR"

    echo -e "${C_GREEN}Başlatılıyor...${C_RESET}"
    sleep 1
    clear
    cd "$APP_DIR"

    # Ctrl+C Python'a ulaşıyor.
    $PYTHON_CMD main.py < /dev/tty
}

#=======================================================
# ANA PROGRAM
#=======================================================

# 1. Python kontrolü
check_python

# 2. Kurulum tespit
if [ -f "$SHORTCUT_FILE" ]; then
    # Daha önce kurulmuş — "Zaten Kurulu" menüsü
    show_installed_menu
    read -n 1 -s -r CHOICE < /dev/tty
    echo ""

    case "$CHOICE" in
        [kK])
            kaldir
            ;;
        [qQ])
            echo ""
            echo -e "${C_DIM}Çıkış yapıldı.${C_RESET}"
            exit 0
            ;;
        *)
            # Enter veya başka tuş → Güncelle ve Başlat
            guncelle_ve_baslat
            ;;
    esac
else
    # İlk kullanım veya kurulum yapılmamış — Karşılama menüsü
    show_welcome
    read -n 1 -s -r CHOICE < /dev/tty
    echo ""

    case "$CHOICE" in
        [kK])
            kur
            ;;
        [qQ])
            echo ""
            echo -e "${C_DIM}Çıkış yapıldı. Tekrar bekleriz! 👋${C_RESET}"
            exit 0
            ;;
        *)
            # Enter veya başka tuş → Direkt Kullan
            direkt_kullan
            ;;
    esac
fi
