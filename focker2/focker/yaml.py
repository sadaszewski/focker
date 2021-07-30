import ruamel.yaml as yaml


def safe_load(stream):
    return yaml.YAML(typ='safe', pure=True).load(stream)


def safe_dump(obj, stream):
    return yaml.YAML(typ='safe', pure=True).dump(obj, stream)
