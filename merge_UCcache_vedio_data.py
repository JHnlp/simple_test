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
        suffix = int("".join(suffix))
        new_names.append((temp, suffix))

    new_names = sorted(new_names, key=lambda x: x[-1], reverse=False)
    new_names = [x + str(y) for x, y in new_names]
    return new_names


def merge_data_with_list():
    for r, dirs, filelists in os.walk(filelists_path):
        # new_files = authorize_file_names_when_necessary(files)
        for fl in filelists:
            original_data_dir = ""
            target_name = os.path.splitext(fl)[0] + ".mp4"

            with codecs.open(os.path.join(r, fl), "r", "utf8")as f:
                for ln in f:
                    ln = ln.rstrip()
                    if ln.rstrip().startswith("/storage/"):
                        fpath = ln.replace("/storage/emulated/0/UCDownloads/VideoData/", par_data_dir)
                        if not original_data_dir:
                            original_data_dir = fpath[:fpath.rfind("/")]

                        if os.path.exists(fpath):
                            with codecs.open(os.path.join(root_dir, "Merged/with_filelist", target_name), "ab")as outf:
                                with codecs.open(fpath, "rb")as inf:
                                    data = inf.read()
                                    outf.write(data)
            if os.path.exists(original_data_dir):
                shutil.rmtree(original_data_dir)
            os.remove(os.path.join(r, fl))


def merge_data_by_name_list(root_dir=None, data_dir=None, filenames_dir=None):
    """
    when we have the *.m3u8 files
    """
    if not root_dir:
        root_dir = pathlib.Path(__file__).resolve().parent  # "F:/Zapya"
    else:
        root_dir = pathlib.Path(root_dir)
    if not data_dir:
        data_dir = root_dir.joinpath("Folder")
    else:
        data_dir = pathlib.Path(data_dir)
    if not filenames_dir:
        filenames_dir = root_dir.joinpath("Misc")
    else:
        filenames_dir = pathlib.Path(filenames_dir)

    cn = 0
    for fn in filenames_dir.glob("*.m3u8"):
        stem = fn.stem
        corresponding_data_dir = ""  # should be removed finally
        target_name = stem + ".mp4"
        print("\tprocessing: {}".format(target_name))
        cn += 1
        with fn.open("r", encoding="utf8")as f:
            for ln in f:
                ln = ln.rstrip()
                if ln.rstrip().startswith("/storage/"):
                    fpath = ln.replace("/storage/emulated/0/UCDownloads/VideoData/", str(data_dir))
                    if not corresponding_data_dir:
                        corresponding_data_dir = fpath[:fpath.rfind("/")]

                    fpath = pathlib.Path(fpath)
                    if fpath.exists():
                        with root_dir.joinpath("Merged/with_filelist", target_name).open("ab")as outf:
                            with fpath.open("rb")as inf:
                                data = inf.read()
                                outf.write(data)
            # if os.path.exists(corresponding_data_dir):
            #     shutil.rmtree(corresponding_data_dir)
            # fn.unlink()
    print("Already processed {} files".format(cn))


def merge_data_without_list():
    for r, dirs, filelists in os.walk(par_data_dir):
        for dd in dirs:
            target_name = os.path.splitext(dd)[0] + ".mp4"

            for _, dirnames, filenames in os.walk(os.path.join(r, dd)):
                if filenames:
                    try:
                        authorized_file_names = authorize_filenames(filenames)
                        with codecs.open(os.path.join(root_dir, "Merged/without_filelist", target_name),
                                         "ab")as outf:
                            for fn in authorized_file_names:
                                with codecs.open(os.path.join(r, dd, fn), "rb")as inf:
                                    data = inf.read()
                                    outf.write(data)
                        if os.path.exists(os.path.join(r, dd)):
                            shutil.rmtree(os.path.join(r, dd))

                    except:
                        print(_, filenames)


def merge_data_by_content(root_dir=None, data_dir=None):
    """
    when we don't have the *.m3u8 files
    """
    if not root_dir:
        root_dir = pathlib.Path(__file__).resolve().parent  # "F:/Zapya"
    else:
        root_dir = pathlib.Path(root_dir)
    if not data_dir:
        data_dir = root_dir.joinpath("Folder")
    else:
        data_dir = pathlib.Path(data_dir)

    cn = 0
    for _dir in data_dir.iterdir():
        target_name = _dir.stem + ".mp4"
        files = []
        print("\tprocessing: {}".format(target_name))
        cn += 1
        for fn in _dir.iterdir():
            if fn.suffix.lower() == ".mp4" or not fn.suffix:
                files.append(str(fn.resolve()))
        try:
            authorized_file_names = authorize_filenames(files)
            with root_dir.joinpath("Merged/without_filelist", target_name).open("ab")as outf:
                for fn in authorized_file_names:
                    with codecs.open(fn, "rb")as inf:
                        data = inf.read()
                        outf.write(data)
            # if _dir.exists():
            #     shutil.rmtree(_dir)
        except:
            print("Cannot process file: {}".format(_dir))
    print("Finally processed {} files.".format(cn))


if __name__ == "__main__":
    print("Merging data, please wait for seconds...")
    # merge_data_with_list()
    # merge_data_without_list()

    # merge_data_by_name_list(root_dir="F:/Zapya")
    merge_data_by_content(root_dir="F:/Zapya")
