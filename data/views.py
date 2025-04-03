from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from .forms import DataForm

@login_required
def Add_Figure(request):
    if request.method == 'POST':
        form = DataForm()

        if form.is_valid():
            data = form.save(commit=False)
            data.created_by = request.user
            data.save

            return redirect('/')
    else:
        form = DataForm()

    return render(request, 'data/add_figure.html', {
        'form': form,
    })