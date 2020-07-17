import os

KNOWN_EXTS = ('.mp4')

def template(folder, outfile='label.txt'):
    lst = os.listdir(folder)
    name, ext = os.path.splitext(outfile)
    suffix = 1
    while outfile in lst:
        outfile = f'{name}_{suffix}{ext}'
        suffix += 1

    with open(os.path.join(folder, outfile), 'w') as fp:
        for filename in lst:
            if filename.endswith(KNOWN_EXTS):
                fp.write(f'~~~~~~~~~~~~ {filename} ~~~~~~~~~~~~~\n'
                          '(VIEW) \n'
                          '(TIME) \n'
                          '\n\n'
                        )


if __name__ == '__main__':
    import sys
    if len(sys.argv) != 2:
        print('One and only one argrument is needed to locate you folder')
    else:
        template(sys.argv[1])
