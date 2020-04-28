# Created by: s.adaszewski@gmail.com
# $FreeBSD$

PORTNAME=	focker
PORTVERSION=	0.92
CATEGORIES=	sysutils python
MASTER_SITES=	https://github.com/sadaszewski/focker/archive/
DISTNAME=	${PORTVERSION}
WRKSRC=         ${WRKDIR}/${PORTNAME}-${PORTVERSION}

MAINTAINER=	s.adaszewski@gmail.com
COMMENT=	FreeBSD jail/image orchestration tool in the vein of Docker

LICENSE=	GPLv3

USES=		python:3.5+
USE_PYTHON=	distutils autoplist

RUN_DEPENDS=    ${PYTHON_PKGNAMEPREFIX}yaml>0:devel/py-yaml@${PY_FLAVOR} \
  ${PYTHON_PKGNAMEPREFIX}tabulate>0:devel/py-tabulate@${PY_FLAVOR} \
  ${PYTHON_PKGNAMEPREFIX}jailconf>0:devel/py-jailconf@${PY_FLAVOR}

NO_ARCH=			yes

.include <bsd.port.mk>
