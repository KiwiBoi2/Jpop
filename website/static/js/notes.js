function deleteNote(noteId) {
    if (confirm('Are you sure you want to delete this note?')) {
        fetch(`/delete-note/${noteId}`, {
            method: 'POST',
        }).then(response => {
            if (response.ok) {
                window.location.reload();
            }
        });
    }
}

function editNote(noteId, currentContent) {
    const newContent = prompt('Edit your note:', currentContent);
    if (newContent && newContent !== currentContent) {
        fetch(`/edit-note/${noteId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ content: newContent })
        }).then(response => {
            if (response.ok) {
                window.location.reload();
            }
        });
    }
}