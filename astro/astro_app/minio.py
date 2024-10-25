from django.conf import settings
from minio import Minio
from django.core.files.uploadedfile import InMemoryUploadedFile
from rest_framework.response import *

def process_file_upload(file_object: InMemoryUploadedFile, client, image_name):
    try:
        client.put_object('images', image_name, file_object, file_object.size)
        return f'http://localhost:9000/images/{image_name}'
    except Exception as e:
        return {'error': str(e)}
    
def process_file_delete(client, image_name):
    try:
        client.remove_object('images', image_name)
        return {'status': 'success'}
    except Exception as e:
        return {'error': str(e)}

def add_pic(new_planet, pic):
    client = Minio(
        endpoint = settings.AWS_S3_ENDPOINT_URL,
        access_key = settings.AWS_ACCESS_KEY_ID,
        secret_key = settings.AWS_SECRET_ACCESS_KEY,
        secure = settings.MINIO_USE_SSL
    )
    i = new_planet.pk
    image_name = f'{i}.png'
    if pic == None:
        return Response({'error': f'No image file given for pic'})
    result = process_file_upload(pic, client, image_name)

    if 'error' in result:
        return Response(result)
    
    new_planet.img = result
    new_planet.save()
    return Response({'status': 'success'})

def del_pic(planet):
    client = Minio(
        endpoint = settings.AWS_S3_ENDPOINT_URL,
        access_key = settings.AWS_ACCESS_KEY_ID,
        secret_key = settings.AWS_SECRET_ACCESS_KEY,
        secure = settings.MINIO_USE_SSL
    )

    url = planet.img
    if url:
        url = '/'.join(url.split('/')[4:])

        res = process_file_delete(client, url)
        if 'error' in res:
            return Response(res)
    
    return Response({'status': 'success'})
