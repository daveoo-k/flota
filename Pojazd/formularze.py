from django import forms
from .models import Pojazd, Magazyn, Opona, Felga,PojazdHistoriaPrzebiegu
from django.shortcuts import render, redirect, get_object_or_404
from django.forms import ModelChoiceField
from django.contrib.auth import get_user_model




class PojazdForm(forms.Form):
    
    marka           = forms.CharField (max_length=100)
    model           = forms.CharField (max_length=300)
    rok_produkcji   = forms.IntegerField()
    silnik          = forms.CharField (max_length=100)
    przebieg        = forms.IntegerField()
    rejestracja     = forms.CharField (max_length=10)
    kolor           = forms.CharField (max_length=100)
    data_zakupu     = forms.DateField (widget = forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'))
    n_przeglad      = forms.DateField (widget = forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'))
    oc_do           = forms.DateField (widget = forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'))
    nr_polisy       = forms.CharField (max_length=40)
    zdjecie         = forms.FileField()
  
   
    class meta:
        model = Pojazd
        fields = '__all__'

class HistoriaForm(forms.Form):
    
    wydarzenie          = forms.ChoiceField( choices = ( ('Serwis / Naprawa','Serwis / Naprawa'),('Szkoda / Wypadek', 'Szkoda / Wypadek'),('Inne','Inne')  ))                                                   
    data_wydarzenia     = forms.DateField (widget = forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'))
    opis                = forms.CharField (max_length=10000, widget=forms.Textarea)
    aktualny_przebieg   = forms.IntegerField()
    zdjecie             = forms.FileField (required=False)
    rachunek            = forms.FileField (required=False)

    @property
    def zdjecie_url(self):
        if self.zdjecie and hasattr(self.zdjecie, 'url'):
            return self.zdjecie.url

class PojazdOponaForm(forms.Form):

    nazwa_opony     = forms.CharField(max_length=300)
    rok_produkcji   = forms.IntegerField()
    opis            = forms.CharField(max_length=10000, required=False, widget=forms.Textarea)
    zdjecie         = forms.FileField(required=False)
  

class PojazdFelgaForm(forms.Form):

    nazwa_felgi     = forms.CharField (max_length=300)
    opis            = forms.CharField(max_length=10000, required=False, widget=forms.Textarea)
    sruby           = forms.CharField (max_length=300)



class PojazdZmianaOponForm(forms.Form):

    opony           = forms.ModelChoiceField(queryset = Opona.objects.filter(w_uzytku = ""), initial=0)
    felgi           = forms.ModelChoiceField(queryset = Felga.objects.filter(w_uzytku = ""), initial=0)
    miejsce_zmiany  = forms.CharField(max_length=500)
    data_zmiany     = forms.DateField(widget = forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'))
    uwagi           = forms.CharField (max_length=9500)
    zdjecie         = forms.FileField(required=False)
    przebieg        = forms.IntegerField()

class Przypisanie(forms.Form):

    User = get_user_model()
    users = User.objects.all()
    nowy       = forms.ModelChoiceField(queryset = users, initial=0)

class PojazdHistoriaPrzebieguForm(forms.ModelForm):

    class Meta:
        model = PojazdHistoriaPrzebiegu
        fields =( 'cel','z', 'data', 'do','uwagi', 'przebieg_start' ,'przebieg_stop', 'kierowca'  )
        widgets = {
            'data': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
        }





        
