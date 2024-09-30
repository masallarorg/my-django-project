import openai
import random
from django.utils.text import slugify
import requests
from django.conf import settings
import os
import re  # Karakter temizlemek için regex kullanacağız
from .models import UserStory, Badge, UserBadge, Notification
from gtts import gTTS
from django.core.files import File
from io import BytesIO





openai.api_key = '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'




from gtts import gTTS
from io import BytesIO
from django.core.files import File

def generate_story_audio(story):
    """
    Verilen hikaye için ses dosyası oluşturur ve veritabanına kaydeder.
    """
    # Hikaye içeriğini seslendir (Türkçe dilinde)
    tts = gTTS(text=story.content, lang='tr', slow=False)

    # Bellekte ses dosyasını oluştur
    audio_file = BytesIO()
    tts.write_to_fp(audio_file)

    # Ses dosyasını geri sar
    audio_file.seek(0)

    # Ses dosyasını veritabanına kaydet
    story.audio_file.save(f"{story.slug}_audio.mp3", File(audio_file))

    # Ses dosyasının URL'sini döndür
    return story.audio_file.url






def check_and_award_badge(user):
    # Kullanıcının okuduğu hikayeleri say
    total_stories_read = UserStory.objects.filter(user=user).count()

    # Rozet kriteri (örneğin 5 hikaye okuyan "Kitap Kurdu" rozetini kazanır)
    if total_stories_read >= 5:
        badge, created = Badge.objects.get_or_create(
            name="Kitap Kurdu", 
            defaults={
                'description': "5 hikaye okuyan kullanıcılara verilen rozet.",
                'icon': 'badges/kitap_kurdu.png'
            }
        )

        # Eğer kullanıcı bu rozeti daha önce kazanmamışsa, kazandır
        if not UserBadge.objects.filter(user=user, badge=badge).exists():
            UserBadge.objects.create(user=user, badge=badge)

            # Rozeti kazanan kullanıcıya bildirim gönder
            Notification.objects.create(user=user, message=f"Tebrikler! '{badge.name}' rozetini kazandınız.")

            # Tüm kullanıcılara bu başarıyı duyur
            message = f"{user.username} 'Kitap Kurdu' rozetini kazandı! Tebrik ederiz."
            users = User.objects.exclude(id=user.id)  # Kazanan hariç tüm kullanıcılara bildirim gönder
            for u in users:
                Notification.objects.create(user=u, message=message)

            return badge
    return None





# Yardımcı Fonksiyonlar

def clean_text(text):
    """İstenmeyen karakterleri temizler."""
    return re.sub(r'[^\w\s]', '', text)

# Başlık Üretimi

def generate_story_title():
    """Yapay zeka kullanarak hikaye başlığı üretir."""
    response = openai.ChatCompletion.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": "Sen yaratıcı bir asistansın ve çocuk hikayeleri için başlıklar oluşturuyorsun."},
            {"role": "user", "content": "Lütfen kısa ve yaratıcı bir çocuk hikayesi başlığı öner."}
        ]
    )
    title = response['choices'][0]['message']['content'].strip()
    return clean_text(title)

# İçerik Üretimi

def generate_story_content(title):
    """Başlık üzerinden hikaye içeriği üretir."""
    category = categorize_story(title)
    greeting_message = f"Merhaba! Bu hikaye, '{title}' başlıklı renkli bir macera sunuyor. Keyifle okuyun!"
    
    prompt = f"Lütfen '{title}' başlıklı, '{category}' kategorisinde bir çocuk hikayesi yaz. Hikaye çocuklara uygun olmalı."
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": "Sen yaratıcı bir asistansın ve çocuk hikayeleri yazıyorsun."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1500
        )
        content = response['choices'][0]['message']['content'].strip()
        cleaned_content = clean_text(content)
        return f"{greeting_message}\n\n{cleaned_content}"
    except Exception as e:
        return f"Hikaye oluşturulurken bir hata oluştu: {str(e)}"

# Yorum Analizi

def analyze_comment(comment_content):
    """Yorumun zararlı olup olmadığını analiz eder."""
    prompt = f"Bu yorum zararlı mı veya uygunsuz mu?: '{comment_content}'"
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": "Sen bir içerik moderatörüsün ve yorumların zararlı olup olmadığını tespit ediyorsun."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=60
        )
        analysis = response['choices'][0]['message']['content'].strip().lower()
        return 'yes' in analysis  # Zararlıysa True döndür
    except Exception as e:
        return False

# Kapak Resmi Üretimi ve Kaydetme

def generate_cover_image(title):
    """Yapay zeka ile kapak resmi üretir."""
    try:
        response = openai.Image.create(
            prompt=f"A detailed children's book cover illustration in cartoon style based on the title '{title}'.",
            n=1,
            size="1024x1024"
        )
        image_url = response['data'][0]['url']
        return image_url
    except Exception as e:
        return f"Kapak resmi oluşturulamadı: {str(e)}"


def download_and_save_image(image_url, title):
    """Kapak resmini indirir ve dosya sistemine kaydeder."""
    try:
        response = requests.get(image_url, timeout=10)
        response.raise_for_status()

        if response.status_code == 200:
            file_name = slugify(title) + ".png"
            covers_dir = os.path.join(settings.MEDIA_ROOT, "covers")

            if not os.path.exists(covers_dir):
                os.makedirs(covers_dir)
            
            file_path = os.path.join(covers_dir, file_name)
            
            with open(file_path, "wb") as f:
                f.write(response.content)
            
            return f"covers/{file_name}"
        else:
            return None
    except requests.exceptions.RequestException as e:
        print(f"Resim indirirken hata oluştu: {str(e)}")
        return None

# Kategori ve Etiket Üretimi

def categorize_story(title):
    """Hikaye başlığına göre kategoriyi belirler."""
    categories = {
        "Hayvanlar": ["kedi", "köpek", "aslan", "fil", "tavşan", "zürafa"],
        "Macera": ["macera", "yolculuk", "keşif", "hazina", "tehlike"],
        "Dostluk": ["dost", "arkadaş", "birlikte", "yardım"],
        "Doğa": ["orman", "deniz", "dağ", "nehir", "doğa", "çevre", "ağaç"]
    }

    title_lower = title.lower()
    for category, keywords in categories.items():
        if any(keyword in title_lower for keyword in keywords):
            return category
    return "Genel"

def generate_story_tags(title, content):
 
    prompt = f"'{title}' başlıklı bir hikaye için uygun, kısa ve anlamlı etiketler üret."
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": "Sen yaratıcı bir asistansın ve hikayeler için uygun etiketler üretiyorsun."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=60
        )
        tags = response['choices'][0]['message']['content'].strip()
        tags = tags.replace(" ", "_").replace("#", "").split(", ")
        return [f"#{tag}" for tag in tags]
    except Exception as e:
        return ["#etiket_üretilemedi"]

# SEO Önerileri

def generate_seo_recommendations(title, content):
    """SEO optimizasyon önerileri üretir."""
    prompt = f"Bu sayfa için SEO önerileri yap. Başlık: '{title}', İçerik: '{content}'."
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": "Sen bir SEO uzmanısın ve öneriler yapıyorsun."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=200
        )
        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        return f"SEO önerileri oluşturulurken hata: {str(e)}"

# Backlink Fırsatları

def generate_backlink_opportunities(content, keywords):
    """Backlink fırsatları önerir."""
    prompt = f"Bu içerik ve anahtar kelimelere göre backlink fırsatları öner: '{content}', Anahtar kelimeler: {keywords}."
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": "Sen bir backlink uzmanısın ve fırsatları öneriyorsun."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=300
        )
        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        return f"Backlink fırsatları oluşturulurken hata: {str(e)}"
import time

def generate_meta_description(title, content):
    """
    Hikaye başlığı ve içeriğine dayalı olarak SEO uyumlu meta description oluşturur.
    """
    prompt = f"SEO optimizasyonu için, '{title}' başlığı ve içeriğiyle uyumlu, maksimum 160 karakterlik bir meta description oluştur."

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": "SEO optimizasyonları öneren bir asistansın."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=100  # Meta description için sınırlandırılmış token
        )

        meta_description = response['choices'][0]['message']['content'].strip()

        # Eğer meta description boş kalırsa varsayılan değer
        if not meta_description or len(meta_description) < 10:  # En az 10 karakterlik bir description bekleniyor
            meta_description = "Bu sayfa çocuk hikayeleri ve masallar hakkında bilgi içermektedir."

        return meta_description

    except Exception as e:
        return "Meta description oluşturulamadı."
def generate_keywords(title, content):
    """
    Hikaye başlığı ve içeriğine dayalı olarak SEO uyumlu anahtar kelimeler oluşturur.
    """
    prompt = f"SEO optimizasyonu için, '{title}' başlığı ve içeriğiyle uyumlu anahtar kelimeler oluştur. Anahtar kelimeler virgülle ayrılmalı ve içerikle alakalı olmalı."

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": "SEO uyumlu anahtar kelimeler öneren bir asistansın."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=100  # Anahtar kelimeler için sınırlandırılmış token
        )

        keywords = response['choices'][0]['message']['content'].strip()

        # Eğer keywords boş kalırsa varsayılan değer
        if not keywords or len(keywords) < 5:  # En az 5 karakterlik anahtar kelimeler bekleniyor
            keywords = "çocuk hikayeleri, masallar, çocuk kitapları"

        return keywords

    except Exception as e:
        return "Anahtar kelimeler oluşturulamadı."









def analyze_comment(comment_content):
    # Yorumun zararlı olup olmadığını analiz eden OpenAI GPT-4 modeli
    prompt = f"Bu yorum zararlı mı veya uygunsuz mu?: '{comment_content}'"
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": "Sen bir içerik moderatörüsün ve yorumların zararlı olup olmadığını tespit ediyorsun."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=60
        )
        
        analysis = response['choices'][0]['message']['content'].strip().lower()
        return 'yes' not in analysis  # Eğer analiz sonucunda zararlı değilse True döner
    
    except Exception as e:
        return False  # Hata durumunda yorum zararlı kabul edilmez