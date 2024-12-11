from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from django.contrib import messages
from django.core.paginator import Paginator
import json

from .models import User, Post, Follow, Like, Comment

@login_required
def index(request):
    profile_user = request.user
    posts = Post.objects.all().order_by('-created_at')
    post_count = Post.objects.filter(user=profile_user).count()
    followers_count = profile_user.followers.count() 
    following_count = profile_user.following.count() 
    is_own_profile = request.user == profile_user
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    suggested_users = get_suggested_users(request)

    return render(request, "network/index.html", {
        "users": profile_user,
        "posts": page_obj,
        "suggested_users": suggested_users,
        "post_count": post_count,
        "followers_count": followers_count,
        "following_count": following_count,
        "is_own_profile": is_own_profile,
        "page_obj": page_obj,
    })
@login_required
def toggle_like(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    user = request.user

    if user in post.likes.all():
        post.likes.remove(user)
        is_liked = False
    else:
        post.likes.add(user)
        is_liked = True

    return JsonResponse({
        "success": True,
        "is_liked": is_liked,
        "like_count": post.likes.count()
    })

def repost(request, post_id):
    original_post = get_object_or_404(Post, id=post_id)

    if request.user in original_post.reposts.all():
        # Remove the repost
        original_post.reposts.remove(request.user)
        
        reposted_post = Post.objects.filter(user=request.user, post=original_post.post).first()
        if reposted_post:
            reposted_post.delete()

        return JsonResponse({'success': True, 'action': 'removed'})

    repost = Post.objects.create(
        user=request.user,
        post=original_post.post,
        created_at=original_post.created_at
    )
    original_post.reposts.add(request.user)

    return JsonResponse({
        'success': True,
        'action': 'added',
        'reposted_post_id': repost.id,
    })

@login_required
@csrf_exempt
def add_comment(request, post_id):
    if request.method == "POST":
        try:
            post = Post.objects.get(id=post_id)
            data = json.loads(request.body)
            content = data.get("content")
            if content:
                comment = Comment.objects.create(post=post, user=request.user, content=content)
                return JsonResponse({"success": True, "comment": comment.content, "username": comment.user.username})
            else:
                return JsonResponse({"success": False, "error": "Empty content"}, status=400)
        except Post.DoesNotExist:
            return JsonResponse({"success": False, "error": "Post not found"}, status=404)
    return JsonResponse({"success": False, "error": "Invalid request"}, status=400)

def get_comments(request, post_id):
    try:
        post = Post.objects.get(id=post_id)
        comments = post.comments.all().order_by('-created_at')
        comment_data = [{"username": comment.user.username, "content": comment.content} for comment in comments]
        return JsonResponse({"success": True, "comments": comment_data})
    except Post.DoesNotExist:
        return JsonResponse({"success": False, "error": "Post not found"}, status=404)

def edit_post(request, id):
    post = get_object_or_404(Post, id=id)
    
    if request.method == "POST":
        post.content = request.POST.get("content")
        post.save()
        return redirect('profile', username=post.user.username)
    
    return render(request, 'network/profile.html', {'post': post})

def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == 'POST':
        post.delete()
        return redirect('profile', username=request.user.username)
    
    return JsonResponse({'success': False}, status=400)

def following(request):
    user = request.user
    profile_user = Follow.objects.filter(follower=request.user).values_list('following', flat=True)
    posts = Post.objects.filter(user__in=profile_user).prefetch_related('likes').order_by('-created_at')
    post_count = Post.objects.filter(user__in=profile_user).count()
    followers_count = Follow.objects.filter(following__in=profile_user).count()
    following_count = Follow.objects.filter(follower__in=profile_user).count()
    return render(request, "network/index.html", {
        "user" : user,
        "users": profile_user,
        "posts": posts,
        "post_count": post_count,
        "followers_count": followers_count,
        "following_count": following_count,
    })

def login_view(request):
    if request.method == "POST":

        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        name = request.POST["name"]
        username = request.POST["username"]
        email = request.POST["email"]
        avatar = request.FILES.get("avatar")

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                name=name  
            )

            if avatar:
                user.avatar = avatar
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")

@login_required
def create_post(request):
    if request.method == "POST":
        create_post = request.POST["create-post"]
        username = request.user

        create = Post.objects.create(
            post = create_post,
            user = username,
        )
        create.save()

        return redirect("index")
    return render(request, "network/index.html")

def search(request):
    query = request.GET.get('q', '').strip()

    if query:
        users = User.objects.filter(
            Q(username__icontains=query) | 
            Q(name__icontains=query)
        )

        posts = Post.objects.filter(post__icontains=query)

        user_results = [{'username': user.username, 'name': user.name} for user in users]
        post_results = [{'user': post.user.username, 'content': post.post[:100], 'created_at': post.created_at} for post in posts]

        return JsonResponse({
            'users': user_results,
            'posts': post_results
        })
    else:
        return JsonResponse({
            'users': [],
            'posts': []
        })


def profile(request, username):
    profile_user = get_object_or_404(User, username=username)
    posts = Post.objects.filter(user=profile_user).order_by('-created_at')
    post_count = posts.count()
    followers_count = profile_user.followers.count()  
    following_count = profile_user.following.count() 
    is_own_profile = request.user == profile_user
    follow_exists = Follow.objects.filter(follower=request.user, following=profile_user).exists()

    is_following = False

    if follow_exists:
        is_following = True


    return render(request, "network/profile.html", {
        "profile_user": profile_user,
        "posts": posts,
        "post_count": post_count,
        "followers_count": followers_count,
        "following_count": following_count,
        "is_own_profile": is_own_profile,
        "is_following": is_following,
    })


@login_required
def follow_user(request, user_id):
    user_to_follow = get_object_or_404(User, id=user_id)

    follow, created = Follow.objects.get_or_create(
        follower=request.user,
        following=user_to_follow
    )
    
    if not created:
        follow.delete()
        is_followed = False
    else:
        is_followed = True

    user_to_follow.is_followed = is_followed
    user_to_follow.save()

    request.user.is_followed = Follow.objects.filter(following=request.user).exists()
    request.user.save()

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'is_following': is_followed})
    
    return redirect('profile', username=user_to_follow.username)

def get_suggested_users(request):
    current_user = request.user
    following = current_user.following.all()
    suggested_users = User.objects.exclude(id__in=following).exclude(id=current_user.id)[:5]
    return suggested_users