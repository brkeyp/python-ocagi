#!/bin/bash
#=======================================================
# Python Ocağı - Mac/Linux Otomatik Kurulum ve Başlatma Betiği
#=======================================================

# NOT: Bu dosyayı GitHub'a yüklemeden önce kendi GitHub bilgilerinizi aşağıya giriniz.
REPO_OWNER="brkeyp" # <-- KENDI KULLANICI ADINIZI BURAYA YAZIN
REPO_NAME="python-ocagi"  # <-- GITHUB REPO ADINIZ
BRANCH="main"

ZIP_URL="https://github.com/$REPO_OWNER/$REPO_NAME/archive/refs/heads/$BRANCH.zip"

DESKTOP_DIR="$HOME/Desktop"
APP_DIR="$DESKTOP_DIR/Python Ocağı"
SHORTCUT_FILE="$DESKTOP_DIR/PYTHON OCAĞINA GİR.command"
UNINSTALL_FILE="$APP_DIR/Uygulamayı Kaldır.command"

echo -e "\033[0;36m=========================================\033[0m"
echo -e "\033[0;36mPython Ocağı Kurulumu Başlıyor...\033[0m"
echo -e "\033[0;36m=========================================\033[0m"

# 1. Klasörü Oluştur
mkdir -p "$APP_DIR"

# 2. Python Kontrolü
if ! command -v python3 &> /dev/null
then
    echo -e "\033[0;31mHATA: Sisteminizde Python 3 komutu (\`python3\`) bulunamadı.\033[0m"
    echo -e "\033[0;33mMac için Terminal'e şunu yazabilirsiniz:\033[0m xcode-select --install \033[0;33mveya\033[0m brew install python"
    echo -e "\033[0;33mLinux için:\033[0m sudo apt update && sudo apt install python3"
    exit 1
fi

echo -e "\033[0;32mPython 3 bulundu. Devam ediliyor.\033[0m"

# 3. Kısa Yol Oluştur (.command)
cat << 'EOF' > "$SHORTCUT_FILE"
#!/bin/bash
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

# Mac'te iş bitince pencereyi otomatik kapat (kullanıcı çıkış yaptığında)
if [[ "$OSTYPE" == "darwin"* ]]; then
    osascript -e 'tell application "Terminal" to close front window' & exit
fi
EOF

# Placeholder'ları değiştir
sed -i.bak "s|PLACEHOLDER_ZIP|$ZIP_URL|g" "$SHORTCUT_FILE"
rm -f "$SHORTCUT_FILE.bak"
sed -i.bak "s|PLACEHOLDER_DIR|$REPO_NAME-$BRANCH|g" "$SHORTCUT_FILE"
rm -f "$SHORTCUT_FILE.bak"

chmod +x "$SHORTCUT_FILE"

# 4. Kaldırma Dosyası Oluştur
cat << 'EOF' > "$UNINSTALL_FILE"
#!/bin/bash
echo -e "\033[0;31m=======================================================\033[0m"
echo -e "\033[0;31mDİKKAT: Python Ocağı tamamen siliniyor!\033[0m"
echo -e "\033[0;31mİlerlemeniz, skorlarınız ve projenin bütün dosyaları yok olacak.\033[0m"
echo -e "\033[0;31m=======================================================\033[0m"
read -p "İptal etmek için 'Ctrl+C' yapın. Devam etmek için ENTER'a basın... "

rm -rf "$HOME/Desktop/Python Ocağı"
rm -f "$HOME/Desktop/PYTHON OCAĞINA GİR.command"
rm -rf "$HOME/.python_ocagi"

echo -e ""
echo -e "\033[0;32mUygulama başarıyla kaldırıldı. Bilgisayarınızdan tüm izler silindi.\033[0m"
echo -e ""
read -n 1 -s -r -p "Bu ekranı kapatmak için herhangi bir tuşa basın..."
echo -e ""

if [[ "$OSTYPE" == "darwin"* ]]; then
    osascript -e 'tell application "Terminal" to close front window' & exit
fi
EOF
chmod +x "$UNINSTALL_FILE"

echo -e "\033[0;32m=========================================\033[0m"
echo -e "\033[0;32mKURULUM TAMAMLANDI!\033[0m"
echo -e "\033[0;32m=========================================\033[0m"
echo -e "\033[0;36mUygulamayı hemen başlatmak üzere Masaüstünüzdeki kısayola ulaşılıyor...\033[0m"
sleep 2

# 5. İlk İndirme ve Başlatma
open "$SHORTCUT_FILE" || "$SHORTCUT_FILE"
