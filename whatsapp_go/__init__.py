# -*- coding: utf-8 -*-

from . import setup
from . import controllers


# Auto-install required Python packages
setup.InstallPackages.install()

# Then load other modules
from . import models