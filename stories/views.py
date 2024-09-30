from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from .models import Story, Category, Comment, Notification, UserStory, UserBadge, Badge
from .forms import CommentForm, ReplyForm, SignUpForm, ContactForm
from .utils import analyze_comment,check_and_award_badge
from .models import Notification
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings



def hakkinda_view(request):
    return render(request, 'hakkinda.html')

def iletisim_view(request):
    form = ContactForm()
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            ad_soyad = form.cleaned_data['ad_soyad']
            email = form.cleaned_data['email']
            mesaj = form.cleaned_data['mesaj']
            
            # E-posta gönderimi (isteğe bağlı)
            send_mail(
                f"{ad_soyad} adlı kişiden iletişim formu mesajı",
                mesaj,
                settings.DEFAULT_FROM_EMAIL,
                [settings.ADMIN_EMAIL],  # Adminin e-posta adresini burada belirtebilirsiniz
                fail_silently=False,
            )
            return render(request, 'iletisim_basarili.html')

    return render(request, 'iletisim.html', {'form': form})











def notifications(request):
    user_notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'notifications.html', {'notifications': user_notifications})


# Anasayfa
from django.shortcuts import render
from django.core.paginator import Paginator
from .models import Notification, Story, Category

def home(request):
    # Bildirim sayısını başlatıyoruz, varsayılan 0
    unread_notifications_count = 0
  
    # Eğer kullanıcı giriş yapmışsa, okunmamış bildirimlerin sayısını al
    if request.user.is_authenticated:
        unread_notifications_count = Notification.objects.filter(user=request.user, is_read=False).count()

    # Hikayeler ve kategorileri alıyoruz, ardından sayfalamayı ayarlıyoruz
    story_list = Story.objects.all().order_by('-created_at')
    categories = Category.objects.all()  # Navbar'da göstermek için kategoriler

    # Sayfalama: her sayfada 6 hikaye
    paginator = Paginator(story_list, 6)
    page_number = request.GET.get('page')
    stories = paginator.get_page(page_number)

    # Meta açıklama ve anahtar kelimeleri ayarlama
    meta_description = 'Çocuklar için eğlenceli ve eğitici hikayeler. En iyi masallar ve çocuk hikayeleri burada!'
    meta_keywords = 'çocuk hikayeleri, eğitici masallar, kısa hikayeler, çocuk kitapları, kısa masallar, masallar, masal oku'

    # Şablona gerekli verileri geçiyoruz
    return render(request, 'index.html', {
        'stories': stories, 
        'categories': categories,
        'unread_notifications_count': unread_notifications_count,  # Bildirim sayısı şablona geçiliyor
        'meta_description': meta_description,
        'meta_keywords': meta_keywords,
    })

    # Bildirim sayısını başlatıyoruz, varsayılan 0
    unread_notifications_count = 0
  
    # Eğer kullanıcı giriş yapmışsa, okunmamış bildirimlerin sayısını al
    if request.user.is_authenticated:
        unread_notifications_count = Notification.objects.filter(user=request.user, is_read=False).count()

    # Hikayeler ve kategorileri alıyoruz, ardından sayfalamayı ayarlıyoruz
    story_list = Story.objects.all().order_by('-created_at')
    categories = Category.objects.all()  # Navbar'da göstermek için kategoriler

    # Sayfalama: her sayfada 6 hikaye
    paginator = Paginator(story_list, 6)
    page_number = request.GET.get('page')
    stories = paginator.get_page(page_number)
    
    # Şablona gerekli verileri geçiyoruz
    return render(request, 'index.html', {
        
        'stories': stories, 
        'categories': categories,
        'unread_notifications_count': unread_notifications_count  # Bildirim sayısı şablona geçiliyor
    })
# Kullanıcı profili

@login_required
def profile_view(request):
    # Kullanıcının okuduğu hikayeleri sorgulama
    user_stories = UserStory.objects.filter(user=request.user).order_by('-read_at')
    story_paginator = Paginator(user_stories, 5)  # Her sayfada 5 hikaye gösterilecek
    story_page_number = request.GET.get('story_page')
    story_page_obj = story_paginator.get_page(story_page_number)

    # Kullanıcının bildirimlerini sorgulama
    user_notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    notification_paginator = Paginator(user_notifications, 5)  # Her sayfada 5 bildirim gösterilecek
    notification_page_number = request.GET.get('notification_page')
    notification_page_obj = notification_paginator.get_page(notification_page_number)

    # Kullanıcının yorumlarını sorgulama
    user_comments = Comment.objects.filter(author=request.user).order_by('-created_at')
    comment_paginator = Paginator(user_comments, 5)  # Her sayfada 5 yorum gösterilecek
    comment_page_number = request.GET.get('comment_page')
    comment_page_obj = comment_paginator.get_page(comment_page_number)

    # Kullanıcının kazandığı rozetleri sorgulama
    user_badges = UserBadge.objects.filter(user=request.user)

    context = {
        'story_page_obj': story_page_obj,  # Hikaye sayfalama objesi
        'notification_page_obj': notification_page_obj,  # Bildirim sayfalama objesi
        'comment_page_obj': comment_page_obj,  # Yorum sayfalama objesi
        'user_badges': user_badges,  # Kullanıcının kazandığı rozetler
    }

    return render(request, 'profile.html', context)


# Silme işlemleri

@login_required
def delete_story(request, story_id):
    user_story = get_object_or_404(UserStory, id=story_id, user=request.user)
    user_story.delete()
    return redirect('profile')

@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id, author=request.user)
    comment.delete()
    return redirect('profile')

@login_required
def delete_notification(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.delete()
    return redirect('profile')

# Kayıt olma fonksiyonu



def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')  # Kayıt sonrası giriş sayfasına yönlendir
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})


def story_detail(request, slug):
    # Hikayeyi getirme
    story = get_object_or_404(Story, slug=slug)

    # Rozet kontrolü ve otomatik atama (Örnek bir rozet fonksiyonu kullanarak)
    if request.user.is_authenticated:
        UserStory.objects.get_or_create(user=request.user, story=story)
        check_and_award_badge(request.user)  # Rozet kontrolü ve ataması

    # Onaylanmış yorumları alma ve sayfalama
    comments = Comment.objects.filter(story=story, approved=True).order_by('-created_at')
    paginator = Paginator(comments, 5)  # Sayfa başına 5 yorum
    page_number = request.GET.get('page')
    comments = paginator.get_page(page_number)

    # Önceki ve sonraki hikayeleri alma
    try:
        previous_story = story.get_previous_by_created_at()
    except Story.DoesNotExist:
        previous_story = None

    try:
        next_story = story.get_next_by_created_at()
    except Story.DoesNotExist:
        next_story = None

    # Yorum formunu işleme
    if request.method == 'POST':
        if request.user.is_authenticated:
            form = CommentForm(request.POST)
            if form.is_valid():
                comment = form.save(commit=False)
                comment.story = story
                comment.author = request.user
                comment.approved = False  # Yorum admin onayı beklesin
                comment.save()
                
                # Kullanıcıya mesaj gösterme
                messages.success(request, "Yorumunuz için teşekkür ederiz! Yorumunuz onaylandıktan sonra yayınlanacaktır.")
                
                return redirect('story_detail', slug=story.slug)
        else:
            return redirect('login')  # Giriş yapılmamışsa yönlendirme

    else:
        form = CommentForm()

    # Şablona verileri gönderme
    return render(request, 'story_detail.html', {
        'story': story,
        'comments': comments,
        'form': form,
        'previous_story': previous_story,
        'next_story': next_story,
    })

    # Hikayeyi getirme
    story = get_object_or_404(Story, slug=slug)
    # Rozet kontrolü ve otomatik atama
    UserStory.objects.get_or_create(user=request.user, story=story)
    check_and_award_badge(request.user)
    # Kullanıcı giriş yaptıysa okuduğu hikayeyi kaydetme
    if request.user.is_authenticated:
        UserStory.objects.get_or_create(user=request.user, story=story)

    # Onaylanmış yorumları alma ve sayfalama
    comments = Comment.objects.filter(story=story, approved=True).order_by('-created_at')
    paginator = Paginator(comments, 5)  # Sayfa başına 5 yorum
    page_number = request.GET.get('page')
    comments = paginator.get_page(page_number)

    # Önceki ve sonraki hikayeleri alma
    try:
        previous_story = story.get_previous_by_created_at()
    except Story.DoesNotExist:
        previous_story = None

    try:
        next_story = story.get_next_by_created_at()
    except Story.DoesNotExist:
        next_story = None

    # Yorum formunu işleme
    if request.method == 'POST':
        if request.user.is_authenticated:
            form = CommentForm(request.POST)
            if form.is_valid():
                comment = form.save(commit=False)
                comment.story = story
                comment.author = request.user
                comment.approved = False  # Yorum admin onayı beklesin
                comment.save()
                
                # Kullanıcıya mesaj gösterme
                messages.success(request, "Yorumunuz için teşekkür ederiz! Yorumunuz onaylandıktan sonra yayınlanacaktır.")
                
                return redirect('story_detail', slug=story.slug)
        else:
            return redirect('login')  # Giriş yapılmamışsa yönlendirme

    else:
        form = CommentForm()

    # Şablona verileri gönderme
    return render(request, 'story_detail.html', {
        'story': story,
        'comments': comments,
        'form': form,
        'previous_story': previous_story,
        'next_story': next_story,
    })
    # Hikayeyi getirme
    story = get_object_or_404(Story, slug=slug)

    # Kullanıcı giriş yaptıysa okuduğu hikayeyi kaydetme
    if request.user.is_authenticated:
        UserStory.objects.get_or_create(user=request.user, story=story)

    # Onaylanmış yorumları alma ve sayfalama
    comments = Comment.objects.filter(story=story, approved=True).order_by('-created_at')
    paginator = Paginator(comments, 5)  # Sayfa başına 5 yorum
    page_number = request.GET.get('page')
    comments = paginator.get_page(page_number)

    # Önceki ve sonraki hikayeleri alma
    try:
        previous_story = story.get_previous_by_created_at()
    except Story.DoesNotExist:
        previous_story = None

    try:
        next_story = story.get_next_by_created_at()
    except Story.DoesNotExist:
        next_story = None

    # Yorum formunu işleme
    if request.method == 'POST':
        if request.user.is_authenticated:
            form = CommentForm(request.POST)
            if form.is_valid():
                comment = form.save(commit=False)
                comment.story = story
                comment.author = request.user
                comment.approved = False  # Yorum admin onayı beklesin
                comment.save()
                return redirect('story_detail', slug=story.slug)
        else:
            return redirect('login')  # Giriş yapılmamışsa yönlendirme

    else:
        form = CommentForm()

    # Şablona verileri gönderme
    return render(request, 'story_detail.html', {
        'story': story,
        'comments': comments,
        'form': form,
        'previous_story': previous_story,
        'next_story': next_story,
    })
# Kategori detay sayfası
def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug)
    story_list = Story.objects.filter(category=category).order_by('-created_at')
    
    # Sayfalama: sayfa başına 6 hikaye göster
    paginator = Paginator(story_list, 6)
    page_number = request.GET.get('page')
    stories = paginator.get_page(page_number)
    
    categories = Category.objects.all()  # Navbar'da göstermek için kategoriler

    return render(request, 'category_detail.html', {
        'category': category,
        'stories': stories,
        'categories': categories
    })

# Yorum silme fonksiyonu
@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)

    # Yalnızca yorum sahibine silme izni ver
    if comment.author == request.user:
        comment.delete()
        return redirect('story_detail', slug=comment.story.slug)
    else:
        return HttpResponseForbidden("Yalnızca kendi yorumlarınızı silebilirsiniz.")

# Yorum yanıtı ekleme fonksiyonu
def add_reply(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    
    if request.method == 'POST':
        form = ReplyForm(request.POST)
        if form.is_valid():
            reply = form.save(commit=False)
            reply.comment = comment
            reply.author = request.user
            reply.save()
            return redirect('story_detail', slug=comment.story.slug)
    else:
        form = ReplyForm()

    return render(request, 'story_detail.html', {'form': form, 'comment': comment})


@login_required
def notifications_view(request):
    # Kullanıcının bildirimlerini alıyoruz
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'notifications.html', {'notifications': notifications})


def search(request):
    query = request.GET.get('q')
    results = []
    if query:
        results = Story.objects.filter(title__icontains=query)  # Adjust as needed to search story titles
    return render(request, 'search_results.html', {'results': results, 'query': query})

def delete_notification(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.delete()  # Bildirimi veritabanından sil
    return redirect('notifications')  # Silme sonrası bildirimler sayfasına yönlendir



