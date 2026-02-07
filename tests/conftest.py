import pytest
import sys
import os
import json
from unittest.mock import MagicMock, patch, mock_open

# Global mock for curses to prevent any import errors or runtime attempts
# This must be done BEFORE importing any module that uses curses
mock_curses_module = MagicMock()
mock_curses_module.error = Exception
sys.modules['curses'] = mock_curses_module

@pytest.fixture(autouse=True)
def mock_curses():
    """Matches the specific calls used in the app."""
    mock_curses_module.reset_mock()
    # Common curses constants/functions
    mock_curses_module.LINES = 24
    mock_curses_module.COLS = 80
    mock_curses_module.color_pair.return_value = 0
    mock_curses_module.A_BOLD = 0
    mock_curses_module.A_REVERSE = 0
    mock_curses_module.A_NORMAL = 0
    yield mock_curses_module

@pytest.fixture
def mock_fs():
    """
    Mock file system operations.
    Returns a dictionary acting as the virtual file system: {path: content}
    """
    virtual_fs = {}

    def _open_side_effect(file, mode='r', *args, **kwargs):
        file_str = str(file)
        if 'w' in mode:
            # Return a mock file-like object that updates virtual_fs on write
            # Truncate on open
            virtual_fs[file_str] = ""
            
            mock_f = MagicMock()
            def write(content):
                virtual_fs[file_str] += content
            mock_f.write.side_effect = write
            
            # Context manager support
            mock_f.__enter__.return_value = mock_f
            mock_f.__exit__.return_value = None
            mock_f.flush = MagicMock()
            mock_f.fileno = MagicMock(return_value=1)
            return mock_f
        else:
            # Read mode
            if file_str not in virtual_fs:
                raise FileNotFoundError(f"No such file: {file_str}")
            return mock_open(read_data=virtual_fs[file_str]).return_value

    def _exists_side_effect(path):
        return str(path) in virtual_fs
        
    def _remove_side_effect(path):
        path_str = str(path)
        if path_str in virtual_fs:
            del virtual_fs[path_str]
        else:
            raise FileNotFoundError(path_str)

    def _replace_side_effect(src, dst):
        src_str, dst_str = str(src), str(dst)
        if src_str in virtual_fs:
            virtual_fs[dst_str] = virtual_fs[src_str]
            del virtual_fs[src_str]
        else:
            raise FileNotFoundError(src_str)

    def _copy2_side_effect(src, dst):
         src_str, dst_str = str(src), str(dst)
         if src_str in virtual_fs:
             virtual_fs[dst_str] = virtual_fs[src_str]
         else:
             raise FileNotFoundError(src_str)

    with patch('builtins.open', side_effect=_open_side_effect), \
         patch('os.path.exists', side_effect=_exists_side_effect), \
         patch('os.remove', side_effect=_remove_side_effect), \
         patch('os.replace', side_effect=_replace_side_effect), \
         patch('shutil.copy2', side_effect=_copy2_side_effect), \
         patch('os.fsync'): # Mock fsync as it requires real fileno
        yield virtual_fs

@pytest.fixture
def sample_curriculum():
    """Sample curriculum data for testing."""
    return [
        {
            "id": 1,
            "uuid": "test-uuid-1",
            "category": "Temeller",
            "title": "Merhaba Dünya",
            "description": "Ekrana 'Merhaba Dünya' yazdır.",
            "hint": "print() fonksiyonunu kullan.",
        },
        {
            "id": 2,
            "uuid": "test-uuid-2", 
            "category": "Değişkenler",
            "title": "Değişken Tanımlama",
            "description": "x adında bir değişken tanımla ve 5 değerini ata.",
            "hint": "x = 5",
        }
    ]

@pytest.fixture
def clean_env():
    """Clean up environment variables or singletons."""
    # Add any global reset logic here if needed
    yield

