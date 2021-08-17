# Created by: s.adaszewski@gmail.com
# $FreeBSD$

PORTNAME=	jailconf
PORTVERSION=	0.2.1
CATEGORIES=	devel python
MASTER_SITES=	https://github.com/leforestier/jailconf/archive/
PKGNAMEPREFIX=  ${PYTHON_PKGNAMEPREFIX}
DISTNAME=	v${PORTVERSION}
WRKSRC=         ${WRKDIR}/${PORTNAME}-${PORTVERSION}

MAINTAINER=	s.adaszewski@gmail.com
COMMENT=	Parse and edit your FreeBSD jail.conf (jails configuration file) with python.

LICENSE=	BSD

USES=		python
USE_PYTHON=	distutils autoplist

RUN_DEPENDS=    ${PYTHON_PKGNAMEPREFIX}ply>0:devel/py-ply@${PY_FLAVOR}
NO_ARCH=        yes

.include <bsd.port.mk>

