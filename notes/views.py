from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Note
from .forms import NoteForm


@login_required
def note_list(request):
    vendor = request.user
    notes = Note.objects.filter(vendor=vendor)

    # Search
    search = request.GET.get('q', '')
    if search:
        notes = notes.filter(
            Q(title__icontains=search) |
            Q(content__icontains=search)
        )

    return render(request, 'notes/note_list.html', {
        'notes': notes,
        'search': search,
        'page': 'notes',
    })


@login_required
def note_add(request):
    if request.method == 'POST':
        form = NoteForm(request.POST)
        if form.is_valid():
            note = form.save(commit=False)
            note.vendor = request.user
            note.save()
            messages.success(request, "Note created successfully.")
            return redirect('notes:note_list')
    else:
        form = NoteForm()

    return render(request, 'notes/note_form.html', {
        'form': form,
        'page': 'notes',
    })


@login_required
def note_edit(request, pk):
    note = get_object_or_404(Note, pk=pk, vendor=request.user)

    if request.method == 'POST':
        form = NoteForm(request.POST, instance=note)
        if form.is_valid():
            form.save()
            messages.success(request, "Note updated successfully.")
            return redirect('notes:note_list')
    else:
        form = NoteForm(instance=note)

    return render(request, 'notes/note_form.html', {
        'form': form,
        'note': note,
        'page': 'notes',
    })


@login_required
def note_detail(request, pk):
    note = get_object_or_404(Note, pk=pk, vendor=request.user)
    return render(request, 'notes/note_detail.html', {
        'note': note,
        'page': 'notes',
    })


@login_required
def note_delete(request, pk):
    note = get_object_or_404(Note, pk=pk, vendor=request.user)
    if request.method == 'POST':
        title = note.title
        note.delete()
        messages.success(request, f"Note '{title}' deleted.")
    return redirect('notes:note_list')
