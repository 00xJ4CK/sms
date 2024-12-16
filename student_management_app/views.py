import json

import requests
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse

from student_management_app.EmailBackEnd import EmailBackEnd

# Create yours views here.


def ShowLoginPage(request):
    return render(request, "login_page.html")


def doLogin(request, **kwargs):
    if request.method != "POST":
        return HttpResponse("<h4>Denied</h4>")
    else:
        # Google recaptcha
        captcha_token = request.POST.get("g-recaptcha-response")
        captcha_url = "https://www.google.com/recaptcha/api/siteverify"
        captcha_key = "6LfTGD4qAAAAALtlli02bIM2MGi_V0cUYrmzGEGd"
        data = {"secret": captcha_key, "response": captcha_token}
        # Make request
        try:
            captcha_server = requests.post(url=captcha_url, data=data)
            response = json.loads(captcha_server.text)
            if response["success"] == False:
                messages.error(request, "Invalid Captcha. Try Again")
                return redirect("/")
        except:
            messages.error(request, "Captcha could not be verified. Try Again")
            return redirect("/")

        # Authenticate
        user = EmailBackEnd.authenticate(
            request,
            username=request.POST.get("email"),
            password=request.POST.get("password"),
        )
        if user != None:
            login(request, user)
            if user.user_type == "1":
                return redirect(reverse("admin_home"))
            elif user.user_type == "2":
                return redirect(reverse("staff_home"))
            else:
                return redirect(reverse("student_home"))
        else:
            messages.error(request, "Invalid details")
            return redirect("/")


def GetUserDetails(request):
    if request.user is not None:
        return HttpResponse(
            "User : "
            + request.user.email
            + " usertype : "
            + str(request.user.user_type)
        )
    else:
        return HttpResponse("Please Login First")


def logout_user(request):
    logout(request)
    return HttpResponseRedirect("/")


def showFirebaseJS(request):
    data = (
        'importScripts("https://www.gstatic.com/firebasejs/7.14.6/firebase-app.js");'
        'importScripts("https://www.gstatic.com/firebasejs/7.14.6/firebase-messaging.js"); '
        "var firebaseConfig = {"
        '        apiKey: "YOUR_API_KEY",'
        '        authDomain: "FIREBASE_AUTH_URL",'
        '        databaseURL: "FIREBASE_DATABASE_URL",'
        '        projectId: "FIREBASE_PROJECT_ID",'
        '        storageBucket: "FIREBASE_STORAGE_BUCKET_URL",'
        '        messagingSenderId: "FIREBASE_SENDER_ID",'
        '        appId: "FIREBASE_APP_ID",'
        '        measurementId: "FIREBASE_MEASUREMENT_ID"'
        " };"
        "firebase.initializeApp(firebaseConfig);"
        "const messaging=firebase.messaging();"
        "messaging.setBackgroundMessageHandler(function (payload) {"
        "    console.log(payload);"
        "    const notification=JSON.parse(payload);"
        "    const notificationOption={"
        "        body:notification.body,"
        "        icon:notification.icon"
        "    };"
        "    return self.registration.showNotification(payload.notification.title,notificationOption);"
        "});"
    )

    return HttpResponse(data, content_type="text/javascript")
