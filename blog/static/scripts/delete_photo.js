function confirmDeletePhoto(photoId) {
    if (confirm("Are you sure you want to delete this photo?")) {
        // Redirect to the delete URL for that specific photo
        window.location.href = '/delete_photo/' + photoId + '/';
    }
}