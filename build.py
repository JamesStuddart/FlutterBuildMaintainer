import os
import json
import argparse
import datetime
import yaml
import shutil
import sys

# Define the paths and filenames
pubspec_path = "../pubspec.yaml"
config_path = "../_build/config.json"
log_file = "../_build/build_log.txt"
pubspec_backup_path = "../_build/pubspec_backup.yaml"

# Function to read the configuration from config.json
def read_config():
    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            return json.load(f)
    return {}

# Function to write log messages to a log file
def write_log(message):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_message = f"{timestamp} - {message}\n"

    # Write to the log file
    with open(log_file, "a") as f:
        f.write(log_message)

    # Write to the console (stdout)
    sys.stdout.write(log_message)
    sys.stdout.flush()  # Flush the buffer to ensure immediate display

# Function to read asset mappings for a specific environment from the configuration
def read_asset_mapping(config, environment):
    return config.get("environments", {}).get(environment, {}).get("assets", {})

# Function to increment version number by one
def increment_version(version, segment):
    version_components = version.split('.')
    if segment == 'major':
        version_components[0] = str(int(version_components[0]) + 1)
        version_components[1] = '0'
        version_components[2] = '0'
    elif segment == 'minor':
        version_components[1] = str(int(version_components[1]) + 1)
        version_components[2] = '0'
    elif segment == 'patch':
        version_components[2] = str(int(version_components[2]) + 1)
    return '.'.join(version_components)

# Function to perform version update
def update_version(pubspec_contents, current_version, build_number, major=False, minor=False, patch=False):
    if major:
        new_version = increment_version(current_version, 'major')
    elif minor:
        new_version = increment_version(current_version, 'minor')
    elif patch:
        new_version = increment_version(current_version, 'patch')
    else:
        new_version = current_version

    # Update the version within pubspec.yaml
    pubspec_data = yaml.safe_load(pubspec_contents)
    pubspec_data['version'] = f'{new_version}+{build_number}'
    updated_pubspec_contents = yaml.dump(pubspec_data, default_flow_style=False)

    return new_version, updated_pubspec_contents

# Function to perform asset replacement
def replace_assets(asset_mapping, pubspec_contents):
    # Update assets in the 'pubspec.yaml' file based on the mapping
    if asset_mapping:
        for old_asset, new_asset in asset_mapping.items():
            pubspec_contents = pubspec_contents.replace(old_asset, new_asset)

    return pubspec_contents

# Function to build the Flutter project
def build_project(config, environment, build_number):
    try:
        if config:
            build_commands = config.get("build_commands", {})
            if build_commands.get("ios"):
                os.system("flutter build ipa --release")
                write_log("iOS build completed.")

            if build_commands.get("android_bundle"):
                os.system("flutter build appbundle")
                write_log("Android App Bundle build completed.")

            if build_commands.get("android_apk"):
                os.system("flutter build apk")
                write_log("Android APK build completed.")

            # Update the build number in config.json
            config["version_build"]["build"] = build_number
            config["version_build"]["version"] = new_version
            with open(config_path, "w") as f:
                json.dump(config, f, indent=4)
            write_log(f"Build number updated to {build_number}")

        else:
            write_log("No configuration found in config.json. Nothing to build.")

    except Exception as e:
        write_log(f"Error occurred during build: {str(e)}")

    finally:
        # Restore the original 'pubspec.yaml' after the build
        restore_original_pubspec()

# Function to restore the original 'pubspec.yaml' file
def restore_original_pubspec():
    if os.path.exists(pubspec_backup_path):
        shutil.copy(pubspec_backup_path, pubspec_path)
        write_log("Original 'pubspec.yaml' restored after build.")
        os.remove(pubspec_backup_path)
        write_log(f"Backup 'pubspec.yaml' has been removed.")

# Parse command-line arguments
parser = argparse.ArgumentParser(description="Build a Flutter project based on configuration")
parser.add_argument("--major", action="store_true", help="Increment the major version by one")
parser.add_argument("--minor", action="store_true", help="Increment the minor version by one")
parser.add_argument("--patch", action="store_true", help="Increment the patch version by one")
parser.add_argument("--environment", required=True, help="Specify the target environment")
args = parser.parse_args()

# Change working directory to the root directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Ensure the _build directory exists
if not os.path.exists("../_build"):
    os.makedirs("../_build")

# Create a backup of the original 'pubspec.yaml' if not already present
if not os.path.exists(pubspec_backup_path):
    shutil.copy(pubspec_path, pubspec_backup_path)
    write_log("Original 'pubspec.yaml' backed up.")

# Read the configuration from config.json
config = read_config()

# Read the current version from the configuration
current_version = config.get("version_build", {}).get("version", "1.0.0")

# Read the build number from the configuration
build_number = config.get("version_build", {}).get("build", 1)
build_number = build_number + 1

# Read the pubspec.yaml contents
with open(pubspec_path, "r") as f:
    pubspec_contents = f.read()

# Update the version numbers and pubspec contents based on command-line arguments
new_version, updated_pubspec_contents = update_version(pubspec_contents, current_version, build_number, args.major, args.minor, args.patch)

# Read asset mapping for the specified environment
environment = args.environment
asset_mapping = read_asset_mapping(config, environment)

# Replace assets in the 'pubspec.yaml' file based on the mapping
updated_pubspec_contents = replace_assets(asset_mapping, updated_pubspec_contents)

# Write the updated pubspec.yaml contents back to the file
with open(pubspec_path, "w") as f:
    f.write(updated_pubspec_contents)

# Build the Flutter project based on user preferences and configuration
build_project(config, environment, build_number)

# Log the build information
log_message = f"Version: {new_version}, Build: {build_number}, Target Environment: {environment}"
write_log(log_message)
