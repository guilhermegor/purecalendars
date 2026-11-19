"""Deprecated alias: ``wwdates`` was renamed to ``purecalendars`` in 3.0.0.

``import wwdates`` and every ``wwdates.<submodule>`` resolve to the matching ``purecalendars``
module, so code written for wwdates 2.x keeps working after the upgrade. Each old module name is
bound to the *same* module object, so ``isinstance`` checks and monkeypatching agree across both
names. The web calendars (``*Web``, ``DatesUSNasdaq``) are not here; they move to
``opendata-calendars``.

This shim is removed in 4.0.0. Import ``purecalendars`` instead.
"""

import importlib
import pkgutil
import sys
import warnings

import purecalendars
from purecalendars import *  # noqa: F403 - the shim re-exports the whole public surface


warnings.warn(
	"`wwdates` was renamed to `purecalendars`; `import wwdates` stops working in 4.0.0. "
	"Use `import purecalendars` instead.",
	DeprecationWarning,
	stacklevel=2,
)

# ponytail: eager aliasing of every submodule, a lazy meta-path finder if import time matters
for _module_info in pkgutil.walk_packages(purecalendars.__path__, prefix="purecalendars."):
	_str_old_name = "wwdates" + _module_info.name.removeprefix("purecalendars")
	sys.modules[_str_old_name] = importlib.import_module(_module_info.name)
	if _str_old_name.count(".") == 1:
		# A module found in sys.modules is not bound onto its parent, so `wwdates.br` needs it.
		globals()[_str_old_name.split(".")[1]] = sys.modules[_str_old_name]

__all__ = purecalendars.__all__
__version__ = purecalendars.__version__
