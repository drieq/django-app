
        $(document).ready(function(){
            var albumId = "{{ album.id }}";  // Pass the album's ID to the AJAX request

            // Edit title
            $("#edit-title-btn").click(function(){
                $("#album-title").hide();  // Hide the current title
                $("#album-title-input").show();  // Show the input for editing
                $("#album-title-input").focus();  // Focus on the input field

                // Move the type cursor to the end of the input field
                var input = $("#album-title-input");
                input.val(input.val());  // Set the value to itself to trigger the cursor to the end
                input[0].setSelectionRange(input.val().length, input.val().length);

            });

            // Edit description
            $("#edit-description-btn").click(function(){
                $("#album-description").hide();  // Hide the current description
                $("#album-description-input").show();  // Show the textarea for editing
                $("#album-description-input").focus();  // Focus on the input field

                // Move the type cursor to the end of the input field
                var input = $("#album-description-input");
                input.val(input.val());  // Set the value to itself to trigger the cursor to the end
                input[0].setSelectionRange(input.val().length, input.val().length);

            });

            // Trigger when the input loses focus (blur)
            $('#album-title-input').on('blur', function() {
                var newTitle = $(this).val().trim();  // Get the new title and trim any extra whitespace
                var originalTitle = $("#album-title").text().trim(); // Get the original title from the element

                if (newTitle !== originalTitle) {  // Only send the request if the title has changed

                    $.ajax({
                        url: "{% url 'update_album_title' album_id=album.id %}",
                        type: "POST",
                        data: {
                            'title': newTitle,  // The new title value
                            'csrfmiddlewaretoken': '{{ csrf_token }}'  // CSRF token
                        },
                        success: function(response) {
                            console.log("Title updated:", response.title);
                            $("#album-title").text(response.title);  // Update the displayed title
                            $("#album-title-input").hide();  // Hide the input field after saving
                            $("#album-title").show();  // Show the updated title
                        },
                        error: function(xhr, status, error) {
                            console.error('Error:', status, error);
                            alert('An error occurred while updating the album title.');
                        }
                    });
                } else {
                    // If no change is made, just hide the input field and show the title
                    $("#album-title-input").hide();  // Hide the input field without making a request
                    $("#album-title").show();  // Show the original title
                }
            });

            // Alternatively, if you want to update when Enter is pressed:
            $('#album-title-input').on('keypress', function(event) {
                if (event.key === "Enter") {
                    var newTitle = $(this).val().trim();  // Get the new title and trim any extra whitespace
                    var originalTitle = $("#album-title").text().trim(); // Get the original title from the element

                    if (newTitle !== originalTitle) {  // Only send the request if the title has changed

                        $.ajax({
                            url: "{% url 'update_album_title' album_id=album.id %}",
                            type: "POST",
                            data: {
                                'title': newTitle,  // The new title value
                                'csrfmiddlewaretoken': '{{ csrf_token }}'  // CSRF token
                            },
                            success: function(response) {
                                console.log("Title updated:", response.title);
                                $("#album-title").text(response.title);  // Update the displayed title
                                $("#album-title-input").hide();  // Hide the input field after saving
                                $("#album-title").show();  // Show the updated title
                            },
                            error: function(xhr, status, error) {
                                console.error('Error:', status, error);
                                alert('An error occurred while updating the album title.');
                            }
                        });
                    } else {
                        // If no change is made, just hide the input field and show the title
                        $("#album-title-input").hide();  // Hide the input field without making a request
                        $("#album-title").show();  // Show the original title
                    }
                }
            });

            // Trigger when the input loses focus (blur)
            $('#album-description-input').on('blur', function() {
                var newDescription = $(this).val().trim();  // Get the new description and trim any extra whitespace
                var originalDescription = $("#album-description").text().trim(); // Get the original description from the element

                if (newDescription !== originalDescription) {  // Only send the request if the description has changed
                    $.ajax({
                        url: "{% url 'update_album_description' album_id=album.id %}",
                        type: "POST",
                        data: {
                            'description': newDescription,  // The new description value
                            'csrfmiddlewaretoken': '{{ csrf_token }}'  // CSRF token
                        },
                        success: function(response) {
                            console.log("Description updated:", response.description);
                            $("#album-description").text(response.description);  // Update the displayed description
                            $("#album-description-input").hide();  // Hide the input field after saving
                            $("#album-description").show();  // Show the updated description
                        },
                        error: function(xhr, status, error) {
                            console.error('Error:', status, error);
                            alert('An error occurred while updating the album description.');
                        }
                    });
                } else {
                    // If no change is made, just hide the input field and show the description
                    $("#album-description-input").hide();  // Hide the input field without making a request
                    $("#album-description").show();  // Show the original description
                }
            });
        });