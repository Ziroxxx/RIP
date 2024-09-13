from .models import planets, requests, mm
from django.shortcuts import render, redirect
from django.db import connection, transaction

def getServices(request):
    data_planets = planets.objects.all()
    searchText = request.GET.get('PlanetName', '')
    searchResult = planets.objects.filter(name__icontains=searchText)
    
    draft_req = request.user.user_reqs.filter(isDraft=True).first()
    if draft_req:
        wishCount = mm.objects.filter(reqID = draft_req).count()
        wishID = draft_req.reqID
    else:
        wishCount = 0
        wishID = ''

    if searchText == '':
        return render(request, 'orders.html', {'planets': data_planets, 'wishCount': wishCount, 'wish_id': wishID, 'action': 'Добавить', 'searchText': searchText})
    return render(request, 'orders.html', {'planets': searchResult, 'wishCount': wishCount, 'wish_id': wishID, 'action': 'Добавить', 'searchText': searchText})

def getPlanet(request, planet_id):
    curPlanet = planets.objects.get(pk=planet_id)
    return render(request, 'order.html', {'planet': curPlanet})

def getWishList(request, wish_id):
    curWish = requests.objects.get(pk=wish_id)
    curPlanets = planets.objects.filter(mm__reqID = curWish)
    return render(request, 'wish_list.html', {'wish': curPlanets, 'action': 'Удалить', 'wishID': wish_id})

def addPlanet(request):
    planet_id = request.POST['addingPlanet']
    draft_request = request.user.user_reqs.filter(isDraft=True).first()
    planet_request = planets.objects.get(pk = planet_id)
    if draft_request and not(mm.objects.filter(reqID = draft_request, planetID = planet_request).exists()):
        adding = mm(planetID = planet_request, reqID = draft_request)
        adding.save()
    elif not(mm.objects.filter(reqID = draft_request, planetID = planet_request).exists()):
        newReq = requests(userID = request.user)
        newReq.save()
        adding = mm(planetID = planets.objects.get(pk=planet_id), reqID = newReq)
        adding.save()

    return redirect('home')

def removeDraft(request):
    id = request.POST['delWish']
    c = connection.cursor()
    c.execute('update astro_requests set "isDraft" = false, "isDeleted" = true where "reqID" = %s', [id])
    transaction.commit()
    c.close()
    return redirect('home')
