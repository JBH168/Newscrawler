import os


def save_webpage(response):
    filename = get_filename(response)

    with open(get_abs_file_path(filename), 'wb') as f:
        f.write(response.body)


def get_filename(response):
    filename = response.url.split("/")[-1]

    if not filename:  # empty string
        filename = response.url.split("/")[-2]

    if not filename.endswith(".html"):
        filename = filename + ".html"

    return filename


def get_abs_file_path(filename):
    # for the following three lines of code, see:
    # http://stackoverflow.com/questions/7165749/open-file-in-a-relative-location-in-python
    #
    # may be replaced with a file path given in a json file
    script_dir = os.path.dirname(__file__)  # absolute dir the script is in
    rel_path = "../../data/" + filename
    abs_file_path = os.path.join(script_dir, rel_path)

    # ensure the directory actually exists, if it doesn't, create it
    abs_dir = os.path.dirname(abs_file_path)
    if not os.path.exists(abs_dir):
        os.makedirs(abs_dir)

    return abs_file_path
