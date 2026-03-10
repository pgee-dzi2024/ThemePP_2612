import uuid
from django.db import models


class SecretMessage(models.Model):
    # Уникален идентификатор (токен), който ще се използва в URL адреса.
    # default=uuid.uuid4 генерира автоматично уникален низ при създаване на записа.
    # db_index=True ускорява търсенето в базата данни по този токен.
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)

    # Поле за съхранение на криптираното съобщение.
    # Използваме TextField, защото библиотеката за криптиране (Fernet) ще ни върне дълъг текст.
    encrypted_content = models.TextField()

    # Записва точните дата и час на създаване на съобщението.
    # Полезно е, ако по-късно решиш да добавиш функционалност за автоматично
    # изтриване на непрочетени съобщения след определено време (напр. 7 дни).
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Съобщение с токен: {self.token}"
