from shutil import rmtree
from os import remove
from pathlib import Path
from my_logger import logger


def main():
    BASE_DIR = Path("/home/UROP/shared_drive/Video_Folders/Trimmed_All_Videos")
    for folder in os.listdir(BASE_DIR):
        print(folder)
        folder_path: Path = BASE_DIR / folder
        assert folder_path.is_dir()

        to_delete_fp: Path = folder_path / "qa_label_template_v5.txt"
        if to_delete_fp.is_file():
            remove(to_delete_fp)
            logger.debug(f"Removed {to_delete_fp}")
        else:
            logger.warning(f"{to_delete_fp} not found")


if __name__ == "__main__":
    main()
