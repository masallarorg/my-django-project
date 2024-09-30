from django.contrib import admin
from .models import Story, Category, Comment, SEOSettings, Backlink, Notification, Badge, UserBadge
from django.contrib.auth.models import User
from .utils import generate_story_title, generate_story_content, categorize_story, generate_story_tags, generate_cover_image, analyze_comment, download_and_save_image, generate_meta_description, generate_keywords, generate_story_audio
from django.utils.text import slugify
import logging

# Log ayarları
logger = logging.getLogger(__name__)

# Story Admin Paneli (Sadece bir kez kayıt ediyoruz)
@admin.register(Story)
class StoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'created_at')
    search_fields = ('title', 'content')

    def save_model(self, request, obj, form, change):
        # Önce kaydetme işlemi gerçekleşir
        super().save_model(request, obj, form, change)

        # Eğer yeni bir hikaye ekleniyorsa bildirim oluştur
        if not change:  
            users = User.objects.all()
            for user in users:
                Notification.objects.create(
                    user=user,
                    message=f"Yeni bir hikaye eklendi: {obj.title}",
                )
            logger.info(f"Yeni hikaye bildirimi oluşturuldu: {obj.title}")

        # Başlık boşsa yapay zeka tarafından başlık oluştur
        if not obj.title:
            obj.title = generate_story_title()
            logger.info(f"Yapay zeka ile başlık oluşturuldu: {obj.title}")

        # Eğer slug boşsa başlık üzerinden slug oluştur
        if not obj.slug and obj.title:
            obj.slug = slugify(obj.title)
            original_slug = obj.slug
            counter = 1
            while Story.objects.filter(slug=obj.slug).exists():
                obj.slug = f"{original_slug}-{counter}"
                counter += 1
            logger.info(f"Slug oluşturuldu: {obj.slug}")

        # Kategoriyi başlık üzerinden belirle
        if not obj.category:
            category_name = categorize_story(obj.title)
            try:
                obj.category = Category.objects.get(name=category_name)
            except Category.DoesNotExist:
                obj.category = Category.objects.get_or_create(name="Genel")[0]
            logger.info(f"Kategori atandı: {obj.category}")

        # Eğer içerik boşsa, yapay zeka tarafından içerik oluştur
        if not obj.content:
            obj.content = generate_story_content(obj.title)
            logger.info(f"İçerik oluşturuldu: {obj.content}")

        # Eğer etiketler boşsa, başlık ve içerikten etiket üret
        if not obj.tags:
            obj.tags = ", ".join(generate_story_tags(obj.title, obj.content))
            logger.info(f"Etiketler oluşturuldu: {obj.tags}")

        # Eğer kapak fotoğrafı yoksa, yapay zeka tarafından kapak fotoğrafı oluştur ve indir
        if not obj.cover_image:
            image_url = generate_cover_image(obj.title)
            saved_image_path = download_and_save_image(image_url, obj.title)
            if saved_image_path:
                obj.cover_image = saved_image_path
            logger.info(f"Kapak fotoğrafı oluşturuldu: {obj.cover_image}")

        # Meta description ve keywords boşsa yapay zeka tarafından oluştur
        if not obj.meta_description:
            obj.meta_description = generate_meta_description(obj.title, obj.content)
            logger.info(f"Meta description: {obj.meta_description}")
        
        if not obj.keywords:
            obj.keywords = generate_keywords(obj.title, obj.content)
            logger.info(f"Keywords: {obj.keywords}")

        # Sesli versiyonu oluşturma (eğer sesli versiyon yoksa)
        if not obj.audio_file:
            generate_story_audio(obj)

        # Son olarak kaydetme işlemini tamamla
        super().save_model(request, obj, form, change)
        logger.info(f"Hikaye kaydedildi: {obj.title}")

# Category Admin Paneli
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}

# Comment Admin Paneli
@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('story', 'author', 'approved', 'created_at')
    list_filter = ('approved', 'created_at')
    search_fields = ('content',)
    actions = ['approve_comments']

    def approve_comments(self, request, queryset):
        queryset.update(approved=True)
    approve_comments.short_description = "Seçilen yorumları onayla"

# SEOSettings Admin Paneli
@admin.register(SEOSettings)
class SEOSettingsAdmin(admin.ModelAdmin):
    list_display = ('page_title', 'meta_description', 'keywords')
    search_fields = ('page_title', 'keywords')

# Backlink Admin Paneli
@admin.register(Backlink)
class BacklinkAdmin(admin.ModelAdmin):
    list_display = ('target_url', 'anchor_text', 'quality_score', 'added_on')
    search_fields = ('target_url', 'anchor_text')

# Bildirim modeli için admin paneli
@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('message', 'is_read', 'created_at', 'user')

    # Toplu bildirim gönderme işlemi
    actions = ['send_bulk_notification']

    def send_bulk_notification(self, request, queryset):
        # Kullanıcılara gönderilecek mesajı tanımlayın
        message = "Admin tarafından gönderilen toplu bildirim."

        # Tüm kullanıcıları alın
        users = User.objects.all()

        # Her kullanıcıya bildirim oluşturun
        for user in users:
            Notification.objects.create(user=user, message=message)

        self.message_user(request, "Tüm kullanıcılara başarıyla bildirim gönderildi.")
    
    send_bulk_notification.short_description = "Tüm kullanıcılara bildirim gönder"

# Badge Admin Paneli
@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'created_at')

# UserBadge Admin Paneli
@admin.register(UserBadge)
class UserBadgeAdmin(admin.ModelAdmin):
    list_display = ('user', 'badge', 'awarded_at')
