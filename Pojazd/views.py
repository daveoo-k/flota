from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpRequest
from .formularze import PojazdForm , PojazdOponaForm, PojazdFelgaForm, PojazdZmianaOponForm, HistoriaForm, PojazdHistoriaPrzebieguForm, Przypisanie
from .models import Pojazd,Pojazdtemp, PojazdHistoria, Magazyn, Opona, Felga, PojazdHistoriaPrzebiegu
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import Permission, User
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db.models import Q
from django.contrib.auth.context_processors import PermWrapper
from django.utils import timezone
from datetime import timedelta
from django.conf import settings
from django.core.mail import EmailMessage


# Create your views here.
def home_view(request):
    return render (request, "base.html",{} )

def kontakt_view(request):
    sent = False
    if request.method == 'POST':
        kontakt = request.POST
        subject = 'Formularz kontaktowy ze strony FleetManager: "%s"' % kontakt.get('subject', '')
        body = kontakt.get('body', '')
        reply_to = kontakt.get('email', '')
        recipient = settings.CONTACT_RECIPIENT

        try:
            EmailMessage(
                subject=subject,
                body=body,
                from_email=settings.EMAIL_HOST_USER or None,
                to=[recipient] if recipient else [],
                reply_to=[reply_to] if reply_to else None,
            ).send(fail_silently=False)
            sent = True
            print('Email sent!')
        except Exception as exc:
            print('Something went wrong...', exc)

    return render (request, "kontakt.html", {'sent': sent})

def handle_uploaded_file(f):
    with open('img/%Y/%m/%d/'+f, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)

def login_view(request,*args,**kwargs):
    
    errors={}
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate( request, username=username, password=password )
        if user is not None:
            login(request, user)
            user_pojazds = Pojazd.objects.filter(przypisany = user.username)
            user_pojazd =""
            if user_pojazds.count() == 0 : # brak przypisanych pojazdów urzytkownika 
                request.session['user_pojazd'] = ""
                return redirect('../')

            elif user_pojazds.count() == 1 :
                user_pojazd = user_pojazds[0]
                request.session['user_pojazd'] = user_pojazd.rejestracja
                return redirect('../')

            else :
                user_pojazd = "pojazdy" # urzytkownik ma wiecej niz 1 pojazd 
                request.session['user_pojazd'] =  user_pojazd
                return redirect('../')

        else:
            errors['error'] = 'Błędny login lub haslo'

    return render (request, "login.html", errors )

def logout_view(request):

    logout(request)
    return redirect ('../../')


@permission_required('Pojazd.add_pojazd')
def pojazd_create_view(request,*args,**kwargs):
    
    if not request.user.is_authenticated : # manualne sprawdzenie bez dekoratora
        return redirect ("../login")

    elif request.user.is_authenticated:
        
        new = {}
        form_dane ={}
        form_pojazd = PojazdForm()
        ok=""
        if request.method == 'POST':
            form_dane = PojazdForm(request.POST, request.FILES)
            if form_dane.is_valid(): 
                reg = form_dane.cleaned_data['rejestracja']
                pojazd = form_dane.cleaned_data
                if 'zdjecie' in request.FILES:
                    pojazd['zdjecie'] = request.FILES['zdjecie']
                    pojazd['dodal'] = request.user.username
                    form_dane = Pojazdtemp.objects.create(**pojazd)
                    request.session['temp'] = form_dane.rejestracja
                    form_pojazd = ""
                
                
                    
                else :
                    print('nie ma zdjecia')
        
            else:
                print(form_dane.errors)

        if  request.POST.get('ok'):
            # rejestracja z formularza (pewniejsze niz sesja na serverless), z fallbackiem do sesji
            reg = request.POST.get('reg') or request.session.get('temp')
            rows = Pojazdtemp.objects.filter(rejestracja=reg).values() if reg else None
            if not rows:
                # brak danych tymczasowych (np. odswiezenie/utracona sesja) -> zacznij od nowa
                return redirect('../nowy/')
            dane = dict(rows[0])
            dane.pop('id', None)                        # nowy klucz glowny, nie nadpisuj id=0
            Pojazd.objects.create(**dane)               # przeniesienie z tabeli temp do glownej
            Pojazdtemp.objects.filter(rejestracja=reg).delete()
            request.session.pop('temp', None)
            return redirect("../nowa-opona/?" + reg)    # do tworzenia opon i dalej felg

        context = {
            'form' : form_pojazd,
            'obj' : form_dane,
            }
    

        return render (request, "create_view.html", context)

@permission_required('Pojazd.add_pojazd')
@login_required(redirect_field_name='login')
def zapisz_view (request):

    item = request.session.get('temp')
    if item:
        print (item)

    return render (request, "item_display.html",{})

@permission_required('Pojazd.add_pojazd')
@login_required(redirect_field_name='login')

def wheels_create_view(request,*args,**kwargs):

    request.session['temp_o'] = 0
    request.session['temp_f'] = 0
    temp_o = {}
    temp_f = {}

    form_opona = PojazdOponaForm()
    form_felga = PojazdFelgaForm()

    if 'rok_produkcji' in request.POST:
        request.session['temp_o'] = request.POST
        temp_o = request.POST 
        form_opona = ""
        
    if 'sruby' in request.POST:
        request.session['temp_f'] = request.POST
        temp_f = request.POST 
        form_felga = ""

    if form_opona == "" and form_felga == ""  and request.method == "GET":
        return redirect("../zapisz")

    context = {
            'form_o':form_opona,
            'form':form_felga,
            'temp_o': request.session['temp_o'], 
            'temp_f': request.session['temp_f'],
    }

    return render (request,"create_wheels.html", context)


@login_required(redirect_field_name='login')
@permission_required('Pojazd.add_opona')    
def opona_create_view(request,*args,**kwargs ):

    form_opona =  PojazdOponaForm()
    new_reg = request.get_full_path().lstrip('/nowa-opona/?reg=').rstrip('&ok=zapisz') # nr rejstracyjny dla przypisania opony odpowiedniemu pojazdowi
    context = {      
                        'form' : form_opona }

    if request.method == 'POST':

        form_opona = PojazdOponaForm(request.POST)
        if form_opona.is_valid():
            
            new_opona = form_opona.cleaned_data
            new_opona['w_uzytku'] = new_reg
            new_opona['dodal'] = request.user.username
            new_opona = Opona.objects.create(**new_opona)

            if len(new_reg) > 0 :
                veh = Pojazd.objects.filter(rejestracja=new_reg).update(opony=new_opona)                


            path= "../nowa-felga/?"+new_reg # przesłanie dalej nr rejstracyjnego pojazdu dla ktorego dodawane sa opony
            return redirect(path)
        else:
            print(form_opona.errors)

    return render (request, "create_opona.html", context)

@login_required(redirect_field_name='login')
@permission_required('Pojazd.add_felga')
def felga_create_view(request,*args,**kwargs):

    form_felga =  PojazdFelgaForm()
    new_reg = request.get_full_path().lstrip('/nowa-felga/?').rstrip('&ok=zapisz') # rejestracja pojazdu dla ktorego tworzy sie felge

    context = {      
                        'form' : form_felga }

    if request.method == 'POST':
        
        form_felga = PojazdFelgaForm(request.POST)
        if form_felga.is_valid():
            
            new_felga = form_felga.cleaned_data
            new_felga['w_uzytku'] = new_reg  
            new_felga['dodal'] = request.user.username
            new_felga = Felga.objects.create(**new_felga)
            if len(new_reg) > 0 :
                veh = Pojazd.objects.filter(rejestracja=new_reg).update(felgi=new_felga)
            path= "../pojazd/"+str(new_reg)
    
            return redirect(path)
        else:
            print(form_felga.errors)

    return render (request, "create_felga.html", context)

@login_required(redirect_field_name='login')
@permission_required('Pojazd.view_pojazd')
def przedmiot_view(request,id):
    # widok do wyswietlania różnych modeli litera przed ID stanowi typ obiektu
    obj= {}
    if id[0] == "A" :
        id = int(id.lstrip("A"))
        obj = Felga.objects.get(id=id)
    elif id[0] == "B" :
        id = int(id.lstrip("B"))
        obj = Opona.objects.get(id=id)
    elif id[0] == "C" :
        id = int(id.lstrip("C"))
        obj = Pojazd.objects.get(id=id)
    elif id[0] == "H" :
        id = int(id.lstrip("H"))
        obj = PojazdHistoria.objects.get(id=id)
    else :
        "błąd id"
        
    context = {
        'obj' : obj
    }


    return render (request, 'item_display.html', context)


@login_required(redirect_field_name='login')
@permission_required('Pojazd.view_pojazd')
def pojazd_opis_view(request,rejestracja):

    User = get_user_model() 
    users = {}
    form = Przypisanie()
    obj = Pojazd.objects.get(rejestracja = rejestracja)
    q = PojazdHistoria.objects.filter(rejestracja = rejestracja ).values().order_by('-aktualny_przebieg')
    e = PojazdHistoria.objects.filter(rejestracja = rejestracja ).count()
    if  request.user.has_perm('Pojazd.delete_pojazdhistoriaprzebiegu'):
        users = User.objects.exclude(username="jakbruttonetto")  # lista uzytkowników dla managera bez superusera
        q2 = PojazdHistoriaPrzebiegu.objects.filter(rejestracja = rejestracja).values().order_by('-przebieg_stop')
        e2 = PojazdHistoriaPrzebiegu.objects.filter(rejestracja = rejestracja).count()
    else :      # uzytkownik widzi jedynie 4 ostatnie pozycje w histori przebiegu
        q2 = PojazdHistoriaPrzebiegu.objects.filter(rejestracja= rejestracja).values().order_by('-przebieg_stop')
        if q2.count() > 3: 
            e2 = 4  
        else :
            e2= q2.count()
    inner_context = {}
    context = {}

    for i in range (0,e):
        inner_context['q'+str(i)]= q[i]

    inner_context2 = {}
    for i in range (0,e2):
        inner_context2['q2'+str(i)]= q2[i]
        
    if request.method == "POST":  # przypisanie pojazdu urzytkownikowi
        nowy = request.POST['nowy']
        zmiana = Pojazd.objects.filter(rejestracja = obj.rejestracja).update(przypisany = nowy)
        if nowy == request.user.username :          # jesli uzytkownik sam zmienia swoj pojazd aktualizujemy zmienna sesji
            request.session['user_pojazd'] = obj.rejestracja
            print (request.session['user_pojazd'])
        if (nowy != request.user.username and request.session['user_pojazd'] == obj.rejestracja ):  
            request.session['user_pojazd'] = ""
            print (request.session['user_pojazd'])
        

        return redirect(request.get_full_path()) 
    
    warning_przeglad = obj.n_przeglad - timedelta(days = 14)
    warning_oc  = obj.oc_do - timedelta(days = 14)

    context = {     'obj' :obj,
                    'context': inner_context,
                    'context2': inner_context2,
                    'e': e , 
                    'e2': e2 , 
                    'users' : users,
                    'form' : form,
                    'warning_oc': warning_oc,
                    'warning_przeglad':warning_przeglad,
                    } 

    return render (request, "opis.html", context)

@login_required(redirect_field_name='login')
@permission_required('Pojazd.change_pojazd')
@permission_required('Pojazd.change_opona')
@permission_required('Pojazd.change_felga')
def pojazd_zmiana_opon_view(request):

    form = PojazdZmianaOponForm()
    reg = request.GET['rejestracja']
   
    veh = Pojazd.objects.get(rejestracja = reg)

    context = {
        ''
        'obj' : veh ,
        'form' : form
     }

    if request.method == 'POST' :
        #zmiana opon
        swap_opona = Opona.objects.get(id=request.POST['opony'])
        swap_off = Opona.objects.filter(w_uzytku = reg ).update(w_uzytku="")
        swap_on = Opona.objects.filter(id=request.POST['opony'] ).update(w_uzytku=reg)
        swap_p = Pojazd.objects.filter(rejestracja = reg).update(opony=swap_opona)
        
        swap_felga = Felga.objects.get(id=request.POST['felgi'])
        swap_off_f = Felga.objects.filter(w_uzytku = reg ).update(w_uzytku="")
        swap_on_f = Felga.objects.filter(id=request.POST['felgi'] ).update(w_uzytku=reg)
        swap_p = Pojazd.objects.filter(rejestracja = reg).update(felgi=swap_felga)
        przebieg=0
        opis_zmiany ='Opony : ' + str(veh.opony) + ' na felgach : ' + str(veh.felgi) + ' zamieniono na opony : ' + str(swap_opona.nazwa_opony) + " i felgi : " + str(swap_felga.nazwa_felgi) + "   " + str(request.POST['uwagi']) +' miejsce zmiany :  ' + str(request.POST['miejsce_zmiany'])   

        if int(request.POST['przebieg']) >  veh.przebieg :  
            p = Pojazd.objects.filter(rejestracja = reg).update( przebieg = request.POST['przebieg'])

        historia = PojazdHistoria.objects.create( 
            rejestracja = reg, 
            wydarzenie ='zmiana  kół/opon',
            data_wydarzenia = request.POST['data_zmiany'],
            opis = opis_zmiany,
            zdjecie = request.POST['zdjecie'],
            aktualny_przebieg = request.POST['przebieg']
            )

        return redirect("../pojazd/"+str(reg))
        
       

    return render (request, "zmiana_opon.html", context)

@login_required(redirect_field_name='login')
@permission_required('Pojazd.view_pojazdhistoria')
def pojazdHistoria_find_view(request,*args,**kwargs):
    context={}

    if request.POST:

        q = PojazdHistoria.objects.filter(opis__contains=request.POST['opis']).values()
        e = PojazdHistoria.objects.filter(opis__contains=request.POST['opis']).count()
        inner_context = {}
        for i in range (0,e):
            inner_context['q'+str(i)]= q[i]

        context = { 'context': inner_context, 
                    'e': e , 
                    }     

        # return redirect ('wynik/')
    return render (request,'historia_find_view.html',context)

@login_required(redirect_field_name='login')
@permission_required('Pojazd.add_pojazd')
def pojazd_find_view(request,*args,**kwargs):
    

    context={}
    q = Pojazd.objects.all().values()
    e = Pojazd.objects.all().count()
    inner_context = {}

    for i in range (0,e):
        inner_context['q'+str(i)]= q[i]

    context = { 'context': inner_context, 
                    'e': e , 
                    }     

    if request.POST:

        q = Pojazd.objects.filter(rejestracja__contains=request.POST['rejestracja']).values()
        e = Pojazd.objects.filter(rejestracja__contains=request.POST['rejestracja']).count()
        inner_context = {}
        for i in range (0,e):
            inner_context['q'+str(i)]= q[i]

        context = { 'context': inner_context, 
                    'e': e , 
                    }     

        # return redirect ('wynik/')
    return render (request,'find_view.html',context)


@login_required(redirect_field_name='login')
@permission_required('Pojazd.view_pojazd')
def user_find_view(request,*args,**kwargs):

    context={}
    q = Pojazd.objects.filter(Q(przypisany = request.user.username ) | Q( przypisany=  "1" )).values()  # uzytkownik widzi pojazdy dostepne oraz te przypisane do niego
    e = Pojazd.objects.filter(Q(przypisany = request.user.username ) | Q( przypisany=  "1" )).count()
    inner_context = {}

    for i in range (0,e):
        inner_context['q'+str(i)]= q[i]

    context = { 'context': inner_context, 
                    'e': e , 
                    }     
    if request.POST:

        q = q.filter(rejestracja__contains=request.POST['rejestracja']).values()  # wyszukiwanie w dostępnych samochodach dla usera
        e = q.count()
        inner_context = {}
        for i in range (0,e):
            inner_context['q'+str(i)]= q[i]

        context = { 'context': inner_context, 
                    'e': e , 
                    }     

    return render (request,'find_view.html',context)

@login_required(redirect_field_name='login')
@permission_required('Pojazd.view_opona')
def magazyn_view(request,*args,**kwargs):
    
    queryset = Opona.objects.filter(w_uzytku = "")
    queryset2 = Felga.objects.filter(w_uzytku = "")
    if (request.POST) :
        queryset = Opona.objects.filter(nazwa_opony__contains=request.POST['kola'])
        queryset2 = Felga.objects.filter(nazwa_felgi__contains=request.POST['kola'])

    context={

        'opona_list' : queryset ,
        'felga_list' : queryset2
    }


        # return redirect ('wynik/')
    return render (request,'magazyn.html',context)

@login_required(redirect_field_name='login')
@permission_required('Pojazd.delete_pojazd')
def pojazd_usun_view(request,rejestracja):

    if  request.GET:
        objtodel = Pojazd.objects.filter(rejestracja = rejestracja).delete()
        return redirect ('../find/')
    
    return render (request,'usun.html',{'rejestracja' : rejestracja })

@login_required(redirect_field_name='login')
@permission_required('Pojazd.delete_felga')
@permission_required('Pojazd.delete_opona')
def usun_przedmiot(request,id):

    nazwa = "" # nazwa do wyswietlenia w template
    if id[0] == "A" : # litera przed nr id identyfikuje typ obiektu
        objtodel = Felga.objects.get(id = int(id.lstrip("A")))
        nazwa = objtodel.nazwa_felgi
        if request.GET :
            dels = Felga.objects.get(id = int(id.lstrip("A"))).delete()
            return redirect ('../magazyn')
    elif id[0] == 'B' :
        objtodel = Opona.objects.get(id = int(id.lstrip("B")))
        nazwa = objtodel.nazwa_opony
        if request.GET :
            objtodel = Opona.objects.get(id = int(id.lstrip("B"))).delete()
            return redirect ('../magazyn')
    elif id[0] == 'C' :
        id = id.lstrip("C")
        objtodel = Magazyn.objects.get(id = int(id.lstrip("B")))
        nazwa = objtodel.nazwa
        if request.GET :
            objtodel = Magazyn.objects.get(id = int(id.lstrip("B"))).delete()
            return redirect ('../magazyn')
    elif id[0] == 'H' :
        id = id.lstrip("h")
        objtodel = PojazdHistoria.objects.get(id = int(id.lstrip("H")))
        nazwa = objtodel.wydarzenie + " " + str(objtodel.data_wydarzenia)
        if request.GET :
            objtodel = PojazdHistoria.objects.get(id = int(id.lstrip("H"))).delete()
            return redirect ('../')
    else :
        print ("id error")

    return render (request,'usun.html', {'nazwa':nazwa} )

@login_required(redirect_field_name='login')
@permission_required('Pojazd.add_pojazdhistoria')
def historia_create_view (request):

    form_historia = HistoriaForm()
    reg = request.GET['rejestracja']

    if  request.method == 'POST':
        wpis = HistoriaForm(request.POST)
        if wpis.is_valid():
            wpis = wpis.cleaned_data    
            if 'rachunek' in request.FILES:
                wpis['rachunek'] = request.FILES['rachunek']
            if 'zdjecie' in request.FILES:
                wpis['zdjecie'] = request.FILES['zdjecie']

            wpis['dodal'] = request.user.username
            obj = PojazdHistoria.objects.create(**wpis)
            obj.save()
            obj = PojazdHistoria.objects.filter(id=obj.id).update(rejestracja = reg)

            return redirect('../historia-find/')

    context = {
        'form': form_historia,
    }
        
    return render (request, 'historia_create.html', context)

@login_required(redirect_field_name='login')
@permission_required('Pojazd.add_pojazdhistoriaprzebiegu')
def historia_przebiegu_create_view (request):

    form_historia = PojazdHistoriaPrzebieguForm()
    reg = request.GET['rejestracja']
    obj = Pojazd.objects.get(rejestracja=reg)

    if  request.method == 'POST':
        wpis = PojazdHistoriaPrzebieguForm(request.POST)
        if wpis.is_valid():
            wpis = wpis.cleaned_data
            wpis['rejestracja'] = reg
            wpis['dodal'] = request.user.username
            obj_hp = PojazdHistoriaPrzebiegu.objects.create(**wpis)
            obj = Pojazd.objects.filter(id=obj.id).update(przebieg = request.POST['przebieg_stop'],)
            return redirect('../pojazd/'+reg)

    context = {
        'form': form_historia,
        'obj': obj
    }
        
    return render (request, 'historia_przebiegu_create.html', context)




  