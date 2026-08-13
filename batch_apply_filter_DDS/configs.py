from pathlib import Path
import configparser
import logging
from tkinter import filedialog

logger = logging.getLogger()
cfgparser = configparser.ConfigParser()
ini_file = Path('configs.ini')

# initialize variables
sPathSBSRender: str | None = None
sPathTexconv: str | None = None

DEF_TEXCONV = Path('util') / 'texconv.exe'


def setup_config(cfgparser=cfgparser, logger=logger):
    
    # declare globals
    global sPathSBSRender
    global sPathTexconv


    # try to get paths from config
    # if this fails, add find the paths with filedialog and add them to the config.
    try:
        cfgparser.read('configs.ini')
        sPathSBSRender = cfgparser.get('PATHS', 'sPathSBSRender')
    except (FileNotFoundError, configparser.NoSectionError, configparser.NoOptionError):
        while True:
            new_dir = filedialog.askopenfilename(filetypes=[("Executables", "*.exe")], title="Please find sbsrender.exe")
            if not new_dir: raise SystemExit("[ERROR] Operation canceled by user")
            if new_dir.endswith("sbsrender.exe"):
                break
            else:
                logger.warning('[WARNING] Incorrect program selected. Please select "sbsrender.exe"')
        
        sPathSBSRender = new_dir

    try:
        sPathTexconv = cfgparser.get('PATHS', 'sPathTexconv')
    except configparser.NoSectionError:
        if not DEF_TEXCONV.is_file():
            while True:
                new_dir = filedialog.askopenfilename(filetypes=[("Executables", "*.exe")], title="Please find texconv.exe")
                if not new_dir: raise SystemExit("[ERROR] Operation canceled by user")
                if new_dir.endswith("texconv.exe"):
                    break
                else:
                    logger.warning('[WARNING] Incorrect program selected. Please select "texconv.exe"')
        else:
            new_dir = DEF_TEXCONV.resolve()
        sPathTexconv = new_dir

    # sync with ini file
    sync_config()

    logger.info('[INFO] Config setup is complete.')
    return [sPathSBSRender, sPathTexconv]

def sync_config():
    write_to_config('PATHS', 'sPathSBSRender', str(sPathSBSRender))
    write_to_config('PATHS', 'sPathTexconv', str(sPathTexconv))

# pull the values from the config
def load_config(cfgparser=cfgparser, ini_file=ini_file):
    # declare globals
    global sPathSBSRender
    global sPathTexconv

    # check if ini exists first
    if not ini_file.exists():
        # re-runs setup, unless we got here from setup
        # in which case, somethings wrong! cancel the operation.
        return setup_config()
    
    # load values from ini file
    try:
        sPathSBSRender = cfgparser.get("PATHS", sPathSBSRender)
        sPathTexconv = cfgparser.get("PATHS", sPathTexconv)
    except (configparser.NoSectionError, configparser.NoOptionError): 
        logger.warning("[WARNING] Failed to load config. Rebuilding...")
        return setup_config()

    return [sPathSBSRender, sPathTexconv]

def write_to_config(section: str, key: str, value: str, cfgparser=cfgparser, ini_file=ini_file):
    # Save the in-memory config values
    if not cfgparser.has_section(section):
        cfgparser.add_section(section)

    # set the [key] in [section] to [value]
    cfgparser[section][key] = value

    # write the new values to the config file
    with open(ini_file, 'w', encoding="utf-8") as ini:
        cfgparser.write(ini)


def main():
    setup_config()

if __name__ == "__main__":
    main()