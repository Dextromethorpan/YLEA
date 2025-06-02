# PyCharm Project 33 - Master Orchestrator

## Overview
Project 33 is a master orchestrator that manages the sequential execution of Projects 30, 31, and 32, handling data flow between them automatically based on today's date.

## Workflow
1. **Project 30**: Executes and produces `Output_30_YYYY-MM-DD`
2. **Transfer**: Moves Project 30 output to Project 31 as input
3. **Project 31**: Processes input and produces `Output_31_YYYY-MM-DD`
4. **Transfer**: Moves Project 31 output to Project 32 as input
5. **Project 32**: Processes input and produces `Output_32_YYYY-MM-DD`
6. **Final Output**: Creates `Output_YYYY-MM-DD` for Project 33

## Setup Instructions

### 1. Configure Project Paths
Edit `Functions/config.py` and update the paths to match your actual project locations:
```python
PROJECT_30_PATH = Path("../PyCharm_30_Project")  # Update this
PROJECT_31_PATH = Path("../PyCharm_31_Project")  # Update this
PROJECT_32_PATH = Path("../PyCharm_32_Project")  # Update this
