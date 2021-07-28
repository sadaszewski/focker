import ruamel.yaml as yaml


def safe_load(stream):
    return yaml.YAML(typ='safe', pure=True).load(stream)
