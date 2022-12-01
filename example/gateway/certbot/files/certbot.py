import json
import subprocess


def main():
    with open('/certbot/data/metadata.json', 'r') as f:
        data = json.load(f)
    ips = data['ips'][0]
    domains = data['domains'][0]
    for ds in domains:
        cmd = [ '/usr/local/bin/certbot', 'certonly', '--webroot',
            '-w', '/certbot/webroot', '--server', 'https://127.0.11.1:14000/dir',
            '--email', 's.adaszewski@gmail.com', '--no-verify-ssl', '-n',
            '--agree-tos', '--expand' ]
        for d in ds:
            cmd.append('-d')
            cmd.append(d)
        ret = subprocess.run(cmd)
        if ret.returncode != 0:
            raise RuntimeError('Failed certbot certonly for:', ' '.join(ds))


if __name__ == '__main__':
    main()
