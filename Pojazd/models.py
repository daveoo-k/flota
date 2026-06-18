# Create your models here.
from django.db import models
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

# Create your models here.


class Magazyn(models.Model):
    
    nazwa           = models.CharField (max_length=200)
    opis            = models.TextField (max_length=10000)
    zdjecie         = models.FileField (blank=True)
    w_uzytku        = models.CharField (max_length=100,blank=True)

    def __str__(self):
       return u'{0}'.format(self.nazwa)

class Opona(models.Model):
    
    nazwa_opony     = models.CharField (max_length=200)
    producent       = models.CharField (max_length= 100)
    model           = models.CharField (max_length= 100,blank=True, null=True)
    rozmiar         = models.CharField (max_length= 10)
    rok_produkcji   = models.IntegerField ()
    sezon           = models.CharField (max_length= 13)
    opis            = models.TextField (max_length=10000,blank=True, null=True)
    zdjecie         = models.FileField (blank=True, upload_to='img/opony/%Y/%m/%d')
    w_uzytku        = models.CharField (max_length=100, blank=True, default="")
    dodal           = models.CharField(max_length=200)
    data_dodania    = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        
       #return u'{0}'.format(self.nazwa_opony)
       return u'{0}'.format(self.producent + " " + self.rozmiar + " " + self.sezon)

class Felga(models.Model):
    
    nazwa_felgi     = models.CharField (max_length=200)    
    sruby           = models.CharField (max_length=200)
    opis            = models.TextField (max_length=10000,blank=True)
    zdjecie         = models.FileField (blank=True)
    w_uzytku        = models.CharField (max_length=100,blank=True,default="")
    dodal           = models.CharField(max_length=200)
    data_dodania    = models.DateTimeField(auto_now_add=True)
    def __str__(self):
       return u'{0}'.format(self.nazwa_felgi)


class Pojazd(models.Model):

    marka           = models.CharField (max_length=100)
    model           = models.CharField (max_length=300)
    rok_produkcji   = models.IntegerField()
    silnik          = models.CharField (max_length=100)
    rejestracja     = models.CharField (max_length=100, unique=True)
    kolor           = models.CharField (max_length=100)
    data_zakupu     = models.DateField ()
    data_sprzedazy  = models.DateField (null=True, blank=True)
    #kola_CHOICES    =  [ ('z', 'zimowe'),('l', 'letnie'),('w', 'wielosezon'),]
    opony           = models.ForeignKey(Opona, on_delete=models.SET_NULL, null=True,blank=True)
    felgi           = models.ForeignKey(Felga, on_delete=models.SET_NULL, null=True,blank=True)
    historia        = models.IntegerField(null=True, blank=True)
    przebieg        = models.IntegerField()
    zdjecie         = models.FileField (blank=True, upload_to='img/pojazdy/%Y/%m/%d')
    dodal           = models.CharField(max_length=200)
    data_dodania    = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    przypisany      = models.CharField (max_length=300, default="1")
    n_przeglad      = models.DateField ()
    oc_do           = models.DateField ()
    nr_polisy       = models.CharField (max_length=40)

    
    def __str__(self):
       return u'{0}'.format(self.rejestracja)
    
    class Meta :
        permissions = (("can_add_vehicles", "Doadj nowy pojazd"),("can_add_history  ", "Doadj nowy wpis"))

class Pojazdtemp(models.Model):

    marka           = models.CharField (max_length=100)
    model           = models.CharField (max_length=300)
    rok_produkcji   = models.IntegerField()
    silnik          = models.CharField (max_length=100)
    rejestracja     = models.CharField (max_length=100, unique=True)
    kolor           = models.CharField (max_length=100)
    data_zakupu     = models.DateField ()
    data_sprzedazy  = models.DateField (null=True, blank=True)
    #kola_CHOICES    =  [ ('z', 'zimowe'),('l', 'letnie'),('w', 'wielosezon'),]
    opony           = models.ForeignKey(Opona, on_delete=models.SET_NULL, null=True,blank=True)
    felgi           = models.ForeignKey(Felga, on_delete=models.SET_NULL, null=True,blank=True)
    historia        = models.IntegerField(null=True, blank=True)
    przebieg        = models.IntegerField()
    zdjecie         = models.FileField (blank=True, upload_to='img/pojazdy/%Y/%m/%d')
    dodal           = models.CharField(max_length=200)
    data_dodania    = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    przypisany      = models.CharField (max_length=300, default="1")
    n_przeglad      = models.DateField ()
    oc_do           = models.DateField ()
    nr_polisy       = models.CharField (max_length=40)

    
    def __str__(self):
       return u'{0}'.format(self.rejestracja)
    class Meta :
        permissions = (("can_add_vehicles", "Doadj nowy pojazd"),("can_add_history  ", "Doadj nowy wpis"))

class PojazdHistoria(models.Model):

    rejestracja         = models.CharField (max_length=100)
    wydarzenie          = models.CharField (max_length=200)
    data_wydarzenia     = models.DateField ()
    opis                = models.TextField (max_length=10000)
    aktualny_przebieg   = models.IntegerField()
    zdjecie             = models.FileField (blank=True, upload_to='img/historia/%Y/%m/%d')
    rachunek            = models.FileField (blank=True, upload_to='rachunki/historia/%Y/%m/%d')
    dodal               = models.CharField(max_length=200)
    data_dodania        = models.DateTimeField(auto_now_add=True)
    def __str__(self):
       return u'{0}'.format(self.rejestracja +" "+ self.wydarzenie) 


class PojazdHistoriaPrzebiegu(models.Model):

    rejestracja         = models.CharField (max_length=100)
    cel                 = models.CharField (max_length=300)
    z                   = models.CharField (max_length=300)
    do                  = models.CharField (max_length=300)
    data                = models.DateField ()
    uwagi               = models.TextField (max_length=10000,blank=True)
    przebieg_start      = models.IntegerField()
    przebieg_stop       = models.IntegerField()
    kierowca            = models.CharField (max_length=300)
    dodal               = models.CharField(max_length=200)
    data_dodania        = models.DateTimeField(auto_now_add=True)
    

    def __str__(self):
       return u'{0}'.format(self.rejestracja +" "+ self.cel+" "+ str(self.data)) 

    @property
    def zdjecie_url(self):
        if self.zdjecie and hasattr(self.zdjecie, 'url'):
            return self.zdjecie.url


