import tarfile

class Repo:
    def __init__(self, data):
        self.data = {}
        if isinstance(data, dict):
            self.data = data
        elif isinstance(data, tarfile.TarFile):
            for member in data.getmembers():
                if member.name.endswith("/desc"):
                    raw_desc = data.extractfile(member).read()
                    dict_desc = package_desc2dict(raw_desc)
                    self.data = {**self.data, **dict_desc}


    def __iter__(self):
        for key in self.data.keys():
            yield key

    def __getitem__(self, key):
        return self.data[key]

    def __eq__(self, other):
        return self.data == other.data


def package_desc2dict(desc):
    # Bytes to String
    desc = desc.decode()

    # Strip lines
    desc = [line.strip(" ") for line in desc.split("\n")]

    # Remove blank lines
    desc = [line for line in desc if line]

    parsed = {}
    name = ""
    items = []
    for line in desc:
        if line.startswith("%") and line.endswith("%"):
            if name:
                parsed[name] = items

            name = line.strip("%").lower()
            items = []
        else:
            items.append(line)
    parsed[name] = items

    # remove lists
    delist = {}
    for key, value in parsed.items():
        delist[key] = "\n".join(value).strip("\n")

    package_name = delist.pop("name")
    return {package_name: delist}
