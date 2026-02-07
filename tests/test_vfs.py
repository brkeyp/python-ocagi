# -*- coding: utf-8 -*-
"""
Virtual File System (VFS) Tests

Bu test dosyası vfs.py modülünün doğru çalıştığını doğrular:
1. MockFileHandle okuma/yazma işlemleri
2. MockFileSystem dosya yönetimi
3. Context manager protokolü
4. Hata durumları

Güncel API:
- MockFileHandle(fs, path, mode) - StringIO tabanlı dosya handle
- MockFileSystem - In-memory file system with open/exists/read_file/write_file/remove
"""

import sys
import os
import pytest

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sandbox.vfs import MockFileHandle, MockFileSystem


class TestMockFileHandle:
    """MockFileHandle sınıfı testleri."""
    
    def test_write_mode_creates_empty_file(self):
        """Write modunda açılan dosya boş olmalı."""
        fs = MockFileSystem()
        f = MockFileHandle(fs, "test.txt", "w")
        content = f.getvalue()
        assert content == ""
        f.close()
    
    def test_write_and_read_back(self):
        """Yazılan içerik okunabilmeli."""
        fs = MockFileSystem()
        
        # Write
        f = MockFileHandle(fs, "test.txt", "w")
        f.write("Merhaba")
        f.write(" Dünya")
        f.close()
        
        # Read back
        f2 = MockFileHandle(fs, "test.txt", "r")
        content = f2.read()
        assert "Merhaba Dünya" in content
        f2.close()
    
    def test_read_mode_with_initial_content(self):
        """Başlangıç içeriği okunabilmeli."""
        fs = MockFileSystem()
        fs.write_file("test.txt", "Test içerik")
        
        f = MockFileHandle(fs, "test.txt", "r")
        content = f.read()
        assert content == "Test içerik"
        f.close()
    
    def test_readline_returns_lines(self):
        """readline satır satır okumalı."""
        fs = MockFileSystem()
        fs.write_file("test.txt", "Satır 1\nSatır 2\nSatır 3")
        
        f = MockFileHandle(fs, "test.txt", "r")
        line1 = f.readline()
        line2 = f.readline()
        assert "1" in line1
        assert "2" in line2
        f.close()
    
    def test_readlines_returns_all_lines(self):
        """readlines tüm satırları liste olarak döndürmeli."""
        fs = MockFileSystem()
        fs.write_file("test.txt", "A\nB\nC")
        
        f = MockFileHandle(fs, "test.txt", "r")
        lines = f.readlines()
        assert len(lines) == 3
        f.close()
    
    def test_close_marks_file_closed(self):
        """close() dosyayı kapatmalı."""
        fs = MockFileSystem()
        f = MockFileHandle(fs, "test.txt", "w")
        f.close()
        assert f.closed
    
    def test_context_manager_protocol(self):
        """Context manager protokolü çalışmalı."""
        fs = MockFileSystem()
        
        with MockFileHandle(fs, "test.txt", "w") as f:
            f.write("Test")
        
        assert f.closed
    
    def test_append_mode(self):
        """Append modu mevcut içeriğe eklemeli."""
        fs = MockFileSystem()
        fs.write_file("test.txt", "Mevcut")
        
        with MockFileHandle(fs, "test.txt", "a") as f:
            f.write(" Ek")
        
        content = fs.read_file("test.txt")
        assert "Mevcut Ek" in content
    
    def test_read_nonexistent_raises_error(self):
        """Olmayan dosyayı okumak hata vermeli."""
        fs = MockFileSystem()
        with pytest.raises(FileNotFoundError):
            MockFileHandle(fs, "yok.txt", "r")


class TestMockFileSystem:
    """MockFileSystem sınıfı testleri."""
    
    def test_write_file_creates_file(self):
        """write_file dosya oluşturmalı."""
        fs = MockFileSystem()
        fs.write_file("test.txt", "içerik")
        assert fs.exists("test.txt")
    
    def test_read_file_returns_content(self):
        """read_file dosya içeriğini döndürmeli."""
        fs = MockFileSystem()
        fs.write_file("test.txt", "Merhaba")
        content = fs.read_file("test.txt")
        assert content == "Merhaba"
    
    def test_write_file_updates_content(self):
        """write_file dosya içeriğini güncellemeli."""
        fs = MockFileSystem()
        fs.write_file("test.txt", "eski")
        fs.write_file("test.txt", "yeni")
        assert fs.read_file("test.txt") == "yeni"
    
    def test_remove_deletes_file(self):
        """remove dosyayı silmeli."""
        fs = MockFileSystem()
        fs.write_file("test.txt", "içerik")
        fs.remove("test.txt")
        assert not fs.exists("test.txt")
    
    def test_exists_returns_false_for_missing(self):
        """exists() olmayan dosya için False döndürmeli."""
        fs = MockFileSystem()
        assert not fs.exists("yok.txt")
    
    def test_open_read_mode(self):
        """open() read modunda MockFileHandle döndürmeli."""
        fs = MockFileSystem()
        fs.write_file("test.txt", "içerik")
        f = fs.open("test.txt", "r")
        assert f is not None
        content = f.read()
        assert content == "içerik"
        f.close()
    
    def test_open_write_mode(self):
        """open() write modunda MockFileHandle döndürmeli."""
        fs = MockFileSystem()
        f = fs.open("yeni.txt", "w")
        f.write("Yeni içerik")
        f.close()
        assert fs.exists("yeni.txt")
        assert fs.read_file("yeni.txt") == "Yeni içerik"
    
    def test_read_nonexistent_returns_none(self):
        """Olmayan dosyayı okumak None döndürmeli."""
        fs = MockFileSystem()
        result = fs.read_file("yok.txt")
        assert result is None
    
    def test_remove_nonexistent_raises_error(self):
        """Olmayan dosyayı silmek hata vermeli."""
        fs = MockFileSystem()
        with pytest.raises(FileNotFoundError):
            fs.remove("yok.txt")
    
    def test_binary_mode_not_supported(self):
        """Binary mod desteklenmemeli."""
        fs = MockFileSystem()
        fs.write_file("test.bin", "data")
        with pytest.raises(NotImplementedError):
            fs.open("test.bin", "rb")


class TestMockFileSystemIntegration:
    """VFS entegrasyon testleri."""
    
    def test_multiple_files(self):
        """Birden fazla dosya yönetilebilmeli."""
        fs = MockFileSystem()
        
        fs.write_file("dosya1.txt", "içerik 1")
        fs.write_file("dosya2.txt", "içerik 2")
        fs.write_file("dosya3.txt", "içerik 3")
        
        assert fs.read_file("dosya1.txt") == "içerik 1"
        assert fs.read_file("dosya2.txt") == "içerik 2"
        assert fs.read_file("dosya3.txt") == "içerik 3"
    
    def test_overwrite_file(self):
        """Dosya üzerine yazılabilmeli."""
        fs = MockFileSystem()
        
        fs.write_file("test.txt", "eski içerik")
        fs.write_file("test.txt", "yeni içerik")
        
        assert fs.read_file("test.txt") == "yeni içerik"
    
    def test_empty_file(self):
        """Boş dosya oluşturulabilmeli."""
        fs = MockFileSystem()
        fs.write_file("bos.txt", "")
        
        assert fs.exists("bos.txt")
        assert fs.read_file("bos.txt") == ""
    
    def test_file_operations_chain(self):
        """Zincirleme dosya işlemleri çalışmalı."""
        fs = MockFileSystem()
        
        # Create
        fs.write_file("chain.txt", "başlangıç")
        assert fs.exists("chain.txt")
        
        # Read
        assert fs.read_file("chain.txt") == "başlangıç"
        
        # Update via open
        with fs.open("chain.txt", "w") as f:
            f.write("güncellenmiş")
        
        assert fs.read_file("chain.txt") == "güncellenmiş"
        
        # Delete
        fs.remove("chain.txt")
        assert not fs.exists("chain.txt")


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
