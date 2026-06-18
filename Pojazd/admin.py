from django.contrib import admin
from .models import Pojazd, PojazdHistoria, Magazyn, Opona, Felga, PojazdHistoriaPrzebiegu

admin.site.register(Pojazd)
admin.site.register(Opona)
admin.site.register(Felga)
admin.site.register(Magazyn)
admin.site.register(PojazdHistoria)
admin.site.register(PojazdHistoriaPrzebiegu)
# Register your models here.
