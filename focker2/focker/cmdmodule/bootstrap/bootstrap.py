from ...plugin import Plugin
from tabulate import tabulate
from ...core.zfs import zfs_init
from .misc import cmd_bootstrap_filesystem, \
    cmd_bootstrap_empty, \
    cmd_bootstrap_finalize
from .pfrule import cmd_bootstrap_pfrule
from .iface import cmd_bootstrap_interface


class BootstrapPlugin(Plugin):
    @staticmethod
    def provide_parsers():
        return dict(
            bootstrap=dict(
                aliases=['boot', 'bs', 'b'],
                subparsers=dict(
                    filesystem=dict(
                        aliases=['fs'],
                        func=cmd_bootstrap_filesystem
                    ),
                    interface=dict(
                        aliases=['iface', 'if'],
                        func=cmd_bootstrap_interface,
                        interface=dict(
                            aliases=['i'],
                            type=str,
                            default='lo1'
                        ),
                        rename_interface=dict(
                            aliases=['r'],
                            type=str
                        )
                    ),
                    pfrule=dict(
                        aliases=['pf'],
                        func=cmd_bootstrap_pfrule,
                        external_interface=dict(
                            aliases=['eif'],
                            type=str
                        ),
                        jail_interface=dict(
                            aliases=['jif'],
                            type=str,
                            default='lo1'
                        )
                    ),
                    empty=dict(
                        aliases=['e'],
                        func=cmd_bootstrap_empty,
                        tags=dict(
                            aliases=['t'],
                            type=str,
                            nargs='+'
                        )
                    ),
                    finalize=dict(
                        aliases=['f'],
                        func=cmd_bootstrap_finalize,
                        reference=dict(
                            positional=True,
                            type=str
                        )
                    )
                )
            )
        )
