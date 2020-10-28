from django.test import TestCase, Client
import json
from .models import Article, Comment
from django.contrib.auth.models import User


class BlogTestCase(TestCase):
    def setUp(self):
        client = Client()

        response = client.get('/api/token/')
        csrftoken = response.cookies['csrftoken'].value  # Get csrf token from cookie

        # This user is always signed up.
        response = client.post('/api/signup/', json.dumps({'username': 'user', 'password': 'pw'}),
                               content_type='application/json', HTTP_X_CSRFTOKEN=csrftoken)
    

    def test_csrf(self):
        # By default, csrf checks are disabled in test client
        # To test csrf protection we enforce csrf checks here
        client = Client(enforce_csrf_checks=True)
        response = client.post('/api/signup/', json.dumps({'username': 'chris', 'password': 'chris'}),
                               content_type='application/json')
        self.assertEqual(response.status_code, 403)  # Request without csrf token returns 403 response

        response = client.get('/api/token/')
        csrftoken = response.cookies['csrftoken'].value  # Get csrf token from cookie

        response = client.post('/api/signup/', json.dumps({'username': 'chris', 'password': 'chris'}),
                               content_type='application/json', HTTP_X_CSRFTOKEN=csrftoken)
        self.assertEqual(response.status_code, 201)  # Pass csrf protection


    def test_signup(self):
        client = Client()
        
        response = client.get('/api/token/')
        csrftoken = response.cookies['csrftoken'].value  # Get csrf token from cookie
        
        response = client.post('/api/signup/', json.dumps({'username': 'newuser', 'password': 'newpw'}),
                               content_type='application/json', HTTP_X_CSRFTOKEN=csrftoken)
        self.assertEqual(response.status_code, 201)
        response = client.get('/api/signup/')
        self.assertEqual(response.status_code, 405)


    def test_signin(self):
        client = Client()

        response = client.get('/api/token/')
        csrftoken = response.cookies['csrftoken'].value  # Get csrf token from cookie

        response = client.post('/api/signin/', json.dumps({'username': 'user', 'password': 'pw'}),
                               content_type='application/json', HTTP_X_CSRFTOKEN=csrftoken)
        self.assertEqual(response.status_code, 204)

        response = client.post('/api/signin/', json.dumps({'username': 'fail', 'password': 'fail'}),
                               content_type='application/json', HTTP_X_CSRFTOKEN=csrftoken)
        self.assertEqual(response.status_code, 401)

        response = client.get('/api/signin/')
        self.assertEqual(response.status_code, 405)


    def test_signout(self):
        client = Client()

        response = client.get('/api/token/')
        csrftoken = response.cookies['csrftoken'].value  # Get csrf token from cookie

        response = client.get('/api/signout/')
        self.assertEqual(response.status_code, 401)

        response = client.post('/api/signin/', json.dumps({'username': 'user', 'password': 'pw'}),
                               content_type='application/json', HTTP_X_CSRFTOKEN=csrftoken)
        response = client.get('/api/signout/')
        self.assertEqual(response.status_code, 204)

        response = client.post('/api/signout/', json.dumps({'username': 'chris', 'password': 'chris2'}),
                               content_type='application/json', HTTP_X_CSRFTOKEN=csrftoken)
        self.assertEqual(response.status_code, 405)


    def test_article(self):
        client = Client()

        response = client.get('/api/token/')
        csrftoken = response.cookies['csrftoken'].value  # Get csrf token from cookie

        response = client.put('/api/article/', json.dumps({'username': 'user', 'password': 'pw'}),
                               content_type='application/json', HTTP_X_CSRFTOKEN=csrftoken)
        self.assertEqual(response.status_code, 405)

        response = client.get('/api/article/')
        self.assertEqual(response.status_code, 401)

        author = User.objects.create_user(username='username', password='password') 
        article = Article(id=1, title='title', content='content', author=author)
        article.save()
        response = client.post('/api/signin/', json.dumps({'username': 'user', 'password': 'pw'}),
                               content_type='application/json', HTTP_X_CSRFTOKEN=csrftoken)
        response = client.get('/api/article/')
        self.assertEqual(response.status_code, 200)
        response = client.post('/api/article/', json.dumps({'title': 'user', 'content': 'pw'}),
                               content_type='application/json', HTTP_X_CSRFTOKEN=csrftoken)
        self.assertEqual(response.status_code, 201)

        response = client.get('/api/article/')
        self.assertEqual(response.status_code, 200)

        response = client.put('/api/article/', json.dumps({'username': 'user', 'password': 'pw'}),
                               content_type='application/json', HTTP_X_CSRFTOKEN=csrftoken)
        self.assertEqual(response.status_code, 405)


    def test_article_id(self):
        client = Client()

        response = client.get('/api/token/')
        csrftoken = response.cookies['csrftoken'].value  # Get csrf token from cookie

        response = client.post('/api/article/1/', json.dumps({'username': 'user', 'password': 'pw'}),
                               content_type='application/json', HTTP_X_CSRFTOKEN=csrftoken)
        self.assertEqual(response.status_code, 405)

        response = client.get('/api/article/1/')
        self.assertEqual(response.status_code, 401)

        response = client.post('/api/signin/', json.dumps({'username': 'user', 'password': 'pw'}),
                               content_type='application/json', HTTP_X_CSRFTOKEN=csrftoken)
        response = client.get('/api/article/1/')
        self.assertEqual(response.status_code, 404)

        author = User.objects.create_user(username='username', password='password') 
        article = Article(id=1, title='title', content='content', author=author)
        article.save()
        response = client.get('/api/article/1/')
        self.assertEqual(response.status_code, 200)

        response = client.put('/api/article/1/', json.dumps({'title': 'user', 'content': 'pw'}),
                               content_type='application/json', HTTP_X_CSRFTOKEN=csrftoken)
        self.assertEqual(response.status_code, 403)

        response = client.post('/api/signin/', json.dumps({'username': 'username', 'password': 'password'}),
                               content_type='application/json', HTTP_X_CSRFTOKEN=csrftoken)
        response = client.put('/api/article/1/', json.dumps({'title': 'user', 'content': 'pw'}),
                               content_type='application/json', HTTP_X_CSRFTOKEN=csrftoken)
        self.assertEqual(response.status_code, 200)
        
        response = client.delete('/api/article/1/')
        self.assertEqual(response.status_code, 200)

        response = client.get('/api/article/1/')
        self.assertEqual(response.status_code, 404)


    def test_article_id_comment(self):
        client = Client()

        response = client.get('/api/token/')
        csrftoken = response.cookies['csrftoken'].value  # Get csrf token from cookie

        response = client.put('/api/article/1/comment/', json.dumps({'title': 'user', 'content': 'pw'}),
                               content_type='application/json', HTTP_X_CSRFTOKEN=csrftoken)
        self.assertEqual(response.status_code, 405)

        response = client.get('/api/article/1/comment/')
        self.assertEqual(response.status_code, 401)

        response = client.post('/api/signin/', json.dumps({'username': 'user', 'password': 'pw'}),
                               content_type='application/json', HTTP_X_CSRFTOKEN=csrftoken)
        response = client.get('/api/article/1/comment/')
        self.assertEqual(response.status_code, 404)

        author = User.objects.create_user(username='username', password='password') 
        article = Article(id=1, title='title', content='content', author=author)
        article.save()
        article2 = Article(id=2, title='title', content='content', author=author)
        article2.save()
        comment = Comment(id=1, article=article, content='kaka' , author=author)
        comment2 = Comment(id=2, article=article2, content='kaka' , author=author)
        comment.save()
        comment2.save()
        response = client.get('/api/article/1/comment/')
        self.assertEqual(response.status_code, 200)
        
        response = client.post('/api/article/1/comment/', json.dumps({'content': 'user', 'password': 'pw'}),
                               content_type='application/json', HTTP_X_CSRFTOKEN=csrftoken)
        self.assertEqual(response.status_code, 201)

        response = client.get('/api/article/1/comment/')
        self.assertEqual(response.status_code, 200)


    def test_comment_id(self):
        client = Client()

        response = client.get('/api/token/')
        csrftoken = response.cookies['csrftoken'].value  # Get csrf token from cookie

        response = client.post('/api/comment/1/', json.dumps({'username': 'user', 'password': 'pw'}),
                               content_type='application/json', HTTP_X_CSRFTOKEN=csrftoken)
        self.assertEqual(response.status_code, 405)

        response = client.get('/api/comment/1/')
        self.assertEqual(response.status_code, 401)

        response = client.post('/api/signin/', json.dumps({'username': 'user', 'password': 'pw'}),
                               content_type='application/json', HTTP_X_CSRFTOKEN=csrftoken)
        response = client.get('/api/comment/1/')
        self.assertEqual(response.status_code, 404)


        author = User.objects.create_user(username='username', password='password') 
        article = Article(id=1, title='title', content='content', author=author)
        article.save()
        comment = Comment(id=1, article=article, content='kaka' , author=author)
        comment.save()
        response = client.get('/api/comment/1/')
        self.assertEqual(response.status_code, 200)

        response = client.put('/api/comment/1/', json.dumps({'content': 'user', 'password': 'pw'}),
                               content_type='application/json', HTTP_X_CSRFTOKEN=csrftoken)
        self.assertEqual(response.status_code, 403)

        response = client.post('/api/signin/', json.dumps({'username': 'username', 'password': 'password'}),
                               content_type='application/json', HTTP_X_CSRFTOKEN=csrftoken)
        response = client.put('/api/comment/1/', json.dumps({'content': 'user', 'password': 'pw'}),
                               content_type='application/json', HTTP_X_CSRFTOKEN=csrftoken)
        self.assertEqual(response.status_code, 200)

        response = client.delete('/api/comment/1/')
        self.assertEqual(response.status_code, 200)

    
    def test_token(self):
        client = Client()

        response = client.delete('/api/token/')
        self.assertEqual(response.status_code, 405)

        response = client.get('/api/token/')
        self.assertEqual(response.status_code, 204)

        

        
        






