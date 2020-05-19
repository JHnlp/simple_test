import os
import shutil
import codecs
import pathlib

# os.remove()
# os.removedirs()

root_dir = pathlib.Path(__file__).resolve().parent  # "F:/Zapya"
filelists_path = os.path.join(root_dir, "Misc")
par_data_dir = os.path.join(root_dir, "Folder")


def authorize_filenames(filenames):
    new_names = []
    for fn in filenames:
        temp = fn
        suffix = []
        while (temp[-1].isdigit()):
            suffix.append(temp[-1])
            temp = temp[:-1]
        suffix = suffix[::-1]
        try:
            suffix = int("".join(suffix))
            new_names.append((temp, suffix))
        except:
            print("ignore file: {}".format(fn))

    new_names = sorted(new_names, key=lambda x: x[-1], reverse=False)
    new_names = [x + str(y) for x, y in new_names]
    return new_names


def trunc_name(name):
    punc = ':?/\\"\'{},<>|;!@#$%^&*-=+()[]~`'
    for ch in punc:
        name = name.replace(ch, "_")
    return name


def merge_data_by_name_list(root_dir=None, data_folder_name=None, filelist_folder_name=None):
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
    if not filelist_folder_name:
        filelist_folder = root_dir.joinpath("Misc")
    else:
        filelist_folder = root_dir.joinpath(filelist_folder_name)

    cn = 0
    for fn in filelist_folder.glob("*.m3u8"):
        stem = fn.stem
        stem = stem[:25]
        stem = trunc_name(stem)
        corresponding_data_dir = ""  # should be removed finally
        target_name = stem + ".mp4"
        print("\tprocessing: {}".format(target_name))
        cn += 1
        with fn.open("r", encoding="utf8")as f:
            for ln in f:
                ln = ln.rstrip()
                if ln.rstrip().startswith("/storage/"):
                    fpath = ln.replace("/storage/emulated/0/UCDownloads/VideoData/", str(data_folder))
                    if not corresponding_data_dir:
                        corresponding_data_dir = fpath[:fpath.rfind("/")]

                    fpath = pathlib.Path(fpath)
                    if fpath.exists():
                        with root_dir.joinpath("Merged/with_filelist", target_name).open("ab")as outf:
                            with fpath.open("rb")as inf:
                                data = inf.read()
                                outf.write(data)
            if os.path.exists(corresponding_data_dir):
                shutil.rmtree(corresponding_data_dir)
        fn.unlink()
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
        target_name = target_name[:25]
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
    merge_data_by_name_list(root_dir="/home/sunsunbest/Windows10_1t_J/Zapya",
                            data_folder_name="Folder",
                            filelist_folder_name="Misc")
    merge_data_by_content(root_dir="/home/sunsunbest/Windows10_1t_J/Zapya",
                          data_folder_name="Folder")
