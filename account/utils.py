from django.core.mail import send_mail
from django.template.loader import render_to_string
from threading import Thread


def func_send_mail(form, user):
    rendered_message = render_to_string('account/email_message/email_message.html',
                                        context={
                                            'content': form.cleaned_data['content'],
                                            'username': user.username,
                                            'email': user.email,
                                        })
    send_mail(subject='Тема: {}'.format(form.cleaned_data['title']),
              message=form.cleaned_data['content'],
              from_email=None,
              recipient_list=['ivshavrin@gmail.com'],
              html_message=rendered_message
              )


def send_async_mail(form, user):
    Thread(target=func_send_mail, args=(form, user)).start()

