import glob
import yaml
import json


def main():
    res_ips = []
    res_domains = []
    for fname in glob.glob('../**/focker-compose.yml'):
        print(fname)
        with open(fname, 'r') as f:
            spec = yaml.safe_load(f)
        if 'jails' not in spec:
            continue
        for j in spec['jails'].values():
            if 'ip4.addr' not in j:
                continue
            if 'meta' not in j:
                continue
            if 'domains' not in j['meta']:
                continue
            if not j['meta']['domains']:
                continue
            domains = j['meta']['domains']
            if not isinstance(domains, list):
                domains = [ domains ]
            res_ips.append(j['ip4.addr'])
            res_domains.append(domains)
    res = { 'directory_name': 'nginx_conf',
        'ips': [ res_ips ],
        'domains': [ res_domains ] }
    with open('./files/cookiecutter.json', 'w') as f:
        json.dump(res, f)


if __name__ == '__main__':
    main()
