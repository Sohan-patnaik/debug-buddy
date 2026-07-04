import sys
import subprocess
import tempfile
import os
from pathlib import Path
from core.logger import get_logger

logger = get_logger(__name__)

class PythonExecutor:
    """Executes Python code in a safe subprocess and captures outputs/tracebacks."""

    def __init__(self, timeout: float = 5.0):
        self.timeout = timeout

    def execute_code(self, code: str, reference_filepath: Path) -> dict:
        """
        Writes code to a temporary file located next to the reference file
        (to maintain relative import context), executes it, and returns results.
        """
        ref_dir = reference_filepath.parent
        # Create a temp file in the same directory to preserve local imports
        temp_file = tempfile.NamedTemporaryFile(
            mode="w",
            dir=ref_dir,
            suffix=".py",
            prefix="_debug_temp_",
            delete=False,
            encoding="utf-8"
        )
        temp_path = Path(temp_file.name)
        
        try:
            temp_file.write(code)
            temp_file.close()

            logger.info(f"Executing temp file: {temp_path.name} with timeout {self.timeout}s")
            
            # Execute python in a subprocess using the current interpreter
            result = subprocess.run(
                [sys.executable, str(temp_path)],
                capture_output=True,
                text=True,
                timeout=self.timeout,
                cwd=str(ref_dir)
            )

            # Cleanup tracebacks to remove the temporary filename reference
            stderr = result.stderr.replace(str(temp_path), reference_filepath.name)

            return {
                "success": result.returncode == 0,
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": stderr,
                "timeout": False
            }

        except subprocess.TimeoutExpired as e:
            logger.warning(f"Subprocess execution timed out after {self.timeout} seconds")
            return {
                "success": False,
                "returncode": -1,
                "stdout": e.stdout or "",
                "stderr": f"TimeoutExpired: Execution exceeded {self.timeout} seconds.",
                "timeout": True
            }
        except Exception as e:
            logger.error(f"Error executing code: {e}")
            return {
                "success": False,
                "returncode": -1,
                "stdout": "",
                "stderr": str(e),
                "timeout": False
            }
        finally:
            # Always clean up the temp file
            if temp_path.exists():
                try:
                    os.remove(temp_path)
                except Exception as cleanup_err:
                    logger.warning(f"Failed to remove temp file {temp_path}: {cleanup_err}")
