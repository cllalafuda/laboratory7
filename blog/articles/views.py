from django.contrib.auth import authenticate, login as django_login
from django.contrib.auth.models import User
from django.shortcuts import redirect, render
from django.http import Http404

from .models import Article


def archive(request):
    return render(request, "archive.html", {"posts": Article.objects.all()})


def get_article(request, article_id):
    try:
        post = Article.objects.get(id=article_id)
        return render(request, "article.html", {"post": post})
    except Article.DoesNotExist:
        raise Http404


def create_post(request):
    if request.user.is_anonymous:
        raise Http404

    if request.method == "GET":
        return render(request, "create_post.html", {})

    form = {"text": request.POST["text"], "title": request.POST["title"]}

    if not (form["text"] and form["title"]):
        form["errors"] = "Не все поля заполнены"
        return render(request, "create_post.html", {"form": form})

    if Article.objects.filter(title=form["title"]).exists():
        form["errors"] = "Статья с таким заголовком существует"
        return render(request, "create_post.html", context={"form": form})

    user = request.user
    
    article = Article.objects.create(
        text=form["text"], title=form["title"], author=user
    )
    return redirect("get_article", article_id=article.id)


def registrate_user(request):
    if request.method == "GET":
        return render(request, "registrate_user.html", {})

    form = {"login": request.POST["login"], "password": request.POST["password"]}
    login = request.POST["login"]
    password = request.POST["password"]    

    if not (login and password):
        form["errors"] = "Не все поля заполнены"
        return render(request, "registrate_user.html", {"form": form})

    if User.objects.filter(username=login).first():
        form["errors"] = "Такой пользователь существует"
        return render(request, "registrate_user.html", {"form": form})
    
    user = User.objects.create_user(username=login, password=password)

    return redirect("/")


def authorize_user(request):
    if request.method == "GET":
        return render(request, "authorize_user.html", {})

    form = {"login": request.POST["login"], "password": request.POST["password"]}
    login = request.POST["login"]
    password = request.POST["password"]    

    if not (login and password):
        form["errors"] = "Не все поля заполнены"
        return render(request, "authorize_user.html", {"form": form})

    user = authenticate(username=login, password=password)
    
    if not user:
        form["errors"] = "Такого пользователя не существует"
        return render(request, "authorize_user.html", {"form": form})

    django_login(request, user)

    return redirect("/")
