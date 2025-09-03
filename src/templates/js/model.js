document.addEventListener('DOMContentLoaded', function () {
    var saveBtn = document.getElementById('saveModelBtn');
    var form = document.getElementById('createModelForm');

    saveBtn.addEventListener('click', function (e) {
        // Use HTML5 form validation
        if (!form.checkValidity()) {
            e.preventDefault();
            e.stopPropagation();

            // Collect error messages
            var errors = [];
            var elements = form.elements;
            for (var i = 0; i < elements.length; i++) {
                var el = elements[i];
                if (!el.checkValidity()) {
                    if (el.validationMessage) {
                        var label = form.querySelector('label[for="' + el.id + '"]');
                        var fieldName = label ? label.textContent : el.name;
                        errors.push(fieldName + ': ' + el.validationMessage);
                    }
                }
            }
            form.classList.add('was-validated');
            return false;
        } else {
            // Submit the form via AJAX to stay on the current page and display errors or success notification
            document.getElementById('loaddingAction').hidden = false;
            var formData = new FormData(form);
            var xhr = new XMLHttpRequest();
            xhr.open('POST', form.action, true);
            xhr.setRequestHeader('X-Requested-With', 'XMLHttpRequest');

            // Remove any previous alerts
            var oldAlert = document.getElementById('serverFormAlert');
            if (oldAlert) oldAlert.remove();

            xhr.onload = function () {
                // Try to parse JSON response
                var response = {};
                try {
                    response = JSON.parse(xhr.responseText);
                } catch (e) { }

                // Unhide the loading spinner

                // Create alert element
                var alertDiv = document.createElement('div');
                alertDiv.id = 'serverFormAlert';
                alertDiv.classList.add('alert', 'mt-2');

                if (xhr.status >= 200 && xhr.status < 300) {
                    // Success
                    alertDiv.classList.add('alert-success');
                    alertDiv.textContent = response.message || 'Model registered successfully!';
                    // Optionally, reset the form
                    form.reset();
                    form.classList.remove('was-validated');
                    // Optionally, reload the page or update the table dynamically
                    setTimeout(function () {
                        location.reload();
                    }, 1200);
                } else {
                    // Error
                    alertDiv.classList.add('alert-danger');
                    // Remove previous field error messages
                    var oldFieldErrors = form.querySelectorAll('.invalid-feedback.server-error');
                    oldFieldErrors.forEach(function (feedback) {
                        feedback.remove();
                    });

                    // Set error messages from response to corresponding fields
                    if (xhr.status === 400 && typeof response === 'object' && response !== null) {
                        Object.keys(response).forEach(function (fieldName) {
                            var field = form.querySelector('[name="' + fieldName + '"]');
                            if (field) {
                                // Mark field as invalid
                                field.classList.add('is-invalid');
                                // Create error message element
                                var feedback = document.createElement('div');
                                feedback.className = 'invalid-feedback server-error';
                                feedback.textContent = Array.isArray(response[fieldName]) ? response[fieldName][0] : response[fieldName];
                                // Insert after the field
                                if (field.parentNode) {
                                    // If already has a feedback, remove it
                                    var next = field.nextElementSibling;
                                    if (next && next.classList.contains('invalid-feedback')) {
                                        next.remove();
                                    }
                                    field.parentNode.insertBefore(feedback, field.nextSibling);
                                }
                            }
                        });
                        form.classList.add('was-validated');
                        alertDiv.textContent = 'Please correct the errors above.';
                    } else {
                        alertDiv.textContent = response.message || 'An error occurred. Please try again.';
                    }
                }
                // Insert alert before modal footer
                var modalBody = form.querySelector('.modal-body');
                modalBody.parentNode.insertBefore(alertDiv, modalBody.nextSibling);
                document.getElementById('loaddingAction').hidden = true;
            };

            xhr.onerror = function () {
                var alertDiv = document.createElement('div');
                alertDiv.id = 'serverFormAlert';
                alertDiv.className = 'alert alert-danger mt-2';
                alertDiv.textContent = 'Network error. Please try again.';
                var modalBody = form.querySelector('.modal-body');
                modalBody.parentNode.insertBefore(alertDiv, modalBody.nextSibling);
                document.getElementById('loaddingAction').hidden = true;
            };

            xhr.send(formData);
        }
    });

    // Add delete action to delete button
    document.querySelectorAll('.btn-delete-model').forEach(function (btn) {
        btn.addEventListener('click', function (e) {
            e.preventDefault();
            var modelId = btn.getAttribute('modelId');
            if (!modelId) return;

            Swal.fire({
                title: 'Are you sure?',
                text: "Are you sure you want to delete this model?",
                icon: 'warning',
                showCancelButton: true,
                confirmButtonColor: '#d33',
                cancelButtonColor: '#3085d6',
                confirmButtonText: 'Yes, delete it!',
                reverseButtons: true
            }).then((result) => {
                if (!result.isConfirmed) {
                    return;
                }
                // Continue with delete logic below
                var xhr = new XMLHttpRequest();
                xhr.open('DELETE', '/orchestrator/model/' + modelId + "/", true);
                xhr.setRequestHeader('X-Requested-With', 'XMLHttpRequest');
                // CSRF token for Django
                var csrftoken = null;
                var cookies = document.cookie.split(';');
                for (var i = 0; i < cookies.length; i++) {
                    var c = cookies[i].trim();
                    if (c.startsWith('csrftoken=')) {
                        csrftoken = c.substring('csrftoken='.length, c.length);
                        break;
                    }
                }
                if (csrftoken) {
                    xhr.setRequestHeader('X-CSRFToken', csrftoken);
                }

                xhr.onload = function () {
                    if (xhr.status === 204 || xhr.status === 200) {
                        // Remove the row from the table
                        var row = btn.closest('tr');
                        if (row) {
                            row.remove();
                        }
                    } else {
                        var response = {};
                        try {
                            response = JSON.parse(xhr.responseText);
                        } catch (e) { }
                        Swal.fire('Error', response.message || 'Failed to delete model.', 'error');
                    }
                };

                xhr.onerror = function () {
                    Swal.fire('Error', 'Network error. Please try again.', 'error');
                };

                xhr.send();
            });
            return;
        });
    });

    // Handle update server button click
    document.querySelectorAll('.btn-update-model').forEach(function(btn) {
        btn.addEventListener('click', function() {
            var row = btn.closest('tr');
            if (!row) return;
            var modelId = btn.getAttribute('modelId');
            form.elements['id'].value = modelId;
            
            var modal = document.getElementById('createModelModal');

            // Get values from the row's cells
            // Table columns: #, Name, Type, HTTP URL, GRPC URL, Metrics URL, Status, Action
            var cells = row.querySelectorAll('td');
            if (cells.length < 8) return;

            // Set form fields
            form.elements['name'].value = cells[1].textContent.trim();
            // Type: get the text inside the badge
            var typeBadge = cells[2].querySelector('.badge');
            if (typeBadge) {
                form.elements['type'].value = typeBadge.textContent.trim();
            }
            var numInstance = cells[3].querySelector('td');
            if (numInstance) {
                form.elements['instance_num'].value = numInstance.textContent.trim();
            }
            var deployAlgorithm = cells[4].querySelector('span');
            if (deployAlgorithm) {
                form.elements['deploy_algorithm'].value = deployAlgorithm.getAttribute('value').trim();
            }
            var routingAlgorithm = cells[5].querySelector('span');
            if (routingAlgorithm) {
                form.elements['routing_algorithm'].value = routingAlgorithm.getAttribute('value').trim();
            }

            // Show the modal (Bootstrap 4/5 compatible)
            if (typeof $ !== 'undefined' && typeof $.fn.modal === 'function') {
                $('#createModelModal').modal('show');
            } else if (modal && typeof bootstrap !== 'undefined' && bootstrap.Modal) {
                var bsModal = bootstrap.Modal.getOrCreateInstance(modal);
                bsModal.show();
            } else {
                modal.style.display = 'block';
            }
        });
    });
});
