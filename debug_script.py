from chat.models import Message
import os
count = Message.objects.count()
with open('debug_count.txt', 'w') as f:
    f.write(str(count))
