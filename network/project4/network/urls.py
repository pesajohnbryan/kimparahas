
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path("", views.index, name="index"),

    #authentication urls
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),

    #profile url
    path("profile/<str:username>/", views.profile, name="profile"),

    #create_post url
    path("create", views.create_post, name="create-post"),

    #search url
    path('search/', views.search, name='search'),

    #following urls
    path('following', views.following, name="following"),
    path('follow/<int:user_id>/', views.follow_user, name='follow_user'),

    #like url
    path('post/<int:post_id>/like/', views.toggle_like, name='toggle_like'),

    #repost url
    path('post/<int:post_id>/repost/', views.repost, name='repost'),

    #comment urls
    path('post/<int:post_id>/comments/', views.get_comments, name='get_comments'),
    path('post/<int:post_id>/add_comment/', views.add_comment, name='add_comment'),

    #dropwdown urls
    path('post/<int:edit_id>/edit/', views.edit_post, name='edit_post'),
    path('post/<int:post_id>/delete/', views.delete_post, name='delete_post'),
    
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)