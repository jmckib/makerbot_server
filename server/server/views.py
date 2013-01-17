from django import forms
from django.shortcuts import render

from print_s3g import print_s3g


class PrintS3GForm(forms.Form):
    s3g_file = forms.FileField()


def index(request):
    if request.method == 'POST':
        form = PrintS3GForm(request.POST, request.FILES)
        if form.is_valid():
            print_s3g(request.FILES['s3g_file'])
    else:
        form = PrintS3GForm()

    return render(request, 'index.html', {
        'form': form,
    })
