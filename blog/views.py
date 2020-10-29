from django.http import HttpResponse, HttpResponseNotAllowed, JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.views.decorators.csrf import ensure_csrf_cookie
# from django.views.decorators.csrf import csrf_exempt # for debugging
import json
from .models import Article, Comment

# global check: 405, 401, 404, 403
# For all non-allowed requests (X marked in the API table), response with 405 (and any information must not be modified).
# For all requests about article and comment without signing in, response with 401 (and any information must not be modified).
# For all requests about non-existing article and comment, response with 404 (and any information must not be modified).
# For all PUT and DELETE requests from non-author, response with 403 (and any information must not be modified).

##@csrf_exempt
def signup(request):
    if request.method == 'POST':
        req_data = json.loads(request.body.decode())
        username = req_data['username']
        password = req_data['password']
        User.objects.create_user(username=username, password=password)
        response_dict = {'username': username, 'password': password}
        return JsonResponse(response_dict, status=201)
    else:
        return HttpResponse(status=405)


##@csrf_exempt
def signin(request):
    if request.method == 'POST':
        req_data = json.loads(request.body.decode())
        username = req_data['username']
        password = req_data['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            response_dict = {'username': username, 'password': password}
            return JsonResponse(response_dict, status=204)
        else:
            return HttpResponse(status=401)
    else:
        return HttpResponse(status=405)


##@csrf_exempt
def signout(request):
    if request.method == 'GET':
        if request.user.is_authenticated:
            logout(request)
            return HttpResponse(status=204)
        else:
            return HttpResponse(status=401)
    else:
        return HttpResponse(status=405)


##@csrf_exempt
def article(request):
    if not request.method == 'GET' and not request.method == 'POST':
        return HttpResponse(status=405)
    if not request.user.is_authenticated:
        return HttpResponse(status=401)
    if request.method == 'GET':
        article_list = [article for article in Article.objects.all().values()]
        
        for article in article_list:
            article['author'] = article.pop('author_id')
            
        return JsonResponse(article_list, safe=False)
    else: # if request.method == 'POST':
        req_data = json.loads(request.body.decode())
        title = req_data['title']
        content = req_data['content']
        author = request.user

        article = Article(title=title, content=content, author=author)
        article.save()

        response_dict = {'title': title, 'content' : content, 'id': article.id}
        return JsonResponse(response_dict, status=201)


##@csrf_exempt
def article_id(request, article_id=0):
    if not request.method == 'GET' and not request.method == 'PUT' and not request.method == 'DELETE':
        return HttpResponse(status=405)
    if not request.user.is_authenticated:
        return HttpResponse(status=401)
    try:
        article = Article.objects.get(id=article_id)
    except Article.DoesNotExist as e:
        return HttpResponse(status=404)
    if request.method == 'GET':
        response_dict = {'title': article.title, 'content': article.content, 'author': article.author.id} 
        return JsonResponse(response_dict)
    if article.author.id != request.user.id:
        return HttpResponse(status=403)
    if request.method == 'PUT':
        req_data = json.loads(request.body.decode())
        title = req_data['title']
        content = req_data['content']

        article.title = title
        article.content = content
        article.save()
        response_dict = {'title': article.title, 'content': article.content, 'id': article.id} 
        return JsonResponse(response_dict, status=200)
    else: # if request.method == 'DELETE':
        article.delete()
        return HttpResponse(status=200)



##@csrf_exempt
def article_id_comment(request, article_id=0):
    if not request.method == 'GET' and not request.method == 'POST':
        return HttpResponse(status=405)
    if not request.user.is_authenticated:
        return HttpResponse(status=401)
    try:
        article = Article.objects.get(id=article_id)
    except Article.DoesNotExist as e:
        return HttpResponse(status=404)
    if request.method == 'GET':
        
        all_comment_list = [comment for comment in Comment.objects.all().values()]
        
        wanted_comment_list = []
        for comment in all_comment_list:
            if comment['article_id'] == article_id:
                comment['article'] = comment.pop('article_id')
                comment['content'] = comment.pop('content')
                comment['author'] = comment.pop('author_id')
                wanted_comment_list.append(comment)

        return JsonResponse(wanted_comment_list, safe=False)
    else: # if request.method == 'POST':
        req_data = json.loads(request.body.decode())
        content = req_data['content']
        author = request.user

        comment = Comment(article=article, content=content , author=author)
        comment.save()

        response_dict = {'content': content, 'id': comment.id}
        return JsonResponse(response_dict, status=201)        



##@csrf_exempt
def comment_id(request, comment_id=0):
    if not request.method == 'GET' and not request.method == 'PUT' and not request.method == 'DELETE':
        return HttpResponse(status=405)
    if not request.user.is_authenticated:
        return HttpResponse(status=401)
    try:
        comment = Comment.objects.get(id=comment_id)
    except Comment.DoesNotExist as e:
        return HttpResponse(status=404)
    if request.method == 'GET':
        response_dict = {'article': comment.article.id ,'content': comment.content, 'author': comment.author.id }
        return JsonResponse(response_dict)
    if comment.author.id != request.user.id:
        return HttpResponse(status=403)
    if request.method == 'PUT':
        req_data = json.loads(request.body.decode())
        content = req_data['content']
        comment.content = content
        comment.save()
        response_dict = {'content': content, 'id': comment.id}
        return JsonResponse(response_dict, status=200)
    else: # if request.method == 'DELETE':
        comment.delete()
        return HttpResponse(status=200)
    

@ensure_csrf_cookie
def token(request):
    if request.method == 'GET':
        return HttpResponse(status=204)
    else:
        return HttpResponseNotAllowed(['GET'])
