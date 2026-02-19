from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Message
from users.models import CustomUser
from django.db.models import Q

@login_required
def user_list(request):
    users = CustomUser.objects.exclude(id=request.user.id)
    for u in users:
        u.last_message = Message.objects.filter(
            (Q(sender=request.user) & Q(receiver=u)) |
            (Q(sender=u) & Q(receiver=request.user))
        ).order_by('-timestamp').first()
        u.unread_count = Message.objects.filter(sender=u, receiver=request.user, is_read=False).count()
    return render(request, 'user_list.html', {'users': users})

@login_required
def chat_room(request, username):
    other_user = get_object_or_404(CustomUser, username=username)
    
    # Load previous history
    messages = Message.objects.filter(
        (Q(sender=request.user) & Q(receiver=other_user)) |
        (Q(sender=other_user) & Q(receiver=request.user))
    ).order_by('timestamp')
    
    # Mark messages as read
    Message.objects.filter(sender=other_user, receiver=request.user, is_read=False).update(is_read=True)
    
    users = CustomUser.objects.exclude(id=request.user.id)
    for u in users:
        u.last_message = Message.objects.filter(
            (Q(sender=request.user) & Q(receiver=u)) |
            (Q(sender=u) & Q(receiver=request.user))
        ).order_by('-timestamp').first()
        u.unread_count = Message.objects.filter(sender=u, receiver=request.user, is_read=False).count()

    return render(request, 'chat.html', {
        'other_user': other_user,
        'chat_messages': messages,
        'users': users
    })

def landing(request):
    return render(request, 'landing.html')
