from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect

from django.views.decorators.csrf import csrf_protect

from django.conf import settings
from cryptography.fernet import Fernet
from .models import SecretMessage  # Импортираме модела за съобщенията

@csrf_protect
def login_view(request):
    next_url = request.GET.get('next') or request.POST.get('next') or 'home'
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
    else:
        form = AuthenticationForm(request)

    # Подавам form за да покажа грешки/values без да променям визията
    return render(request, 'main/sign-in.html', {'form': form, 'next': next_url})

@csrf_protect
def message(request):
    if request.method == 'POST':
        # 1. Вземаме текста от формата (атрибута name="content" от HTML-а)
        raw_content = request.POST.get('content')
        print(f'1: {raw_content}')

        if raw_content:
            # 2. Инициализираме криптирането с нашия ключ от settings.py
            f = Fernet(settings.ENCRYPTION_KEY)
            print('2')
            # 3. Криптираме текста (първо трябва да го превърнем в байтове)
            encrypted_content = f.encrypt(raw_content.encode('utf-8'))
            print('3')
            # 4. Записваме в базата данни
            # Използваме .decode('utf-8'), за да превърнем криптираните байтове обратно в текст,
            # подходящ за запис в TextField базата.
            secret = SecretMessage.objects.create(
                encrypted_content=encrypted_content.decode('utf-8')
            )
            print('4')
            # 5. Генериране на линк за четене
            # secret.token е уникалното UUID на записа
            relative_url = f"/secret/{secret.token}/"
            # build_absolute_uri превръща /secret/... в пълен линк (напр. http://127.0.0.1:8000/secret/...)
            full_url = request.build_absolute_uri(relative_url)
            print('5')
            # 6. Зареждаме страницата за резултат, като предаваме линка като контекст
            print(f'6: {full_url}')
            return render(request, 'main/link.html', {'secret_link': full_url})

    # Ако заявката е GET (потребителят просто отваря страницата), показваме празната форма
    return render(request, 'main/message.html')

@csrf_protect
def logout_view(request):
    logout(request)
    return redirect('login')

@csrf_protect
def token_link(request):
    return render(request, 'main/link.html')


# Увери се, че имаш тези импорти най-горе:
# from cryptography.fernet import Fernet
# from django.conf import settings
# from .models import SecretMessage

def read_secret(request, token):
    try:
        # 1. Търсим съобщението в базата данни по токена
        secret = SecretMessage.objects.get(token=token)

        # 2. Инициализираме криптирането със същия ключ
        f = Fernet(settings.ENCRYPTION_KEY)

        # 3. Декриптираме съдържанието
        # Първо превръщаме стринга от базата в байтове (.encode),
        # декриптираме го и го връщаме обратно в нормален текст (.decode)
        decrypted_bytes = f.decrypt(secret.encrypted_content.encode('utf-8'))
        decrypted_text = decrypted_bytes.decode('utf-8')

        # 4. НАЙ-ВАЖНАТА СТЪПКА: Изтриваме записа от базата данни!
        # Това гарантира "еднократното прочитане"
        secret.delete()

        # 5. Зареждаме шаблон, в който показваме тайното съобщение
        return render(request, 'main/read_secret.html', {
            'secret_message': decrypted_text,
            'error': False
        })

    except SecretMessage.DoesNotExist:
        # Ако съобщението не съществува (вече е прочетено и изтрито, или линкът е грешен)
        return render(request, 'main/read_secret.html', {
            'error': True,
            'error_msg': 'Това съобщение вече е прочетено и унищожено, или линкът е невалиден.'
        })
    except Exception as e:
        # Хващаме всякакви други грешки (напр. проблем с ключа за декриптиране)
        return render(request, 'main/read_secret.html', {
            'error': True,
            'error_msg': 'Възникна грешка при декриптирането на съобщението.'
        })