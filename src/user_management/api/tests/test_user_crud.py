import os
import uuid

from api.models import CustomUser
from api.models import UPLOAD_TO_PROFILE
from django.conf import settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from test_setup import MyTestSetUp
from utils_jwt import generate_token

UNDER_ONE_MB = "default/900kb.jpg"
AROUND_ONE_MB = "default/1mb.jpg"
OVER_ONE_MB = "default/1.8mb.jpg"

NEW_NAME = "NewName"


class TestCrud(MyTestSetUp):
    def setUp(self):
        self.user_id = str(uuid.uuid4())
        self.fake_user_id = str(uuid.uuid4())
        self.displayname = "Test API"
        self.data = {
            "displayname": self.displayname,
        }
        self.url = reverse("user-creation")
        self.url_profile = reverse("profile")

        self.headers = {
            # "HTTP_AUTHORIZATION": f"Bearer {self.access_token}",
        }

        self.setup_jwt_with_cookie(self.user_id)

        self.images = {
            "900kb": os.path.join(settings.MEDIA_ROOT, UPLOAD_TO_PROFILE, UNDER_ONE_MB),
            "1mb": os.path.join(settings.MEDIA_ROOT, UPLOAD_TO_PROFILE, AROUND_ONE_MB),
            "1.8mb": os.path.join(settings.MEDIA_ROOT, UPLOAD_TO_PROFILE, OVER_ONE_MB),
        }

    def post(self):
        return self.client.post(self.url, self.data, format="json", secure=True, **self.headers)

    def delete(self):
        return self.client.delete(self.url_profile, secure=True, **self.headers)

    def patch(self, request, displayname):
        return self.client.patch(self.url_profile, format="json", secure=True, **self.headers)

    ### TEST Profile creation ###
    def test_no_displayname(self):
        del self.data["displayname"]
        response = self.post()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # print(response.data)

    def test_displayname_too_long(self):
        self.data["displayname"] = "displayname too long ggggggggggggggggggggggggggg"
        response = self.post()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # print(response.data)

    def test_no_data(self):
        self.data = {}
        response = self.post()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_duplicate(self):
        response = self.post()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response = self.post()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(CustomUser.objects.count(), 1)
        # print(response.data)

    # Succesful api call
    def test_success(self):
        # print(f"q: uuid: {self.user_id}, data.user_id {self.data["user_id"]}")
        response = self.post()
        # print(f"q: RESPONSE: {response.data}")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(CustomUser.objects.count(), 1)
        self.assertEqual(CustomUser.objects.get().displayname, self.displayname)
        self.assertEqual(str(CustomUser.objects.get().user_id), self.user_id)

    # This test is redundant, learned that the serializer just checks if all required fields are present
    def test_additional_unrequired_data(self):
        self.data["iser_id"] = "unrequired_data"
        response = self.post()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    

    ### Test Profile get - /profile GET ###
    def test_successful_get(self):
        self.test_success()
        response = self.client.get(self.url_profile, format="json", secure=True, **self.headers)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), {"displayname": self.displayname, "image": '/um/media/images/profile/default/default_avatar.png'})

    def test_invalid_jwt_get(self):
        self.test_success()
        self.setup_jwt_with_cookie(self.fake_user_id)
        response = self.client.get(self.url_profile, format="json", secure=True, **self.headers)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.setup_jwt_with_cookie(self.user_id) # set jwt back to the correct user


    ### Test Editing Profile ###
    def test_editing_profile_name(self):
        self.test_success()
        self.data['displayname'] = NEW_NAME
        response = self.client.patch(self.url_profile, self.data, format='multipart', secure=True, **self.headers)
        print(response.json())
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(CustomUser.objects.filter(displayname=NEW_NAME).count(), 1)
        self.assertEqual(CustomUser.objects.filter(displayname=self.displayname).count(), 0)

    def test_editing_profile_img(self):
        self.test_success()
        with open(self.images["900kb"], 'rb') as image:
            self.data['image'] = image
            response = self.client.patch(self.url_profile, self.data, format='multipart', secure=True, **self.headers)
            image_path = CustomUser.objects.get().image.path

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(os.path.exists(image_path))

        # delete the image after the test
        self.delete()

    def test_editing_profile_img_twice(self):
        self.test_success()

        with open(self.images["900kb"], 'rb') as image:
            self.data['image'] = image
            response = self.client.patch(self.url_profile, self.data, format='multipart', secure=True, **self.headers)
            old_image_path = CustomUser.objects.get().image.path

        with open(self.images["1mb"], 'rb') as image:
            self.data['image'] = image
            response = self.client.patch(self.url_profile, self.data, format='multipart', secure=True, **self.headers)
            image_path = CustomUser.objects.get().image.path

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(os.path.exists(image_path))
        self.assertFalse(os.path.exists(old_image_path))
        self.delete()

    def test_editing_profile_img_too_big(self):
        self.test_success()
        with open(self.images["1.8mb"], 'rb') as image:
            self.data['image'] = image
            response = self.client.patch(self.url_profile, self.data, format='multipart', secure=True, **self.headers)
            response_json = response.json()
            default_image_path = CustomUser.objects.get().image.path

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response_json, {'image': ['Max file size is 1MB']})
        self.assertTrue(os.path.exists(default_image_path))

    def test_editing_profile_img_and_data(self):
        self.test_success()

        self.data['displayname'] = NEW_NAME

        with open(self.images["900kb"], 'rb') as image:
            self.data['image'] = image
            response = self.client.patch(self.url_profile, self.data, format='multipart', secure=True, **self.headers)

        # user = CustomUser.objects.get()
        # image_path = user.image.path
        # print(image_path)
        # response_json = response.json()
        print(response.json())
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(CustomUser.objects.all().count(), 1)
        self.assertEqual(CustomUser.objects.filter(displayname=self.data['displayname']).count(), 1)

        # delete the image after the test
        self.delete()

    ### Test profile deletion ###
    def test_user_deletion_with_default_image(self):
        self.test_success()

        default_image_path = CustomUser.objects.get().image.path

        response = self.delete()

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertTrue(os.path.exists(default_image_path))  # default image should not be deleted

    def test_user_deletion_with_custom_image(self):
        self.test_success()
        with open(self.images["900kb"], 'rb') as image:
            self.data['image'] = image
            response = self.client.patch(self.url_profile, self.data, format='multipart', secure=True, **self.headers)

        image_path = CustomUser.objects.get().image.path
        self.assertTrue(os.path.exists(image_path))

        response = self.delete()

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(os.path.exists(image_path))


# def test_no_uid(self):
#     del self.data["user_id"]  # This will remove the key "user_id" and its value from self.data
#     response = self.post()
#     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

# redundant since no user_id already tested
# def test_wrong_key_name(self):
#     del self.data["user_id"]
#     self.data["iser_id"] = self.user_id
#     response = self.post()
#     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

# def test_invalid_uid(self):
#     self.data["user_id"] = "invalid user id"
#     response = self.post()
#     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#     # print(response.data)
