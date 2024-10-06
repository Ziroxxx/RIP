from .models import planet, cons_period, mm, AuthUser
from django.db.models import Q
from astro_app.serializers import *
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from django.shortcuts import get_object_or_404
from .minio import *
from django.contrib.auth import get_user_model
import datetime

def user():
    try:
        user1 = AuthUser.objects.get(id=1)
    except:
        user1 = AuthUser(id=1, first_name="Иван", last_name="Иванов", password=1234, username="user1")
        user1.save()
    return user1

class planetMethods(APIView):
    model = planet
    serializer_class = planetSerial

    def get(self, request, format=None):
        searchText = request.query_params.get('PlanetName', '')
        searchResult = planet.objects.filter(name__icontains=searchText)
        user1 = user()
        draft_req = user1.user_reqs.filter(status='draft').first()
        if draft_req:
            wishCount = mm.objects.filter(reqID = draft_req).count()
            wishID = draft_req.reqID
        else:
            wishCount = 0
            wishID = ''
        serial_data = self.serializer_class(searchResult, many = True)
        return Response({'planets': serial_data.data, 'wishID': wishID, 'wishCount': wishCount})
    
    def post(self, request, format=None):
        row_data = self.serializer_class(data=request.data)
        if row_data.is_valid():
            row_data.save()
            return Response(row_data.data, status=status.HTTP_201_CREATED)
        return Response(row_data.errors, status=status.HTTP_400_BAD_REQUEST)



class one_planet(APIView):
    model = planet
    serializer_class = planetSerial

    def get(self, request, pk, format=None):
        obj = get_object_or_404(self.model, pk=pk)
        return Response(self.serializer_class(obj).data)
    
    def put(self, request, pk, format=None):
        obj = get_object_or_404(self.model, pk=pk)
        changing = self.serializer_class(obj, data=request.data, partial=True)        
        if changing.is_valid():
            changing.save()
            return Response(changing.data)
        return Response(changing.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk, format=None):
        obj = get_object_or_404(self.model, pk=pk)
        res = del_pic(obj)
        if 'error' in res.data:
            return res
        mm_with_planet = mm.objects.filter(planetID = obj)
        mm_with_planet.delete()
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    def post(self, request, pk, format=None):
        user1 = user()
        draft = user1.user_reqs.filter(status='draft').first()
        obj = get_object_or_404(self.model, pk=pk)
        if not draft and not(mm.objects.filter(reqID = draft, planetID = obj).exists()):
            draft = cons_period(userID = user1)
            draft.save()
        if not(mm.objects.filter(reqID = draft, planetID = obj).exists()):
            new_position = mm(reqID = draft, planetID = obj)
            new_position.save()
            return Response(status=status.HTTP_200_OK)
        return Response(status=status.HTTP_208_ALREADY_REPORTED)
    
@api_view(['Post'])
def add_image(request, pk, format = None):
    planett = get_object_or_404(planet, pk=pk)
    pic = request.FILES.get('pic')
    result = add_pic(planett, pic)
    if 'error' in result.data:
        return result
    return Response(status=status.HTTP_200_OK)

class cons_periods(APIView): #cons_periods
    model = cons_period
    serializer_class = requestSerial

    def get(self, request, format = None):
        dateCreated = request.query_params.get('dateCreated', '')
        status = request.query_params.get('status', '')
        
        filters = {}
        if dateCreated:
            filters['dateCreated'] = dateCreated
        
        if status:
            filters['status'] = status

        reqs = self.model.objects.filter(**filters).exclude(Q(status = 'draft') | Q(status = 'deleted'))
        serialized = self.serializer_class(reqs, many=True)
        return Response(serialized.data)
    
class one_cons_period(APIView):
    model = cons_period
    serializer_class = requestDetailSerial

    def get(self, request, pk, format = None):
        req = get_object_or_404(self.model, pk=pk)
        serialised = self.serializer_class(req)
        return Response(serialised.data)
    
    def put(self, request, pk, format = None):
        req = get_object_or_404(self.model, pk=pk)
        serialized = self.serializer_class(req, data=request.data, partial=True)
        if serialized.is_valid():
            serialized.save()
            return Response(serialized.data, status=status.HTTP_202_ACCEPTED)
        return Response(serialized.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk, format = None):
        req = get_object_or_404(self.model, pk=pk)
        req.status = 'deleted'
        req.save()
        return Response(self.serializer_class(req).data)
    
@api_view(['put'])
def save_by_creator(request, pk, format=None):
    req = get_object_or_404(cons_period, pk=pk)
    serialized = requestDetailSerial(req)
    if req.dateStart is not None and req.dateEnd is not None and req.constellation is not None:
        req.dateSaved = datetime.date.today().isoformat()
        req.status = 'saved'
        req.save()
        return Response(serialized.data, status=status.HTTP_200_OK)
    return Response({'error': 'some required field(s) was not declared'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['put'])
def moderate(request, pk, format=None):
    isAccepted = request.data.get('isAccepted')
    req = get_object_or_404(cons_period, pk=pk)
    if req.dateStart == '' or req.dateEnd == '' or req.constellation == '' or req.status != 'saved':
        return Response({'error': 'This request didn`t saved or have some incompete fields'}, status=status.HTTP_403_FORBIDDEN)
    req.isAccepted = isAccepted
    if isAccepted:
        req.status = 'accepted'
    else:
        req.status = 'cancelled'
    planets_in_this_req = planet.objects.filter(mm__reqID = req)
    same_req = cons_period.objects.filter(dateStart = req.dateStart, dateEnd = req.dateEnd, constellation = req.constellation).exclude(pk=pk, status = 'draft')
    planets_in_same_req = planet.objects.filter(mm__reqID__in = same_req).distinct()

    for one_planet in planets_in_this_req:
        result = mm.objects.get(planetID = one_planet, reqID = req)
        if one_planet in planets_in_same_req:
            result.isNew = False
        else:
            result.isNew = True
        result.save()

    req.dateModerated = datetime.date.today().isoformat()
    req.moderID = user()
    req.save()

    serialized = requestDetailSerial(req)
    return Response(serialized.data, status=status.HTTP_202_ACCEPTED)

class MMMethods(APIView):
    model = mm
    serializer_class = MMwithPlanetSerial

    def delete(self, requset, pk_planet, pk_req, format = None):
        mm_obj = get_object_or_404(self.model, planetID = pk_planet, reqID = pk_req)
        mm_obj.delete()
        mm_list = self.model.objects.filter(reqID = pk_req)
        return Response(self.serializer_class(mm_list, many = True).data)
    
    def put(self, request, pk_planet, pk_req, format = None):
        mm_obj = get_object_or_404(self.model, planetID = pk_planet, reqID = pk_req)
        serialized = self.serializer_class(mm_obj, data=request.data)
        if serialized.is_valid():
            serialized.save()
            mm_list = self.model.objects.filter(reqID = pk_req)
            return Response(self.serializer_class(mm_list, many = True).data, status=status.HTTP_202_ACCEPTED)
        return Response(serialized.errors, status=status.HTTP_400_BAD_REQUEST)
    
class userMethods(APIView):
    model = get_user_model()
    serializer_class = userSerial

    def post(self, request, format = None):
        serialized = self.serializer_class(data=request.data)
        if serialized.is_valid():
            user1 = self.model.objects.create_user(
                username = serialized.validated_data.get('username'),
                password = serialized.validated_data.get('password'),
                is_superuser = serialized.validated_data.get('is_superuser'),
                is_staff = serialized.validated_data.get('is_staff'),
                email = serialized.validated_data.get('email'),
                first_name = serialized.validated_data.get('first_name'),
                last_name = serialized.validated_data.get('last_name')
            )
            user_list = self.model.objects.all()
            return Response(self.serializer_class(user_list, many=True).data, status=status.HTTP_201_CREATED)
        return Response(serialized.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request, pk, format = None):
        user1 = get_object_or_404(self.model, pk = pk)
        serialized = self.serializer_class(user1, data=request.data, partial = True)
        if serialized.is_valid():
            serialized.save()
            if 'password' in serialized.validated_data:
                user1.set_password(serialized.validated_data.get('password'))
                user1.save()
            return Response(serialized.data, status=status.HTTP_202_ACCEPTED)
        return Response(serialized.errors, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['post'])
def autentification(request, pk, format = None):
    obj = get_user_model().objects.get(pk = pk)
    if obj.check_password(request.data.get('password')) and obj.username == request.data.get('username'):
        return Response({'auth': 'success'}, status=status.HTTP_200_OK)
    return Response({'auth': 'failed, wrong password or username'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['post'])
def logout(request, pk, format = None):
    return Response({'status': 'logged out'}, status=status.HTTP_401_UNAUTHORIZED)