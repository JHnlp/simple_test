import os
import shutil
import codecs
import pathlib
from Crypto.Cipher import AES

# os.remove()
# os.removedirs()
# os.system('mkdir merge')

ROOT_DIR = pathlib.Path(__file__).resolve().parent  # "F:/Zapya"
FILELISTS_PATH = os.path.join(ROOT_DIR, "Misc")
PARENT_DATA_DIR = os.path.join(ROOT_DIR, "Folder")
# FILENAME_BLACKLIST = ["kye0", ".index.m3u8", ".local.index.m3u8", "k0"]
FILENAME_BLACKLIST = [".index.m3u8", ".local.index.m3u8"]


def authorize_filenames(filenames):
    new_names = []
    for absolute_fn in filenames:
        temp = absolute_fn
        fn = absolute_fn[absolute_fn.rfind("/"):]
        if fn in FILENAME_BLACKLIST:  # filter some invalid files
            continue

        suffix = []
        while (temp[-1].isdigit()):
            suffix.append(temp[-1])
            temp = temp[:-1]
        suffix = suffix[::-1]
        try:
            suffix = int("".join(suffix))
            new_names.append((temp, suffix))
        except:
            print("ignore file: {}".format(absolute_fn))

    new_names = sorted(new_names, key=lambda x: x[-1], reverse=False)
    new_names = [x + str(y) for x, y in new_names]
    return new_names


def trunc_name(name):
    punc = ':?/\\"\'{},<>|;!@#$%^&*-=+()[]~`'
    for ch in punc:
        name = name.replace(ch, "_")
    return name


def parse_m3u8(dir_prefix, m3u8_uri):
    m3u8_uri = pathlib.Path(m3u8_uri)
    with m3u8_uri.open("r", encoding="utf8")as f:
        content = f.read()
    list_content = content.split('\n')
    player_files = []
    encript_key_file = None
    for index, line in enumerate(list_content):
        if "#EXT-X-KEY" in line:
            method_pos = line.find("METHOD")
            comma_pos = line.find(",")
            method = line[method_pos:comma_pos].split('=')[1]  # get encription method
            print("\t....Decode Encription Method：", method)
            uri_pos = line.find("URI")
            quotation_mark_pos = line.rfind('"')
            key_uri = line[uri_pos:quotation_mark_pos].split('"')[1]
            encript_key_file = key_uri.replace("/storage/emulated/0/UCDownloads/VideoData", str(dir_prefix))
            # encript_key_file = pathlib.Path(encript_key_file)
        if '#EXTINF' in line:
            href = list_content[index + 1]
            href = href.replace("/storage/emulated/0/UCDownloads/VideoData", str(dir_prefix))
            # href = pathlib.Path(href)
            player_files.append(href)

    return player_files, encript_key_file


def merge_data_by_name_list(root_dir=None, data_folder_name=None, m3u8_folder_name=None):
    """
    when we have the *.m3u8 files
    """
    if not root_dir:
        root_dir = pathlib.Path(__file__).resolve().parent  # "F:/Zapya"
    else:
        root_dir = pathlib.Path(root_dir)
    if not data_folder_name:
        data_folder = root_dir.joinpath("Folder")
    else:
        data_folder = root_dir.joinpath(data_folder_name)
    if not m3u8_folder_name:
        m3u8_folder = root_dir.joinpath("Misc")
    else:
        m3u8_folder = root_dir.joinpath(m3u8_folder_name)

    cn = 0
    for fm3u8 in m3u8_folder.glob("*.m3u8"):
        stem = fm3u8.stem
        stem = stem[:80]
        stem = trunc_name(stem)
        corresponding_data_dir = ""  # should be removed finally
        target_name = stem + ".mp4"
        print("\tprocessing: {}".format(target_name))
        cn += 1
        with fm3u8.open("r", encoding="utf8")as f:
            cryptor = None
            player_files, encript_file = parse_m3u8(data_folder, fm3u8)
            if encript_file is not None:
                encript_file = pathlib.Path(encript_file)
                if encript_file.exists():
                    with encript_file.open("rb") as enf:
                        encript_key = enf.read()
                        cryptor = AES.new(encript_key, AES.MODE_CBC, encript_key)
            for fpath in player_files:
                if not corresponding_data_dir:
                    corresponding_data_dir = fpath[:fpath.rfind("/")]
                fp = pathlib.Path(fpath)
                if fp.exists():
                    with root_dir.joinpath("Merged/with_filelist", target_name).open("ab")as outf:
                        with fp.open("rb")as inf:
                            data = inf.read()
                            if cryptor:
                                outf.write(cryptor.decrypt(data))
                            else:
                                outf.write(data)

            if os.path.exists(corresponding_data_dir):
                shutil.rmtree(corresponding_data_dir)
        fm3u8.unlink()
    print("Already processed {} files".format(cn))


def merge_data_by_content(root_dir=None, data_folder_name=None):
    """
    when we don't have the *.m3u8 files
    """
    if not root_dir:
        root_dir = pathlib.Path(__file__).resolve().parent  # "F:/Zapya"
    else:
        root_dir = pathlib.Path(root_dir)
    if not data_folder_name:
        data_folder = root_dir.joinpath("Folder")
    else:
        data_folder = root_dir.joinpath(data_folder_name)

    cn = 0
    for _dir in data_folder.iterdir():
        target_name = _dir.stem
        target_name = target_name[:80]
        target_name = trunc_name(target_name)
        target_name = target_name + ".mp4"
        files = []
        print("\tprocessing: {}".format(target_name))
        cn += 1
        for fn in _dir.iterdir():
            if fn.suffix.lower() == ".mp4" or not fn.suffix:
                files.append(str(fn.resolve()))
        try:
            authorized_file_names = authorize_filenames(files)
            if authorized_file_names:
                with root_dir.joinpath("Merged/without_filelist", target_name).open("ab")as outf:
                    for fn in authorized_file_names:
                        with codecs.open(fn, "rb")as inf:
                            data = inf.read()
                            outf.write(data)
            shutil.rmtree(_dir, ignore_errors=True)
        except:
            print("Cannot process file: {}".format(_dir))
    print("Finally processed {} files.".format(cn))


if __name__ == "__main__":
    print("Merging data, please wait for seconds...")
    merge_data_by_name_list(root_dir="J:/Zapya",
                            data_folder_name="Folder",
                            m3u8_folder_name="Misc")
    merge_data_by_content(root_dir="J:/Zapya",
                          data_folder_name="Folder")
