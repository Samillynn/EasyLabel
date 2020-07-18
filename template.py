import os
from pathlib import Path


def template(folder_path: str, outfile="label.txt"):
    folder_path = Path(folder_path)
    if not folder_path.is_dir():
        raise Exception("\n\nFolder: {folder_path} does not exist.\n")

    lst = sorted(os.listdir(folder_path))
    name, ext = os.path.splitext(outfile)
    suffix = 1
    while outfile in lst:
        outfile = f"{name}_{suffix}{ext}"
        suffix += 1

    with open(os.path.join(folder_path, outfile), "w") as f:
        for filename in lst:
            if filename.endswith(".mp4"):
                f.write(
                    f"~~~~~~~~~~~~ {filename} ~~~~~~~~~~~~~\n"
                    "(VIEW) \n"
                    "(TIME) \n"
                    "\n\n"
                )


if __name__ == "__main__":
    import sys

    if len(sys.argv) == 1:
        folder_path = "REPLACE ME"
        template(folder_path)
    elif len(sys.argv) == 2:
        template(sys.argv[1])
    else:
        print("Only one argrument is needed to locate you folder.")
