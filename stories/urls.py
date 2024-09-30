# stories/urls.py
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views


urlpatterns = [

    path('', views.home, name='home'),  # Ana sayfa
    path('story/<slug:slug>/', views.story_detail, name='story_detail'),  # Hikaye detay
    path('category/<slug:slug>/', views.category_detail, name='category_detail'),  # Kategori detayı
    path('comment/<int:comment_id>/delete/', views.delete_comment, name='delete_comment'),
    path('signup/', views.signup, name='signup'),  # Kayıt olma url'si
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),  # Logout URL tanımı
    path('profile/', views.profile_view, name='profile'),  # Correct view function
    path('profile/delete_story/<int:story_id>/', views.delete_story, name='delete_story'),
    path('profile/delete_comment/<int:comment_id>/', views.delete_comment, name='delete_comment'),
    path('profile/delete_notification/<int:notification_id>/', views.delete_notification, name='delete_notification'),
    path('notifications/', views.notifications_view, name='notifications'),
    path('search/', views.search, name='search'),  # Add this for the search view
    path('delete_notification/<int:notification_id>/', views.delete_notification, name='delete_notification'),
    path('notifications/delete/<int:notification_id>/', views.delete_notification, name='delete_notification'),
    path('hakkinda/', views.hakkinda_view, name='hakkinda'),
    path('iletisim/', views.iletisim_view, name='iletisim'),

]
