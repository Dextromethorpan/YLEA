#!/usr/bin/env python3
"""
PyCharm Project 33 - Master Orchestrator
Main entry point for the project workflow orchestration
"""

import sys
import os
from datetime import datetime
from pathlib import Path

# Add project root and Functions folder to Python path
project_root = Path(__file__).parent
functions_path = project_root / "Functions"
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(functions_path))

# Import from Functions folder
from Functions.orchestrator import ProjectOrchestrator
from Functions.config import Config


def main():
    """Main entry point for Project 33"""
    print("=" * 70)
    print("          PyCharm Project 33 - Master Orchestrator")
    print("=" * 70)

    try:
        # Initialize orchestrator with today's date
        today = datetime.now().strftime('%Y-%m-%d')
        orchestrator = ProjectOrchestrator(today)

        # Display configuration
        print(f"Execution Date: {today}")
        print(f"Project 30 Path: {Config.PROJECT_30_PATH}")
        print(f"Project 31 Path: {Config.PROJECT_31_PATH}")
        print(f"Project 32 Path: {Config.PROJECT_32_PATH}")
        print(f"Project 30 Output: Videos{today}")
        print(f"Project 31 Input: Videos{today} -> Output: analysis_{today}")
        print(f"Project 32 Input: analysis_{today} -> Output: Output_Analysis_{today}")
        print(f"Final Output: Output_{today}")
        print(f"⚠️  All project errors will be logged, but workflow continues if projects produce expected output")
        print("=" * 70)

        # Run the complete orchestration
        success = orchestrator.run_complete_workflow()

        if success:
            print("\n" + "=" * 70)
            print("          🎉 ORCHESTRATION COMPLETED SUCCESSFULLY! 🎉")
            print(f"          Final output available: Output_{today}")
            print("=" * 70)
            return 0
        else:
            print("\n" + "=" * 70)
            print("          ❌ ORCHESTRATION FAILED!")
            print("          Check logs for details")
            print("=" * 70)
            return 1

    except KeyboardInterrupt:
        print("\n\n⚠️  Orchestration interrupted by user")
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)