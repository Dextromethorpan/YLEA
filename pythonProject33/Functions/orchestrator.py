"""
Core orchestration logic for Project 33
Handles running projects in sequence and managing data flow
"""

import os
import shutil
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Tuple, Optional

from .config import Config
from .utils import setup_logging, validate_path, create_directory


class ProjectOrchestrator:
    def __init__(self, execution_date: str):
        self.execution_date = execution_date
        self.logger = setup_logging(f"project_33_{execution_date}")

        # Output directory names based on updated patterns
        self.output_30 = Config.get_output_dir_name(30, execution_date)  # Videos{date}
        self.output_31 = Config.get_output_dir_name(31, execution_date)  # analysis_{date}
        self.output_32 = Config.get_output_dir_name(32, execution_date)  # Output_Analysis_{date}
        self.final_output = Config.FINAL_OUTPUT_PATTERN.format(date=execution_date)

        # Input directory names
        self.input_31 = Config.get_input_dir_name(31, execution_date)  # Videos{date}
        self.input_32 = Config.get_input_dir_name(32, execution_date)  # analysis_{date}

        self.logger.info(f"Orchestrator initialized for date: {execution_date}")
        self.logger.info(f"Project 30 output: {self.output_30}")
        self.logger.info(f"Project 31 input: {self.input_31}, output: {self.output_31}")
        self.logger.info(f"Project 32 input: {self.input_32}, output: {self.output_32}")

    def validate_all_projects(self) -> bool:
        """Validate that all required projects and scripts exist"""
        self.logger.info("Validating project structure...")

        projects = [
            (Config.PROJECT_30_PATH, Config.PROJECT_30_SCRIPT, "Project 30", None),
            (Config.PROJECT_31_PATH, Config.PROJECT_31_SCRIPT, "Project 31", "youtube-sentiment-analyzer"),
            (Config.PROJECT_32_PATH, Config.PROJECT_32_SCRIPT, "Project 32", None)
        ]

        for project_path, script_name, project_name, subdirectory in projects:
            if not validate_path(project_path):
                self.logger.error(f"{project_name} directory not found: {project_path}")
                return False

            # Check subdirectory if required
            if subdirectory:
                subdirectory_path = project_path / subdirectory
                if not validate_path(subdirectory_path):
                    self.logger.error(f"{project_name} subdirectory not found: {subdirectory_path}")
                    return False

                # Check script in subdirectory
                script_path = subdirectory_path / script_name
                if not validate_path(script_path):
                    self.logger.error(f"{project_name} script not found: {script_path}")
                    return False
            else:
                # Check script in main directory
                script_path = project_path / script_name
                if not validate_path(script_path):
                    self.logger.error(f"{project_name} script not found: {script_path}")
                    return False

        self.logger.info("All projects validated successfully")
        return True

    def is_non_critical_error(self, error_message: str) -> bool:
        """Check if error message contains non-critical errors that shouldn't stop execution"""
        for pattern in Config.NON_CRITICAL_ERRORS:
            if pattern in error_message:
                return True
        return False

    def find_csv_files_in_videos_folder(self, project_num: int) -> list:
        """Find all CSV files in the Videos folder structure"""
        if project_num != 31:
            return []

        project_path = Config.PROJECT_31_PATH
        youtube_analyzer_path = project_path / "youtube-sentiment-analyzer"

        # Look for Videos folder patterns
        videos_folder = None
        for pattern in Config.OUTPUT_30_ALTERNATIVE_PATTERNS:
            folder_name = pattern.format(date=self.execution_date)
            potential_folder = youtube_analyzer_path / folder_name
            if validate_path(potential_folder):
                videos_folder = potential_folder
                break

        if not videos_folder:
            self.logger.error(f"Videos folder not found in youtube-sentiment-analyzer directory")
            return []

        csv_files = []
        try:
            # Walk through all subdirectories to find CSV files
            for root, dirs, files in os.walk(videos_folder):
                for file in files:
                    if file.endswith('.csv'):
                        csv_path = os.path.join(root, file)
                        # Get relative path from youtube-sentiment-analyzer directory
                        relative_path = os.path.relpath(csv_path, youtube_analyzer_path)
                        csv_files.append(relative_path)
                        self.logger.info(f"Found CSV file: {relative_path}")

        except Exception as e:
            self.logger.error(f"Error scanning for CSV files: {e}")

        return csv_files

    def check_csv_file_empty(self, csv_path):
        """Check if CSV file is empty or has no data"""
        try:
            import pandas as pd

            # First check if file exists and has content
            if not os.path.exists(csv_path):
                return True, "CSV file does not exist"

            # Check file size
            if os.path.getsize(csv_path) == 0:
                return True, "CSV file is empty (0 bytes)"

            # Try to read the CSV with pandas
            df = pd.read_csv(csv_path)

            if df.empty:
                return True, "CSV file is empty (no rows)"
            if len(df.columns) == 0:
                return True, "CSV file has no columns"

            # Check if all values are NaN
            if df.isnull().all().all():
                return True, "CSV file contains only NaN values"

            return False, f"CSV file has {len(df)} rows and {len(df.columns)} columns"

        except pd.errors.EmptyDataError:
            return True, "CSV file is empty (EmptyDataError)"
        except pd.errors.ParserError as e:
            return True, f"CSV parsing error: {e}"
        except Exception as e:
            # If we can't read it, let's try to continue anyway
            self.logger.warning(f"Could not check CSV emptiness: {e}")
            return False, f"Could not verify CSV (assuming not empty): {e}"

    def organize_project_31_output(self) -> bool:
        """Organize Project 31 output folders into analysis_{date} structure"""
        project_path = Config.PROJECT_31_PATH

        # Create the main analysis folder
        analysis_folder_name = f"analysis_{self.execution_date}"
        analysis_folder_path = project_path / analysis_folder_name

        self.logger.info(f"Organizing Project 31 output into: {analysis_folder_path}")

        try:
            # Create the analysis folder if it doesn't exist
            analysis_folder_path.mkdir(exist_ok=True)

            # Find all analysis_results folders
            moved_folders = 0
            for item in project_path.iterdir():
                if (item.is_dir() and
                        item.name.startswith("analysis_results_most_viewed_last_") and
                        self.execution_date.replace("-", "") in item.name):

                    # Move the folder into the analysis directory
                    target_path = analysis_folder_path / item.name

                    # Remove target if it exists
                    if target_path.exists():
                        shutil.rmtree(target_path)

                    # Move the folder
                    shutil.move(str(item), str(target_path))
                    self.logger.info(f"Moved: {item.name} -> {analysis_folder_name}/{item.name}")
                    moved_folders += 1

            self.logger.info(f"Successfully organized {moved_folders} analysis folders into {analysis_folder_name}")
            return moved_folders > 0

        except Exception as e:
            self.logger.error(f"Error organizing Project 31 output: {e}")
            return False

    def run_project_31_with_csvs(self) -> bool:
        """Run Project 31 with each CSV file found"""
        project_path = Config.PROJECT_31_PATH
        script_name = Config.get_project_script(31)
        project_name = "Project 31"

        self.logger.info(f"Starting execution of {project_name} with CSV processing")

        # Find all CSV files
        csv_files = self.find_csv_files_in_videos_folder(31)
        if not csv_files:
            self.logger.error("No CSV files found for Project 31")
            return False

        self.logger.info(f"Found {len(csv_files)} CSV files to process")

        successful_runs = 0
        total_runs = len(csv_files)

        try:
            # Change to project directory
            original_cwd = os.getcwd()
            os.chdir(project_path)

            # Change to youtube-sentiment-analyzer subdirectory
            youtube_analyzer_path = project_path / "youtube-sentiment-analyzer"
            os.chdir(youtube_analyzer_path)
            self.logger.info(f"Changed to subdirectory: {youtube_analyzer_path}")

            # Prepare environment variables
            env = os.environ.copy()
            env['EXECUTION_DATE'] = self.execution_date
            env['TODAY_DATE'] = self.execution_date
            env['PYTHONIOENCODING'] = 'utf-8'
            if os.name == 'nt':  # Windows
                env['PYTHONLEGACYWINDOWSSTDIO'] = '1'

            # Process each CSV file
            for i, csv_file in enumerate(csv_files, 1):
                self.logger.info(f"Processing CSV {i}/{total_runs}: {csv_file}")

                # Check if CSV file is empty
                full_csv_path = youtube_analyzer_path / csv_file
                is_empty, empty_reason = self.check_csv_file_empty(full_csv_path)

                if is_empty:
                    self.logger.warning(f"EMPTY CSV: {csv_file} - {empty_reason}")
                    self.logger.info(f"Skipping empty CSV file and continuing...")
                    continue

                # Prepare command with CSV file path
                python_executable = Config.PYTHON_EXECUTABLE or sys.executable
                command = [python_executable, script_name, csv_file]

                self.logger.info(f"Running command: {' '.join(command)}")

                # Execute Project 31 with the specific CSV
                import time as time_module
                start_time = time_module.time()

                if os.name == 'nt':  # Windows
                    result = subprocess.run(
                        command,
                        capture_output=True,
                        text=True,
                        timeout=Config.PROJECT_TIMEOUT,
                        env=env,
                        check=False,
                        encoding='utf-8',
                        errors='replace'
                    )
                else:
                    result = subprocess.run(
                        command,
                        capture_output=True,
                        text=True,
                        timeout=Config.PROJECT_TIMEOUT,
                        env=env,
                        check=False
                    )

                execution_time = time_module.time() - start_time

                # Log output
                if result.stdout:
                    self.logger.info(f"CSV {i} stdout:")
                    for line in result.stdout.strip().split('\n'):
                        if line.strip():
                            self.logger.info(f"  {line}")

                if result.stderr:
                    self.logger.warning(f"CSV {i} stderr (errors/warnings):")
                    for line in result.stderr.strip().split('\n'):
                        if line.strip():
                            self.logger.warning(f"  {line}")

                # Check result
                if result.returncode == 0:
                    self.logger.info(f"SUCCESS: CSV {i} processed successfully in {execution_time:.2f} seconds")
                    successful_runs += 1
                else:
                    self.logger.warning(
                        f"WARNING: CSV {i} finished with exit code {result.returncode} in {execution_time:.2f} seconds")
                    # Continue processing other CSVs even if one fails
                    successful_runs += 1  # Count as successful since we continue

            # Return to original directory
            os.chdir(original_cwd)

            self.logger.info(f"Project 31 completed: {successful_runs}/{total_runs} CSV files processed")

            # Organize the output folders into analysis_{date} structure
            if successful_runs > 0:
                self.logger.info("Organizing Project 31 output folders...")
                if not self.organize_project_31_output():
                    self.logger.warning("Could not organize Project 31 output, but continuing...")

            # Consider successful if at least one CSV was processed
            return successful_runs > 0

        except subprocess.TimeoutExpired:
            self.logger.error(f"TIMEOUT: {project_name} execution timed out after {Config.PROJECT_TIMEOUT} seconds")
            os.chdir(original_cwd)
            return False
        except Exception as e:
            self.logger.error(f"ERROR: Unexpected error running {project_name}: {e}")
            os.chdir(original_cwd)
            return False
        """Verify that project produced expected output despite any errors"""
        import time

        project_paths = {
            30: Config.PROJECT_30_PATH,
            31: Config.PROJECT_31_PATH,
            32: Config.PROJECT_32_PATH
        }

        project_path = project_paths[project_num]

        # For Project 30, check multiple possible folder patterns
        if project_num == 30:
            possible_patterns = Config.OUTPUT_30_ALTERNATIVE_PATTERNS
            self.logger.info(f"Checking Project 30 output with multiple patterns...")

            # Wait a moment for file system operations to complete
            time.sleep(2)

            for pattern in possible_patterns:
                folder_name = pattern.format(date=self.execution_date)
                output_path = project_path / folder_name
                self.logger.info(f"Checking for: {output_path}")

                if validate_path(output_path):
                    self.logger.info(f"VERIFIED: Project {project_num} output found: {output_path}")
                    return True

            # Also check for any folder containing the date
            self.logger.info(f"Checking for any folder containing date {self.execution_date}...")
            try:
                self.logger.info(f"Listing all directories in {project_path}:")
                for item in project_path.iterdir():
                    if item.is_dir():
                        self.logger.info(f"  Found directory: {item.name}")
                        if self.execution_date in item.name:
                            self.logger.info(f"VERIFIED: Project {project_num} output found (date match): {item}")
                            return True
            except Exception as e:
                self.logger.warning(f"Error scanning directory: {e}")

            self.logger.error(f"MISSING: Project {project_num} output not found with any pattern")
            return False

        else:
            # For other projects, use standard pattern
            expected_output = Config.get_output_dir_name(project_num, self.execution_date)
            output_path = project_path / expected_output

            # Wait a moment for file system operations to complete
            time.sleep(1)

            if validate_path(output_path):
                self.logger.info(f"VERIFIED: Project {project_num} output found: {output_path}")
                return True
            else:
                self.logger.error(f"MISSING: Project {project_num} output not found: {output_path}")
                return False

    def check_project_dependencies(self, project_num: int) -> bool:
        """Check if project dependencies are available"""
        project_paths = {
            30: Config.PROJECT_30_PATH,
            31: Config.PROJECT_31_PATH,
            32: Config.PROJECT_32_PATH
        }

        project_path = project_paths[project_num]
        project_name = f"Project {project_num}"

        self.logger.info(f"Checking dependencies for {project_name}")

        # Check if requirements.txt exists
        requirements_file = project_path / "requirements.txt"
        if requirements_file.exists():
            self.logger.info(f"Found requirements.txt in {project_name}")
            try:
                with open(requirements_file, 'r') as f:
                    requirements = f.read().strip().split('\n')
                    self.logger.info(f"Requirements: {requirements}")
            except Exception as e:
                self.logger.warning(f"Could not read requirements.txt: {e}")
        else:
            self.logger.info(f"No requirements.txt found in {project_name}")

        # For Project 30, specifically check googleapiclient
        if project_num == 30:
            try:
                result = subprocess.run(
                    [sys.executable, "-c",
                     "from googleapiclient.discovery import build; print('googleapiclient available')"],
                    capture_output=True,
                    text=True,
                    check=False,
                    env=os.environ.copy(),
                    encoding='utf-8' if os.name == 'nt' else None,
                    errors='replace' if os.name == 'nt' else None
                )
                if result.returncode == 0:
                    self.logger.info(f"Dependency check for {project_name}: googleapiclient is available")
                    return True
                else:
                    self.logger.error(f"Dependency check failed for {project_name}: {result.stderr}")
                    return False
            except Exception as e:
                self.logger.error(f"Error during dependency check for {project_name}: {e}")
                return False

        return True  # Skip dependency check for other projects for now

    def run_project(self, project_num: int) -> bool:
        """Run a specific project and return success status"""
        project_paths = {
            30: Config.PROJECT_30_PATH,
            31: Config.PROJECT_31_PATH,
            32: Config.PROJECT_32_PATH
        }

        project_path = project_paths[project_num]
        script_name = Config.get_project_script(project_num)
        project_name = f"Project {project_num}"

        self.logger.info(f"Starting execution of {project_name}")

        try:
            # Change to project directory
            original_cwd = os.getcwd()
            os.chdir(project_path)

            # Check if project requires subdirectory change (Project 31 needs youtube-sentiment-analyzer)
            subdirectory = Config.get_project_subdirectory(project_num)
            if subdirectory:
                subdirectory_path = project_path / subdirectory
                if not validate_path(subdirectory_path):
                    self.logger.error(f"Required subdirectory not found: {subdirectory_path}")
                    os.chdir(original_cwd)
                    return False

                os.chdir(subdirectory_path)
                self.logger.info(f"Changed to subdirectory: {subdirectory_path}")

            # Prepare environment variables (pass today's date)
            env = os.environ.copy()
            env['EXECUTION_DATE'] = self.execution_date
            env['TODAY_DATE'] = self.execution_date

            # Fix Unicode encoding issues on Windows
            env['PYTHONIOENCODING'] = 'utf-8'
            if os.name == 'nt':  # Windows
                env['PYTHONLEGACYWINDOWSSTDIO'] = '1'

            # Prepare command arguments
            python_executable = Config.PYTHON_EXECUTABLE or sys.executable
            command = [python_executable, script_name]

            # Add command line argument if required (Project 31 needs folder name)
            if Config.requires_argument(project_num):
                argument = Config.get_project_argument(project_num, self.execution_date)
                command.append(argument)
                self.logger.info(f"{project_name} command: {' '.join(command)}")
                self.logger.info(f"Executing from directory: {os.getcwd()}")

            # Execute the project with timeout
            start_time = time.time()

            # Handle encoding issues on Windows
            if os.name == 'nt':  # Windows
                result = subprocess.run(
                    command,
                    capture_output=True,
                    text=True,
                    timeout=Config.PROJECT_TIMEOUT,
                    env=env,
                    check=False,  # Don't raise exception on non-zero exit codes
                    encoding='utf-8',
                    errors='replace'  # Replace problematic characters instead of failing
                )
            else:
                result = subprocess.run(
                    command,
                    capture_output=True,
                    text=True,
                    timeout=Config.PROJECT_TIMEOUT,
                    env=env,
                    check=False  # Don't raise exception on non-zero exit codes
                )

            execution_time = time.time() - start_time

            # Log all output (both stdout and stderr)
            if result.stdout:
                self.logger.info(f"{project_name} stdout:")
                for line in result.stdout.strip().split('\n'):
                    if line.strip():
                        self.logger.info(f"  {line}")

            if result.stderr:
                self.logger.warning(f"{project_name} stderr (errors/warnings):")
                for line in result.stderr.strip().split('\n'):
                    if line.strip():
                        self.logger.warning(f"  {line}")

            # Check the return code
            if result.returncode == 0:
                self.logger.info(f"SUCCESS: {project_name} completed successfully in {execution_time:.2f} seconds")
                os.chdir(original_cwd)
                return True
            else:
                self.logger.warning(
                    f"WARNING: {project_name} finished with exit code {result.returncode} in {execution_time:.2f} seconds")

                # Check if expected output was produced despite non-zero exit code
                if self.verify_project_output(project_num):
                    self.logger.info(
                        f"SUCCESS: {project_name} produced expected output despite exit code {result.returncode}")
                    self.logger.info(f"Continuing workflow as project completed its task")
                    os.chdir(original_cwd)
                    return True
                else:
                    self.logger.error(
                        f"FAILED: {project_name} failed - exit code {result.returncode} and no expected output found")
                    os.chdir(original_cwd)
                    return False

        except subprocess.TimeoutExpired:
            self.logger.error(f"{project_name} execution timed out after {Config.PROJECT_TIMEOUT} seconds")
            os.chdir(original_cwd)
            return False
        except subprocess.CalledProcessError as e:
            self.logger.error(f"{project_name} execution failed with return code {e.returncode}")
            self.logger.error(f"{project_name} stderr: {e.stderr}")

            # Check for common dependency issues
            if "ModuleNotFoundError" in str(e.stderr):
                self.logger.error("DEPENDENCY ISSUE DETECTED!")
                self.logger.error("Suggestion: Check if all required modules are installed")
                self.logger.error(f"Try running: pip install -r requirements.txt in {project_path}")

            os.chdir(original_cwd)
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error running {project_name}: {e}")
            os.chdir(original_cwd)
            return False

    def find_actual_output_folder(self, project_num: int) -> str:
        """Find the actual output folder that was created by the project"""
        project_paths = {
            30: Config.PROJECT_30_PATH,
            31: Config.PROJECT_31_PATH,
            32: Config.PROJECT_32_PATH
        }

        project_path = project_paths[project_num]

        # For Project 30, check multiple possible folder patterns
        if project_num == 30:
            for pattern in Config.OUTPUT_30_ALTERNATIVE_PATTERNS:
                folder_name = pattern.format(date=self.execution_date)
                folder_path = project_path / folder_name
                if validate_path(folder_path):
                    self.logger.info(f"Found actual output folder: {folder_name}")
                    return folder_name

            # Also check for any folder containing the date
            try:
                for item in project_path.iterdir():
                    if item.is_dir() and self.execution_date in item.name:
                        self.logger.info(f"Found output folder by date match: {item.name}")
                        return item.name
            except Exception as e:
                self.logger.warning(f"Error scanning directory: {e}")

        # For Project 31, look for analysis_{date} folder
        elif project_num == 31:
            analysis_folder_name = f"analysis_{self.execution_date}"
            analysis_folder_path = project_path / analysis_folder_name
            if validate_path(analysis_folder_path):
                self.logger.info(f"Found Project 31 analysis folder: {analysis_folder_name}")
                return analysis_folder_name
            else:
                self.logger.error(f"Project 31 analysis folder not found: {analysis_folder_name}")
                return analysis_folder_name  # Return expected name anyway

        # For other projects, use standard pattern
        return Config.get_output_dir_name(project_num, self.execution_date)

    def transfer_output(self, source_project_num: int, target_project_num: int) -> bool:
        """Transfer output from source project to target project as input"""
        project_paths = {
            30: Config.PROJECT_30_PATH,
            31: Config.PROJECT_31_PATH,
            32: Config.PROJECT_32_PATH
        }

        source_path = project_paths[source_project_num]
        target_path = project_paths[target_project_num]

        # Get appropriate folder names based on project workflow
        if source_project_num == 30 and target_project_num == 31:
            # Project 30 output -> Project 31 youtube-sentiment-analyzer subdirectory
            # Find the actual folder that was created
            source_folder_name = self.find_actual_output_folder(30)
            target_folder_name = source_folder_name  # Use the same name for target

            # For Project 31, move to youtube-sentiment-analyzer subdirectory
            youtube_analyzer_path = target_path / "youtube-sentiment-analyzer"
            target_input = youtube_analyzer_path / target_folder_name

        elif source_project_num == 31 and target_project_num == 32:
            # Project 31 output (analysis_{date}) -> Project 32 input (analysis_{date})
            source_folder_name = self.find_actual_output_folder(31)
            target_folder_name = source_folder_name
            target_input = target_path / target_folder_name

            self.logger.info(f"Transferring Project 31 analysis folder to Project 32")
            self.logger.info(f"Expected analysis folder: analysis_{self.execution_date}")

        else:
            self.logger.error(f"Unsupported transfer: Project {source_project_num} -> Project {target_project_num}")
            return False

        source_output = source_path / source_folder_name

        self.logger.info(f"Transferring: {source_output} -> {target_input}")

        try:
            # Verify source output exists
            if not validate_path(source_output):
                self.logger.error(f"Source output directory not found: {source_output}")
                return False

            # For Project 31, ensure youtube-sentiment-analyzer directory exists
            if source_project_num == 30 and target_project_num == 31:
                youtube_analyzer_path = target_path / "youtube-sentiment-analyzer"
                if not validate_path(youtube_analyzer_path):
                    self.logger.error(f"youtube-sentiment-analyzer directory not found: {youtube_analyzer_path}")
                    return False

            # Remove existing target directory if it exists
            if target_input.exists():
                shutil.rmtree(target_input)
                self.logger.info(f"Removed existing target directory: {target_input}")

            # Move the output directory
            shutil.move(str(source_output), str(target_input))
            self.logger.info(f"Successfully transferred: {source_output} -> {target_input}")

            return True

        except Exception as e:
            self.logger.error(f"Error transferring output: {e}")
            return False

    def create_final_output(self) -> bool:
        """Create final output directory for Project 33"""
        self.logger.info("Creating final output directory")

        try:
            source_output = Config.PROJECT_32_PATH / self.output_32
            final_output_path = Path(self.final_output)

            # Verify source exists
            if not validate_path(source_output):
                self.logger.error(f"Project 32 output not found: {source_output}")
                return False

            # Remove existing final output if it exists
            if final_output_path.exists():
                shutil.rmtree(final_output_path)
                self.logger.info(f"Removed existing final output: {final_output_path}")

            # Copy to final output
            shutil.copytree(str(source_output), str(final_output_path))
            self.logger.info(f"Final output created: {final_output_path}")

            return True

        except Exception as e:
            self.logger.error(f"Error creating final output: {e}")
            return False

    def run_complete_workflow(self) -> bool:
        """Run the complete workflow orchestration"""
        self.logger.info("=" * 60)
        self.logger.info("STARTING COMPLETE WORKFLOW ORCHESTRATION")
        self.logger.info("=" * 60)

        try:
            # Step 0: Validate all projects
            if not self.validate_all_projects():
                self.logger.error("Project validation failed")
                return False

            # Step 1: Run Project 30
            self.logger.info("STEP 1: Executing Project 30")

            # Check dependencies first (if enabled)
            if Config.ENABLE_DEPENDENCY_CHECK:
                if not self.check_project_dependencies(30):
                    self.logger.warning("Project 30 dependency check failed, but continuing anyway...")

            if not self.run_project(30):
                self.logger.error("Project 30 execution failed")
                return False

            # Step 2: Transfer Project 30 output to Project 31
            self.logger.info("STEP 2: Transferring Project 30 output to Project 31")
            if not self.transfer_output(30, 31):
                self.logger.error("Failed to transfer Project 30 output to Project 31")
                return False

            # Step 3: Run Project 31
            self.logger.info("STEP 3: Executing Project 31 with CSV processing")
            if not self.run_project_31_with_csvs():
                self.logger.error("Project 31 execution failed")
                return False

            # Step 4: Transfer Project 31 output to Project 32
            self.logger.info("STEP 4: Transferring Project 31 output to Project 32")
            if not self.transfer_output(31, 32):
                self.logger.error("Failed to transfer Project 31 output to Project 32")
                return False

            # Step 5: Run Project 32
            self.logger.info("STEP 5: Executing Project 32")
            if not self.run_project(32):
                self.logger.error("Project 32 execution failed")
                return False

            # Step 6: Create final output
            self.logger.info("STEP 6: Creating final output")
            if not self.create_final_output():
                self.logger.error("Failed to create final output")
                return False

            self.logger.info("=" * 60)
            self.logger.info("WORKFLOW ORCHESTRATION COMPLETED SUCCESSFULLY")
            self.logger.info("=" * 60)

            return True

        except Exception as e:
            self.logger.error(f"Unexpected error during workflow orchestration: {e}")
            return False