from pathlib import Path
import configparser
import logging
from tkinter import filedialog

BASE_DIR = Path(__file__).resolve().parent
DEF_SBSRENDER = Path('C:/Program Files/Adobe/Adobe Substance 3D Designer/sbsrender.exe')
DEF_TEXCONV = BASE_DIR / 'util' / 'texconv.exe'

logger = logging.getLogger()
cfgparser = configparser.ConfigParser()
ini_file = BASE_DIR / 'config.ini'

# initialize variables to default paths
sPathSBSRender = str(DEF_SBSRENDER)
sPathTexconv = str(DEF_TEXCONV)


def setup_config(cfgparser=cfgparser, logger=logger):
    
    # declare globals
    global sPathSBSRender
    global sPathTexconv

    # try to get paths from config
    # if this fails, add find the paths with filedialog and add them to the config.
    try:
        # read the ini
        cfgparser.read(ini_file, encoding="utf-8")

        # get the SBSRender path entry
        sPathSBSRender = cfgparser.get('PATHS', 'sPathSBSRender')

        # throw an error if the existing entry is not a file
        if not sPathSBSRender or not Path(sPathSBSRender).is_file():
            raise FileNotFoundError('[ERROR] Please select the SBSRender executable.')
        
    except (FileNotFoundError, configparser.NoSectionError, configparser.NoOptionError):

        if not DEF_SBSRENDER.is_file():
            
            while True:

                # user finds the SBSRender exe
                new_dir = filedialog.askopenfilename(filetypes=[("Executables", "*.exe")], title="Please find sbsrender.exe")
                if not new_dir: raise SystemExit("[ERROR] Operation canceled by user")
                if new_dir.lower().endswith("sbsrender.exe"):
                    break
                else:
                    logger.warning('[WARNING] Incorrect program selected. Please select "sbsrender.exe"')
            
            sPathSBSRender = new_dir
        else:
            sPathSBSRender = str(DEF_SBSRENDER)

    try:
        sPathTexconv = cfgparser.get('PATHS', 'sPathTexconv')

        # throw an error if the existing entry is not a file
        if not sPathTexconv or not Path(sPathTexconv).is_file():
            raise FileNotFoundError('[ERROR] Please select the Texconv executable.')
    
    except (FileNotFoundError, configparser.NoSectionError, configparser.NoOptionError):
        if not DEF_TEXCONV.is_file():
            while True:
                # user finds the Texconv exe
                new_dir = filedialog.askopenfilename(filetypes=[("Executables", "*.exe")], title="Please find texconv.exe")
                if not new_dir: raise SystemExit("[ERROR] Operation canceled by user")
                if new_dir.lower().endswith("texconv.exe"):
                    break
                else:
                    logger.warning('[WARNING] Incorrect program selected. Please select "texconv.exe"')
            sPathTexconv = new_dir
        else:
            sPathTexconv = str(DEF_TEXCONV)

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
        cfgparser.read(ini_file, encoding="utf-8")
        sPathSBSRender = cfgparser.get("PATHS", 'sPathSBSRender')
        sPathTexconv = cfgparser.get("PATHS", 'sPathTexconv')

        if not Path(sPathSBSRender).is_file() or not Path(sPathTexconv).is_file():
            raise FileNotFoundError
    except (FileNotFoundError, configparser.NoSectionError, configparser.NoOptionError): 
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