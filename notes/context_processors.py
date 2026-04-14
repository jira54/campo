from .models import Note
from .forms import NoteForm

def sidebar_notes(request):
    if request.user.is_authenticated:
        # Get latest 5 notes for the sidebar
        notes = Note.objects.filter(vendor=request.user).order_by('-updated_at')[:5]
        return {
            'sidebar_notes': notes,
            'sidebar_note_form': NoteForm(),
        }
    return {}
