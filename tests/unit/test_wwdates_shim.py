"""The ``import wwdates`` compatibility shim (#83): it warns once and aliases every module."""

import importlib
import sys

import pytest


def _forget_wwdates() -> None:
	"""Drop every cached ``wwdates`` module so the next import runs the shim again."""
	for str_name in [str_name for str_name in sys.modules if str_name.split(".")[0] == "wwdates"]:
		del sys.modules[str_name]


def test_import_wwdates_warns_and_aliases_every_module() -> None:
	"""Old imports from 2.x resolve to the very same ``purecalendars`` objects, with a warning."""
	_forget_wwdates()
	with pytest.warns(DeprecationWarning, match="renamed to `purecalendars`"):
		wwdates = importlib.import_module("wwdates")

	import purecalendars
	import purecalendars.br.anbima
	from wwdates.br import DatesBRAnbima
	from wwdates.br.anbima import DatesBRAnbima as cls_from_submodule
	from wwdates.us import DatesUSFederalHolidays

	assert DatesBRAnbima is purecalendars.br.DatesBRAnbima
	assert cls_from_submodule is purecalendars.br.anbima.DatesBRAnbima
	assert DatesUSFederalHolidays is purecalendars.us.DatesUSFederalHolidays
	assert wwdates.br is purecalendars.br
	assert wwdates.__version__ == purecalendars.__version__
