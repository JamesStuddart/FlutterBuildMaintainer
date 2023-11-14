# Flutter Build Maintainer

This script automates the process of building a Flutter project with version and asset updates based on a configuration file.

## Prerequisites

Before using this script, ensure you have the following:

1. [Flutter](https://flutter.dev/docs/get-started/install) installed on your system.
2. A Flutter project with a `pubspec.yaml` file.
3. Python 3.x installed on your system.

## Python Libraries Installation

Before using the script, you need to install some Python libraries. Open a terminal and navigate to your project's root directory, then run the following command to install the required libraries:

```bash
pip install pyyaml
```

## Setup

1. Create a directory called `_build` in the root of your project if it doesn't already exist.

2. Clone or download the script to the `_build` folder

3. Update the a `config.json` file inside the `_build` directory to configure the script's behavior. 

## Configuration

Edit the `config.json` file in the `_build` directory to specify your build configuration. Here's an example configuration:

```json
{
  "version_build": {
    "version": "1.0.0",    // Current version
    "build": 1             // Current build number
  },
  "environments": {
    "dev": {
      "assets": {
      }
    },
    "test": {
      "assets": {
        "assets/config/dev/": "assets/config/test/"
      }
    },
    "prod": {
      "assets": {
        "assets/config/dev/": "assets/config/prod/"
      }
    }
  },
  "build_commands": {
    "ios": true,
    "android_bundle": true,
    "android_apk": true
  }
}
```

- `version_build`: Set the current version and build number.

- `environments`: Define asset replacements for different environments.

- `build_commands`: Enable or disable build commands for iOS and Android.

## Usage

To use the script, open a terminal and navigate to your project's root directory. Then, run the script with the following command:

```bash
python _build/build.py --environment dev
```

You can also use optional flags to increment the version:

- `--major`: Increment the major version.
- `--minor`: Increment the minor version.
- `--patch`: Increment the patch version.

Example:

```bash
python _build/build.py --major --environment dev
```

## Logs

The script logs build information to a `build_log.txt` file in the `_build` directory.

## Original 'pubspec.yaml' Backup

The script automatically creates a backup of the original `pubspec.yaml` file in case you need to restore it later. The backup is named `pubspec_backup.yaml`.

## Notes

- This script assumes that the `pubspec.yaml` file follows the standard YAML format for Flutter projects.

- Always back up your project before running the script.

- Make sure to configure your build commands in the `config.json` file to match your project's needs.

- The script resets asset changes after the build is complete to ensure the original `pubspec.yaml` is restored.
