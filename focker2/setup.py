from distutils.core import setup

setup(
    name='focker',
    version='2.00',
    author='Stanislaw Adaszewski',
    author_email='s.adaszewski@gmail.com',
    url='https://github.com/sadaszewski/focker',
    packages=['focker'],
    license='The GNU General Public License v3.0',
    description='Focker is a FreeBSD image orchestration tool in the vein of Docker.',
    long_description='Focker is a FreeBSD image orchestration tool in the vein of Docker.',
    scripts=['scripts/focker', 'scripts/focker-bsdinstall', 'scripts/focker-mirrorselect'],
    install_requires=[
        "tabulate",
        "jailconf",
        "pyyaml"
    ]
)
