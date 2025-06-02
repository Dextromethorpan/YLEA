"""
Configuration settings for Project 33
Adjust these paths to match your actual project locations
"""

from pathlib import Path


class Config:
    # Project paths - ADJUST THESE TO YOUR ACTUAL LOCATIONS
    # For Windows paths, use one of these methods:
    # Method 1: Raw strings (recommended)
    PROJECT_30_PATH = Path(r"C:\Users\Luciano Muratore\PycharmProjects\pythonProject30")
    PROJECT_31_PATH = Path(r"C:\Users\Luciano Muratore\PycharmProjects\pythonProject31")
    PROJECT_32_PATH = Path(r"C:\Users\Luciano Muratore\PycharmProjects\pythonProject32")

    # Optional: Specify Python executable if different environments are needed
    # Leave as None to use current Python, or specify path to specific Python
    PYTHON_EXECUTABLE = None  # Set to specific path if needed, e.g., r"C:\path\to\python.exe"

    # Method 2: Forward slashes (alternative)
    # PROJECT_30_PATH = Path("C:/Users/Luciano Muratore/PycharmProjects/pythonProject30")
    # PROJECT_31_PATH = Path("C:/Users/Luciano Muratore/PycharmProjects/pythonProject31")
    # PROJECT_32_PATH = Path("C:/Users/Luciano Muratore/PycharmProjects/pythonProject32")

    # Method 3: Double backslashes (alternative)
    # PROJECT_30_PATH = Path("C:\\Users\\Luciano Muratore\\PycharmProjects\\pythonProject30")
    # PROJECT_31_PATH = Path("C:\\Users\\Luciano Muratore\\PycharmProjects\\pythonProject31")
    # PROJECT_32_PATH = Path("C:\\Users\\Luciano Muratore\\PycharmProjects\\pythonProject32")

    # Script names for each project (adjust if different)
    PROJECT_30_SCRIPT = "main.py"
    PROJECT_31_SCRIPT = "main.py"
    PROJECT_32_SCRIPT = "main.py"

    # Folder naming patterns - Updated based on your specifications
    # Project 30: Output -> Videos{Today}
    OUTPUT_30_PATTERN = "Videos{date}"  # Original pattern
    OUTPUT_30_ALTERNATIVE_PATTERNS = ["Videos_{date}", "Videos{date}", "Videos-{date}"]  # Alternative patterns

    # Project 31: Input -> Videos{Today}, Output -> analysis_{Today}
    INPUT_31_PATTERN = "Videos{date}"
    OUTPUT_31_PATTERN = "analysis_{date}"

    # Project 32: Input -> analysis_{Today}, Output -> Output_Analysis_{Today}
    INPUT_32_PATTERN = "analysis_{date}"
    OUTPUT_32_PATTERN = "Output_Analysis_{date}"

    # Final output for Project 33
    FINAL_OUTPUT_PATTERN = "Output_{date}"

    # Logging configuration
    LOG_LEVEL = "INFO"
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

    # Timeout settings (in seconds)
    PROJECT_TIMEOUT = 3600  # 1 hour timeout for each project

    # Non-critical error patterns that shouldn't stop execution
    NON_CRITICAL_ERRORS = [
        "pandas.errors.EmptyDataError",
        "EmptyDataError: No columns to parse from file",
        "UserWarning:",
        "FutureWarning:",
        "DeprecationWarning:"
    ]

    # Optional dependency checking (can be disabled)
    ENABLE_DEPENDENCY_CHECK = False  # Set to True if you want pre-execution dependency checks

    @classmethod
    def get_output_dir_name(cls, project_num: int, date: str) -> str:
        """Get output directory name for a specific project"""
        patterns = {
            30: cls.OUTPUT_30_PATTERN,
            31: cls.OUTPUT_31_PATTERN,
            32: cls.OUTPUT_32_PATTERN
        }
        return patterns[project_num].format(date=date)

    @classmethod
    def get_input_dir_name(cls, project_num: int, date: str) -> str:
        """Get input directory name for a specific project"""
        patterns = {
            31: cls.INPUT_31_PATTERN,
            32: cls.INPUT_32_PATTERN
        }
        return patterns[project_num].format(date=date)

    @classmethod
    def get_project_script(cls, project_num: int) -> str:
        """Get script name for a specific project"""
        scripts = {
            30: cls.PROJECT_30_SCRIPT,
            31: cls.PROJECT_31_SCRIPT,
            32: cls.PROJECT_32_SCRIPT
        }
        return scripts[project_num]

    @classmethod
    def get_project_subdirectory(cls, project_num: int) -> str:
        """Get subdirectory for a specific project (if needed)"""
        if project_num == 31:
            return "youtube-sentiment-analyzer"
        return None

    @classmethod
    def requires_argument(cls, project_num: int) -> bool:
        """Check if a project requires command line argument"""
        return project_num == 31  # Only Project 31 requires argument

    @classmethod
    def get_project_argument(cls, project_num: int, date: str) -> str:
        """Get command line argument for a specific project"""
        if project_num == 31:
            return cls.INPUT_31_PATTERN.format(date=date)
        return None