import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chat_app.settings')
django.setup()
from chat.models import Message
from users.models import CustomUser

with open('db_debug.txt', 'w') as f:
    f.write(f"DB Path: {os.path.join(os.getcwd(), 'db_chat.sqlite3')}\n")
    f.write(f"Total Messages: {Message.objects.count()}\n")
    f.write(f"Total Users: {CustomUser.objects.count()}\n")
    f.write("Recent Messages:\n")
    for m in Message.objects.order_by('-timestamp')[:5]:
        f.write(f"{m.sender.username} -> {m.receiver.username}: {m.message}\n")
