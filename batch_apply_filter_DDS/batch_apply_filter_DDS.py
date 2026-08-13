import os
import shutil
import logging
import subprocess
import struct
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from tkinter import filedialog
from itertools import repeat

import configs

logger = logging.getLogger()

# --- CONSTANTS ---

MAX_WORKERS = 10

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / 'out'
TEMP_DIR = BASE_DIR / 'TEMP'

# --- GLOBALS ---
inputdir = None
sbsrender = None
texconv = None
done = False

def apply_filter():

    try:
        # --- SETUP ---

        # grab application paths from ini, if it exists
        if not configs.ini_file.exists():
            configs.setup_config()

        # get exe paths from the ini
        # load_config() contains setup_config() if the paths are incorrect
        global sbsrender
        global texconv
        sbsrender, texconv = configs.load_config()

        # select sbsar file

        try:
            sbsar = filedialog.askopenfile(filetypes=[("SBSAR Files", "*.sbsar")], 
                                    title="Please select your SBSAR file to apply.")
        except FileNotFoundError:
            raise SystemExit("[ERROR] File does not exist!")
        if not sbsar:
            raise SystemExit("[ERROR] User canceled.")

        if not sbsar.name.endswith(".sbsar"):
            raise SystemExit("[ERROR] SBSAR does not exist or otherwise cannot be used.")

        # select folder to process
        global input_dir
        input_dir = filedialog.askdirectory(title="Please find the folder of DDS images to process.")
        if not input_dir:
            raise SystemExit("[ERROR] User canceled.")

        files = [f for f in os.listdir(input_dir) if f.endswith('.dds')]

        if len(files) == 0:
            raise SystemExit("[ERROR] No .dds files found.")
        
        logger.info(f"[INFO] Found {len(files)} DDS files.")

        # set up working directories
        try:
            OUTPUT_DIR.mkdir(exist_ok=True)
            TEMP_DIR.mkdir(exist_ok=True)
        except OSError:
            raise SystemExit("[ERROR] Failed to create directories.")

        # --- CONVERT TO TGA ---
        logger.info("[INFO] Converting files to TGA...")

        tga_args = [
            str(texconv),
            '-ft',
            'tga',
            '-o',
            TEMP_DIR,
            f"{input_dir}" + "\\*.dds"
        ]

        try:
            subprocess.run(tga_args, check=True)
        except subprocess.CalledProcessError:
            raise SystemExit("[ERROR] Failed to convert files to .tga.")

        # --- MULTITHREADING WIZARDRY ---
        
        logger.info("[INFO] Applying filter to files...")

        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            # executor.map applies the function to the list of files across the threads
            executor.map(process_sbsar, repeat(os.path.abspath(sbsar.name)), files, repeat(input_dir), repeat(sbsrender))

        # --- CONVERT TO BC7 ---
        logger.info('[INFO] Converting files to BC7...')

        bc7_args = [
            str(texconv),
            '-f',
            'BC7_UNORM',
            '-gpu',
            '1',
            '-bc',
            'q',
            '-o',
            str(OUTPUT_DIR),
            f"{str(TEMP_DIR)}" + "\\*.tga",
        ]

        try:
            subprocess.run(bc7_args, check=True)
        except subprocess.CalledProcessError:
            raise SystemExit("[ERROR] Failed to convert files back to .dds.")
        return 0
    finally:
        cleanup()

# --- HELPER FUNCTIONS ---

def process_sbsar(sbsar, file, input_dir, sbsrender):

    if input_dir is not None and sbsrender is not None:

        file_name = Path(file).name
        src_tga = (Path(TEMP_DIR) / file_name.stem + ".tga").absolute()

        width, height = get_dimensions_tga(str(src_tga))

        args = [
                str(sbsrender),
                'render',
                '--input', str(sbsar),
                '--set-entry', f'input@{src_tga}',
                '--output-path', str(TEMP_DIR),
                '--output-format', 'tga',
                '--set-value', f'$outputsize@{width},{height}',
                '--output-name', file_name.split('.')[0],
            ]
        try:
            subprocess.run(args, check=True, capture_output=True, text=True, shell=False)

        except subprocess.CalledProcessError as e:
            logger.error(f"[ERROR] Unable to process file {file}.")
            logger.error(e.stderr)
            return 1
        
        except TypeError:
            logger.error(f"[ERROR] File type incorrect for {file}")
            return 1
            
    else:
        logger.error('[ERROR] Input directory not found!' )
        return 1

def get_dimensions_tga(file):

    if not file.strip().lower().endswith(".tga"):
        raise ValueError(f"{file} is not a TGA file.")

    if not Path(file).exists():
        raise FileNotFoundError(f"{file} does not exist.")
    
    with open(file, 'rb') as f:
        # go to the 12th byte in the file header, which is where dimension data is stored
        f.seek(12)

        header_data = f.read(4)

        # '<HH' unpacks two little-endian, 16-bit unsigned integers
        # struct.unpack() converts raw binary to readable data, in this case, integers.
        # in '<HH', the '<' tells the program the file is in little-endian format
        # the 'HH' tells the program to interpret the bytes two at a time 
        width, height = struct.unpack('<HH', header_data)
        return width, height

def cleanup():
    try:
        shutil.rmtree(TEMP_DIR)
    except OSError:
        raise SystemExit("[ERROR] Unable to remove temporary directory.")

def main():
    configs.setup_config()
    apply_filter()

if __name__ == "__main__":
    main()