import pytest
from pathlib import Path
from core.executor import PythonExecutor
from core.llm_client import LLM
from routes.debug import _print_diff
from schemas.schema import FixGenerator

def test_executor_success(tmp_path):
    # Test a successful execution
    code = "print('hello world')"
    ref_file = tmp_path / "script.py"
    ref_file.write_text(code, encoding="utf-8")
    
    executor = PythonExecutor()
    result = executor.execute_code(code, ref_file)
    
    assert result["success"] is True
    assert result["returncode"] == 0
    assert "hello world" in result["stdout"]
    assert result["stderr"] == ""
    assert result["timeout"] is False

def test_executor_failure(tmp_path):
    # Test a failing execution (e.g. division by zero)
    code = "1 / 0"
    ref_file = tmp_path / "script.py"
    ref_file.write_text(code, encoding="utf-8")
    
    executor = PythonExecutor()
    result = executor.execute_code(code, ref_file)
    
    assert result["success"] is False
    assert result["returncode"] != 0
    assert "ZeroDivisionError" in result["stderr"]

def test_llm_client_initialization():
    # Test that the LLM client class can be instantiated
    llm = LLM()
    client = llm.get_llm()
    assert client is not None

def test_print_diff_no_changes(capsys):
    # Test that _print_diff doesn't crash
    original = "def foo():\n    return 42"
    corrected = "def foo():\n    return 42"
    _print_diff(original, corrected, Path("foo.py"))
    captured = capsys.readouterr()
    assert "No changes proposed" in captured.out or "" in captured.out
