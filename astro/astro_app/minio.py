from django.conf import settings
from minio import Minio
from django.core.files.uploadedfile import InMemoryUploadedFile
from rest_framework.response import *

def process_file_upload(file_object: InMemoryUploadedFile, client, image_name, bucket_name):
    try:
        object_name = f"{bucket_name}/{image_name}" if bucket_name != 'images' else image_name
        client.put_object('images', object_name, file_object, file_object.size)
        return f'http://localhost:9000/images/{object_name}'
    except Exception as e:
        return {'error': str(e)}
    
def process_file_delete(client, image_name):
    try:
        client.remove_object('images', image_name)
        return {'status': 'success'}
    except Exception as e:
        return {'error': str(e)}

def add_pic(new_planet, pic, path):
    client = Minio(
        endpoint = settings.AWS_S3_ENDPOINT_URL,
        access_key = settings.AWS_ACCESS_KEY_ID,
        secret_key = settings.AWS_SECRET_ACCESS_KEY,
        secure = settings.MINIO_USE_SSL
    )
    i = new_planet.pk
    image_name = f'{i}.png'
    if pic == None:
        return Response({'error': f'No image file given for {path}'})
    result = process_file_upload(pic, client, image_name, path)

    if 'error' in result:
        return Response(result)
    
    if path == 'images':
        new_planet.img = result
    else:
        new_planet.detImg = result
    new_planet.save()
    return Response({'status': 'success'})

def del_pic(planet):
    client = Minio(
        endpoint = settings.AWS_S3_ENDPOINT_URL,
        access_key = settings.AWS_ACCESS_KEY_ID,
        secret_key = settings.AWS_SECRET_ACCESS_KEY,
        secure = settings.MINIO_USE_SSL
    )

    url1 = planet.img
    url1 = '/'.join(url1.split('/')[4:])

    url2 = planet.detImg
    url2 = '/'.join(url2.split('/')[4:])

    res = process_file_delete(client, url1)
    if 'error' in res:
        return Response(res)
    
    res = process_file_delete(client, url2)
    if 'error' in res:
        return Response(res)
    
    return Response({'status': 'success'})
