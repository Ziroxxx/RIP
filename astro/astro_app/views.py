from .models import planet, cons_period, mm, AuthUser
from django.db.models import Q
from astro_app.serializers import *
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from django.shortcuts import get_object_or_404
from .minio import *
from django.contrib.auth import get_user_model
import datetime
from drf_yasg.utils import swagger_auto_schema
from django.contrib.auth import authenticate
from django.http import HttpResponse
from rest_framework.permissions import AllowAny
from rest_framework.decorators import authentication_classes
from astro_app.permissions import IsAdmin, IsManager, IsAuth
from django.conf import settings
import uuid
from .getUser import getUserBySession
import redis
from django.contrib.auth.models import AnonymousUser

session_storage = redis.StrictRedis(host=settings.REDIS_HOST, port=settings.REDIS_PORT)

def method_permission_classes(classes):
    def decorator(func):
        def decorated_func(self, *args, **kwargs):
            self.permission_classes = classes
            user = getUserBySession(self.request)
            if user == AnonymousUser():
                return Response({"detail": "Authentication credentials were not provided."}, status=401)
            else:
                try:
                    self.check_permissions(self.request)
                except Exception as e:
                    return Response({"detail": "You do not have permission to perform this action."}, status=403)
            return func(self, *args, **kwargs)
        return decorated_func
    return decorator

class planetMethods(APIView):
    model = planet
    serializer_class = planetSerial

    def get(self, request, format=None): #все планеты
        searchText = request.query_params.get('PlanetName', '')
        searchResult = planet.objects.filter(name__icontains=searchText)
        user1 = getUserBySession(self.request)
        if user1 != AnonymousUser():
            draft_req = user1.user_reqs.filter(status='draft').first()
            if draft_req:
                wishCount = mm.objects.filter(reqID = draft_req).count()
                wishID = draft_req.reqID
            else:
                wishCount = 0
                wishID = ''
        else:
            wishCount = 0
            wishID = ''
        serial_data = self.serializer_class(searchResult, many = True)
        return Response({'planets': serial_data.data, 'wishID': wishID, 'wishCount': wishCount})
    
    @swagger_auto_schema(request_body=serializer_class)
    @method_permission_classes((IsAdmin,))
    def post(self, request, format=None): #добавление планеты
        row_data = self.serializer_class(data=request.data)
        if row_data.is_valid():
            row_data.save()
            return Response(row_data.data, status=status.HTTP_201_CREATED)
        return Response(row_data.errors, status=status.HTTP_400_BAD_REQUEST)



class one_planet(APIView):
    model = planet
    serializer_class = planetSerial

    def get(self, request, pk, format=None): #инфа об одной планете
        obj = get_object_or_404(self.model, pk=pk)
        return Response(self.serializer_class(obj).data)
    
    @swagger_auto_schema(request_body=serializer_class)
    @method_permission_classes((IsAdmin,))
    def put(self, request, pk, format=None): #редактирование планеты (без картинки)
        obj = get_object_or_404(self.model, pk=pk)
        changing = self.serializer_class(obj, data=request.data, partial=True)        
        if changing.is_valid():
            changing.save()
            return Response(changing.data)
        return Response(changing.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @method_permission_classes((IsAdmin,))
    def delete(self, request, pk, format=None): #удаление планеты
        obj = get_object_or_404(self.model, pk=pk)
        res = del_pic(obj)
        if 'error' in res.data:
            return res
        mm_with_planet = mm.objects.filter(planetID = obj)
        mm_with_planet.delete()
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @method_permission_classes((IsAuth,))
    @swagger_auto_schema(request_body=serializer_class)
    def post(self, request, pk, format=None): #добавление планеты в заявку
        user1 = getUserBySession(request)
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

@method_permission_classes((IsAdmin,))
@swagger_auto_schema(method='post', request_body=planetSerial)    
@api_view(['Post'])
def add_image(request, pk, format = None): #редактирование/добавление картинки
    planett = get_object_or_404(planet, pk=pk)
    pic = request.FILES.get('pic')
    result = add_pic(planett, pic)
    if 'error' in result.data:
        return result
    return Response(status=status.HTTP_200_OK)

class cons_periods(APIView): #cons_periods
    model = cons_period
    serializer_class = requestSerial

    @method_permission_classes((IsAuth,))
    def get(self, request, format = None): #получение всех заявок
        user = getUserBySession(request)
        dateCreated = request.query_params.get('dateCreated', '')
        status = request.query_params.get('status', '')
        
        filters = {}
        if dateCreated:
            filters['dateCreated'] = dateCreated
        
        if status:
            filters['status'] = status
        if not (user.is_staff or user.is_superuser):
            user = getUserBySession(request)
            filters['userID'] = user

        reqs = self.model.objects.filter(**filters).exclude(Q(status = 'draft') | Q(status = 'deleted'))
        serialized = self.serializer_class(reqs, many=True)
        return Response(serialized.data)
    
class one_cons_period(APIView):
    model = cons_period
    serializer_class = requestDetailSerial

    def get(self, request, pk, format = None): #получение одной зявки
        req = get_object_or_404(self.model, pk=pk)
        serialised = self.serializer_class(req)
        return Response(serialised.data)
    
    @swagger_auto_schema(request_body=serializer_class)
    def put(self, request, pk, format = None): #изменение заявки (поля)
        req = get_object_or_404(self.model, pk=pk)
        serialized = self.serializer_class(req, data=request.data, partial=True)
        if serialized.is_valid():
            serialized.save()
            return Response(serialized.data, status=status.HTTP_202_ACCEPTED)
        return Response(serialized.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk, format = None): #удаление заявки
        req = get_object_or_404(self.model, pk=pk)
        req.status = 'deleted'
        req.save()
        return Response(self.serializer_class(req).data)

@swagger_auto_schema(method='put', request_body=requestDetailSerial)    
@api_view(['put'])
def save_by_creator(request, pk, format=None): #сохранение заявки
    req = get_object_or_404(cons_period, pk=pk)
    serialized = requestDetailSerial(req)
    if req.dateStart is not None and req.dateEnd is not None and req.constellation is not None:
        req.dateSaved = datetime.date.today().isoformat()
        req.status = 'saved'
        req.save()
        return Response(serialized.data, status=status.HTTP_200_OK)
    return Response({'error': 'some required field(s) was not declared'}, status=status.HTTP_400_BAD_REQUEST)

class moderateByCreator(APIView):
    serializer_class= requestDetailSerial

    @swagger_auto_schema(request_body=serializer_class)
    @method_permission_classes((IsManager,))
    def put(self, request, pk, format=None): #модерирование заявки (расчет поля isNew)
        isAccepted = request.data.get('isAccepted')
        req = get_object_or_404(cons_period, pk=pk)
        if req.dateStart == '' or req.dateEnd == '' or req.constellation == '' or req.status != 'saved':
            return Response({'error': 'This request didn`t saved or have some incompete fields'}, status=status.HTTP_400_BAD_REQUEST)
        req.isAccepted = isAccepted
        if isAccepted:
            req.status = 'accepted'
        else:
            req.status = 'cancelled'
        planets_in_this_req = planet.objects.filter(mm__reqID = req)

        for one_planet in planets_in_this_req:
            result = mm.objects.get(planetID = one_planet, reqID = req)
            last_approved_period = cons_period.objects.filter(
                status='accepted',
                mm__planetID=one_planet
                ).order_by('-dateEnd').first()
            if not last_approved_period:
                result.isNew = True
            elif last_approved_period.dateEnd < req.dateEnd and last_approved_period.constellation != req.constellation:
                result.isNew = True
            else:
                result.isNew = False
            result.save()

        req.dateModerated = datetime.date.today().isoformat()
        req.moderID = getUserBySession(request)
        req.save()

        serialized = requestDetailSerial(req)
        return Response(serialized.data, status=status.HTTP_202_ACCEPTED)

class MMMethods(APIView):
    model = mm
    serializer_class = MMwithPlanetSerial

    def delete(self, requset, pk_planet, pk_req, format = None): #удаление из заявки
        mm_obj = get_object_or_404(self.model, planetID = pk_planet, reqID = pk_req)
        mm_obj.delete()
        mm_list = self.model.objects.filter(reqID = pk_req)
        return Response(self.serializer_class(mm_list, many = True).data)
    
    @swagger_auto_schema(request_body=serializer_class)
    @method_permission_classes((IsManager,))
    def put(self, request, pk_planet, pk_req, format = None): #изменение поля isNew
        mm_obj = get_object_or_404(self.model, planetID = pk_planet, reqID = pk_req)
        serialized = self.serializer_class(mm_obj, data=request.data)
        if serialized.is_valid():
            serialized.save()
            mm_list = self.model.objects.filter(reqID = pk_req)
            return Response(self.serializer_class(mm_list, many = True).data, status=status.HTTP_202_ACCEPTED)
        return Response(serialized.errors, status=status.HTTP_400_BAD_REQUEST)
    
class userReg(APIView):
    model = get_user_model()
    serializer_class = userSerial

    @swagger_auto_schema(request_body=serializer_class)
    def post(self, request, format = None): #регистрация
        serialized = self.serializer_class(data=request.data)
        if self.model.objects.filter(username=request.data['username']).exists():
            return Response({'status': 'arleady exists'}, status=status.HTTP_400_BAD_REQUEST)
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

class userProfile(APIView):
    model = get_user_model()
    serializer_class = userSerial

    @swagger_auto_schema(request_body=serializer_class)
    @method_permission_classes((IsAdmin,))
    def put(self, request, pk, format = None): #личный кабинет
        user1 = get_object_or_404(self.model, pk = pk)
        serialized = self.serializer_class(user1, data=request.data, partial = True)
        if serialized.is_valid():
            serialized.save()
            if 'password' in serialized.validated_data:
                user1.set_password(serialized.validated_data.get('password'))
                user1.save()
            return Response(serialized.data, status=status.HTTP_202_ACCEPTED)
        return Response(serialized.errors, status=status.HTTP_400_BAD_REQUEST)

class userLogin(APIView):
    model = get_user_model()
    serializer_class = userSerial
    permission_classes = [AllowAny]
    authentication_classes = []

    @swagger_auto_schema(request_body=serializer_class)
    def post(self, request, format = None): #аутентификация
        username = request.data["username"] 
        password = request.data["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            random_key = str(uuid.uuid4())
            session_storage.set(random_key, username)

            old_ssid = request.COOKIES.get('session_id', '')
            if old_ssid:
                if session_storage.get(old_ssid):
                    session_storage.delete(old_ssid)

            response = HttpResponse("{'status': 'ok'}")
            response.set_cookie("session_id", random_key)

            return response
        else:
            return HttpResponse("{'status': 'error', 'error': 'login failed'}")

class userLogout(APIView):
    model = get_user_model()
    serializer_class = userSerial

    @method_permission_classes((IsAuth,))
    def post(self, request, format = None): #деваторизация
        ssid = request.COOKIES.get('session_id')
        session_storage.delete(ssid)
        return Response({'status': 'logged out'}, status=status.HTTP_401_UNAUTHORIZED)

