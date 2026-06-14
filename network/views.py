from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from .models import Post,User,Follow
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

# Add index view to handle both displaying posts and creating new ones:
def index(request):
    if request.method == "POST":
        if request.user.is_authenticated:
            content = request.POST.get("content")
            if content:
                Post.objects.create(user=request.user, content=content)
            return redirect("index")

    # Fetch all posts, newest first yah
    posts_list = Post.objects.all().order_by("-timestamp")

    # Paginate: 10 posts per page yes
    paginator = Paginator(posts_list, 10)
    page_number = request.GET.get("page")
    posts = paginator.get_page(page_number)

    return render(request, "network/index.html", {
        "posts": posts
    })

#Add views for user authentication (login, logout, register):
def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")

# Add a view to handle user logout:
def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))

# Add a view to handle user registration:
def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation: # If not match, please return an error message
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")
    
# Add a view to create new posts:
@login_required # My view is decorated with @login_required, so only authenticated users can access it.
def new_post(request):
    if request.method == "POST":
        content = request.POST.get("content")
        if content:
            Post.objects.create(user=request.user, content=content)
        return redirect("index")
    return render(request, "network/new_post.html")

# Add a view to load a user’s profile:
def profile(request, username):
    profile_user = get_object_or_404(User, username=username)
    posts_list = Post.objects.filter(user=profile_user).order_by("-timestamp")

    # Paginate: 10 posts per page
    paginator = Paginator(posts_list, 10)
    page_number = request.GET.get("page")
    posts = paginator.get_page(page_number)

    # Calculate counts directly from the Follow model:
    followers_count = profile_user.followers.count()
    following_count = profile_user.following.count()

    is_following = False
    
    # Check if the logged-in user is following the profile user
    if request.user.is_authenticated and request.user != profile_user:
        is_following = Follow.objects.filter(
            follower=request.user, following=profile_user
        ).exists()

    return render(request, "network/profile.html", {
        "profile_user": profile_user,
        "posts": posts,
        "followers_count": followers_count,
        "following_count": following_count,
        "is_following": is_following
    })

# Add a view to toggle following/unfollowing a user:
@login_required
def toggle_follow(request, username):
    profile_user = get_object_or_404(User, username=username)
    if request.user != profile_user:
        relation = Follow.objects.filter(follower=request.user, following=profile_user)
        if relation.exists():
            relation.delete()
        else:
            Follow.objects.create(follower=request.user, following=profile_user)
    return redirect("profile", username=username)

#Add views for adding pagination (10 posts per page)
def index(request):
    if request.method == "POST":
        if request.user.is_authenticated:
            content = request.POST.get("content")
            if content:
                Post.objects.create(user=request.user, content=content)
            return redirect("index")

    # Fetch all posts, newest first
    posts_list = Post.objects.all().order_by("-timestamp")

    # Paginate: 10 posts per page
    paginator = Paginator(posts_list, 10)
    page_number = request.GET.get("page")
    posts = paginator.get_page(page_number)

    return render(request, "network/index.html", {
        "posts": posts
    })

# Add a following view:
@login_required
def following(request):
    # Get all users the current user follows
    following_users = request.user.following.values_list("following", flat=True)

    # Filter posts only from those users
    posts_list = Post.objects.filter(user__in=following_users).order_by("-timestamp")

    # Paginate: 10 posts per page
    paginator = Paginator(posts_list, 10)
    page_number = request.GET.get("page")
    posts = paginator.get_page(page_number)

    return render(request, "network/following.html", {
        "posts": posts
    })

 #adding an endpoint views that only allows the post’s owner to edit:
@login_required
@csrf_exempt
def edit_post(request, post_id):
    if request.method == "PUT":
        post = Post.objects.get(pk=post_id)

        # Security: only the owner can edit
        if post.user != request.user:
            return JsonResponse({"error": "You cannot edit this post."}, status=403)

        # Get new content from request body
        import json
        data = json.loads(request.body)
        new_content = data.get("content", "").strip()

        if new_content:
            post.content = new_content
            post.save()
            return JsonResponse({"message": "Post updated successfully."})
        else:
            return JsonResponse({"error": "Content cannot be empty."}, status=400)
        
#Like/Unlike views to allow users to like or unlike posts
@login_required
def toggle_like(request, post_id):
    post = Post.objects.get(pk=post_id)

    if request.user in post.likes.all():
        post.likes.remove(request.user)
        liked = False
    else:
        post.likes.add(request.user)
        liked = True

    return JsonResponse({
        "liked": liked,
        "likes_count": post.likes.count()
    })
