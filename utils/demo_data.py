
# ==============================
# LIBRARY IMPORTS
# ==============================

import datetime
import json
import logging
import shutil

from pathlib import Path


# ==============================
# FUNCTION IMPORTS
# ==============================

from modules.events import update_events

from utils.utils import (
    confirm_action,
    get_input,
    print_message,
    update_record,
)


# ==============================
# CONSTANTS
# ==============================

from utils.constants import DATA_FILES


# ==============================
# LOGGING
# ==============================

logger = logging.getLogger(__name__)


# ==============================
# DIRECTORY CONFIGURATION
# ==============================

PROJECT_DIR = Path(__file__).resolve().parent.parent
SOURCE_DIR = PROJECT_DIR / "demo_data"
TARGET_DIR = PROJECT_DIR / "data"


# ==============================
# DEMO DATA MANAGEMENT
# ==============================

def load_demo_data():
    """
    Loads the demo JSON files into the application data directory.

    Validates all required demo JSON files before copying them to the
    application data directory. Existing files with matching names are
    overwritten, while missing target files and directories are created.

    Updates demo event 5 to the current date and refreshes the event
    statuses after loading the demo data.

    Returns:
        None: Returns when the operation is completed, cancelled,
            or aborted due to an error.
    """
    if not confirm_action("load", "demo data"):
        return

    try:
        source_files = [
            SOURCE_DIR / f"{data_type}.json"
            for data_type in DATA_FILES
        ]

        # Validate all required demo JSON files before copying.
        for source_file in source_files:
            with open(source_file, "r", encoding="utf-8") as file:
                json.load(file)

        # Create the target directory if it does not exist.
        TARGET_DIR.mkdir(parents=True, exist_ok=True)

        # Copy the validated JSON files to the application data directory.
        for source_file in source_files:
            target_file = TARGET_DIR / source_file.name
            shutil.copyfile(source_file, target_file)

        # Update the demo event date and refresh the event statuses.
        today = datetime.date.today().strftime("%d-%m-%Y")

        update_record("events", "5", "date", today)
        update_events()

    except (OSError, ValueError, UnicodeError):
        logger.exception("Failed to load demo data.")
        print_message("Failed to load demo data. Please check the application log.\n", "red")
        get_input()
        return

    print_message("Demo data successfully loaded.\n", "green")
    get_input()

    return


# ==============================
# APPLICATION DATA MANAGEMENT
# ==============================

def reset_application_data():
    """
    Resets all application JSON files to empty dictionaries.

    Replaces the contents of each required JSON file in the application
    data directory with an empty dictionary. Missing files and directories
    are created automatically.

    Uses temporary files to safely replace individual JSON files.
    The original demo JSON files remain unchanged.

    Returns:
        None: Returns when the operation is completed, cancelled,
            or aborted due to an error.
    """
    if not confirm_action("reset", "application data"):
        return

    try:
        # Create the target directory if it does not exist.
        TARGET_DIR.mkdir(parents=True, exist_ok=True)

        # Determine the required application JSON files.
        target_files = [
            TARGET_DIR / f"{data_type}.json"
            for data_type in DATA_FILES
        ]

        # Reset each JSON file while preserving its structure.
        for target_file in target_files:
            temporary_file = target_file.with_suffix(".json.tmp")

            try:
                with open(temporary_file, "w", encoding="utf-8") as file:
                    json.dump({}, file, indent=4)

                temporary_file.replace(target_file)

            finally:
                temporary_file.unlink(missing_ok=True)

    except (OSError, ValueError, UnicodeError):
        logger.exception("Failed to reset application data.")
        print_message("Failed to reset application data. Please check the application log.\n", "red")
        get_input()
        return

    print_message("Application data successfully reset.\n", "green")
    get_input()

    return
