# Redefining DATETIM formats for more compact display

from django.conf.locale.de import formats as de_formats
from django.conf.locale.en import formats as en_formats
from django.conf.locale.es import formats as es_formats
from django.conf.locale.es import formats as fr_formats
from django.conf.locale.it import formats as it_formats
from django.conf.locale.pt_BR import formats as pt_br_formats
from django.conf.locale.ru import formats as ru_formats
from django.conf.locale.tr import formats as tr_formats
from django.conf.locale.uk import formats as uk_formats


# The *_FORMAT strings use the Django date format syntax,
# see https://docs.djangoproject.com/en/dev/ref/templates/builtins/#date

de_formats.DATE_FORMAT = "j.m.y"            # 5.10.25
de_formats.DATETIME_FORMAT = "d. m Y H:i"   # 05. 10 2025 14:30
de_formats.SHORT_DATE_FORMAT = "d.m.y"      # 05.10.25

en_formats.DATE_FORMAT = "m/d/y"            # 10/25/25
en_formats.DATETIME_FORMAT = "m j, Y, P"    # Oct 5, 2025, 1:30 p.m.
en_formats.SHORT_DATE_FORMAT = "m/d/y"      # 10/25/25

es_formats.DATE_FORMAT = "d/m/y"
es_formats.DATETIME_FORMAT = r"j \d\e M \d\e Y à\s H:i"
es_formats.SHORT_DATE_FORMAT = "d/m/y"

fr_formats.DATE_FORMAT = "d/m/y"            # 25/10/25
fr_formats.DATETIME_FORMAT = r"j \d\e M \d\e Y \a \l\a\s H:i"
fr_formats.SHORT_DATE_FORMAT = "d/m/y"      # 25/10/25

it_formats.DATE_FORMAT = "d/m/y"            # 25/10/25
it_formats.DATETIME_FORMAT = "d M Y H:i"    # 25 Ott 2006 14:30
it_formats.SHORT_DATE_FORMAT = "d/m/y"      # 25/10/25

pt_br_formats.DATE_FORMAT = 'd/m/y'
pt_br_formats.DATETIME_FORMAT = r"j \d\e M \d\e Y à\s H:i"
pt_br_formats.SHORT_DATE_FORMAT = 'd/m/y'

ru_formats.DATE_FORMAT = 'd.m.y'
ru_formats.DATETIME_FORMAT = "j M Y H:i:s"
ru_formats.SHORT_DATE_FORMAT = 'd.m.y'

tr_formats.DATE_FORMAT = 'd m y'            # 05 10 25
tr_formats.DATETIME_FORMAT = "d M Y H:i"    # 5 Oct 2025 14:30
tr_formats.SHORT_DATE_FORMAT = 'd m y'      # 05 10 25

uk_formats.DATE_FORMAT = 'd.m.y'            # 05.10.25
uk_formats.DATETIME_FORMAT = "j M Y H:i:s"  # 5 Oct 2025 14:30:59
uk_formats.SHORT_DATE_FORMAT = 'd.m.y'      # 05.10.25
