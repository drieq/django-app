function confirmDeleteAlbum(albumId) {
    if (confirm("Are you sure you want to delete this album and all its photos?")) {
        // Redirect to the delete URL for that specific album
        window.location.href = '/delete_album/' + albumId + '/';
    }
}