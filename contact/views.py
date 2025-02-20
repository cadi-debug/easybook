from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.contrib import messages
from .forms import ContactForm


def contact_view(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            contact = form.save()
            send_mail(
                f'Message from {contact.name}',
                contact.message,
                contact.email,
                ['cadikambaji@gmail.com'],
            )
            messages.success(request, 'Your message has been sent successfully!')
            return redirect('contact:contact')
    else:
        form = ContactForm()
    return render(request, 'contact/contact.html', {'form': form})


def about(request):
    return render(request,'about.html')
