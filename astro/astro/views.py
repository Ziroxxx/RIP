from .models import app_planet, app_cons_period, app_mm
from django.shortcuts import render, redirect
from django.db import connection, transaction
from django.urls import reverse

def getServices(request):
    searchText = request.GET.get('PlanetName', '')
    searchResult = app_planet.objects.filter(name__icontains=searchText)
    draft_req = request.user.user_reqs.filter(isDraft=True).first()
    print(searchResult, draft_req)
    if draft_req:
        wishCount = app_mm.objects.filter(reqID = draft_req).count()
        wishID = draft_req.reqID
    else:
        wishCount = 0
        wishID = ''
        
    return render(request, 'orders.html', {'planets': searchResult, 'wishCount': wishCount, 'wish_id': wishID, 'action': 'Добавить', 'searchText': searchText})

def getPlanet(request, planet_id):
    curPlanet = app_planet.objects.get(pk=planet_id)
    return render(request, 'order.html', {'planet': curPlanet})

def getWishList(request, wish_id):
    curWish = app_cons_period.objects.get(pk=wish_id)
    curplanet = app_planet.objects.filter(app_mm__reqID = curWish)
    return render(request, 'wish_list.html', {'wish': curplanet, 'action': 'Удалить', 'wishID': wish_id})

def addPlanet(request):
    planet_id = request.POST['addingPlanet']
    draft_request = request.user.user_reqs.filter(isDraft=True).first()
    planet_request = app_planet.objects.get(pk = planet_id)
    if draft_request and not(app_mm.objects.filter(reqID = draft_request, planetID = planet_request).exists()):
        adding = app_mm(planetID = planet_request, reqID = draft_request)
        adding.save()
    elif not(app_mm.objects.filter(reqID = draft_request, planetID = planet_request).exists()):
        newReq = app_cons_period(userID = request.user)
        newReq.save()
        adding = app_mm(planetID = app_planet.objects.get(pk=planet_id), reqID = newReq)
        adding.save()

    PlanetName = request.POST.get('searchArg', '')
    if PlanetName:
        base_url = reverse('home')
        search = f"{base_url}?PlanetName={PlanetName}"
        return redirect(search)
    return redirect('home')

def removeDraft(request):
    id = request.POST['delWish']
    c = connection.cursor()
    c.execute('update astro_app_cons_period set "isDraft" = false, "isDeleted" = true where "reqID" = %s', [id])
    transaction.commit()
    c.close()
    return redirect('home')
