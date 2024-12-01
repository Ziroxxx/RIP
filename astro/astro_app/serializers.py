from .models import planet, mm, cons_period, AuthUser
from rest_framework import serializers
from collections import OrderedDict

class planetSerial(serializers.ModelSerializer):
    class Meta:
        model = planet
        fields = '__all__'

    def get_fields(self):
            new_fields = OrderedDict()
            for name, field in super().get_fields().items():
                field.required = False
                new_fields[name] = field
            return new_fields
    
class planetsSerial(serializers.Serializer):
     planets = planetSerial(many=True)
     wishID = serializers.CharField()
     wishCount = serializers.IntegerField()

class planetNameSerializer(serializers.Serializer):
     PlanetName = serializers.CharField()

class userSerial(serializers.ModelSerializer):
    class Meta:
        model = AuthUser
        fields = '__all__'

    def get_fields(self):
        new_fields = OrderedDict()
        for name, field in super().get_fields().items():
            field.required = False
            new_fields[name] = field
        return new_fields

class loginSeraial(serializers.Serializer):
     status = serializers.CharField()

class requestSerial(serializers.ModelSerializer):
    userID = serializers.StringRelatedField()
    moderID = serializers.StringRelatedField()

    class Meta:
        model = cons_period
        fields = '__all__'

    def get_fields(self):
            new_fields = OrderedDict()
            for name, field in super().get_fields().items():
                field.required = False
                new_fields[name] = field
            return new_fields 

class MMwithPlanetSerial(serializers.ModelSerializer):
    planetID = planetSerial(read_only = True)

    class Meta:
        model = mm
        fields = ['planetID', 'isNew']
    
    def get_fields(self):
            new_fields = OrderedDict()
            for name, field in super().get_fields().items():
                field.required = False
                new_fields[name] = field
            return new_fields 

class requestDetailSerial(serializers.ModelSerializer):
    planets = MMwithPlanetSerial(source = 'mm_set', many = True, read_only = True)
    userID = serializers.StringRelatedField(read_only = True)
    moderID = serializers.StringRelatedField()

    def validate(self, attrs):
        attrs = super().validate(attrs)
        if 'dateStart' in attrs and 'dateEnd' in attrs and not attrs['dateStart'] is None  and not attrs['dateEnd'] is None:
            if  attrs['dateStart'] > attrs['dateEnd']:
                raise serializers.ValidationError('dateStart must be earlier then dateEnd')
        return attrs

    class Meta:
        model = cons_period
        fields = ['reqID', 'dateCreated', 'dateSaved', 'dateModerated',  
                  'status','dateStart', 'dateEnd', 'constellation', 'planets', 'userID', 'moderID']
        
    def get_fields(self):
            new_fields = OrderedDict()
            for name, field in super().get_fields().items():
                field.required = False
                new_fields[name] = field
            return new_fields 