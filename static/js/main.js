document.addEventListener('DOMContentLoaded', function() {
    const userForm = document.getElementById('userForm');
    const resetFormButton = document.getElementById('resetForm');
    const usersTableBody = document.getElementById('usersTableBody');
    const loadingIndicator = document.getElementById('loadingIndicator');

    // Load users on page load
    loadUsers();

    // Form submission handler
    userForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        const userId = document.getElementById('userId').value;
        const userData = {
            name: document.getElementById('name').value,
            email: document.getElementById('email').value
        };

        try {
            if (userId) {
                await updateUser(userId, userData);
                showToast('User updated successfully!', 'success');
            } else {
                await createUser(userData);
                showToast('User created successfully!', 'success');
            }
            resetForm();
            loadUsers();
        } catch (error) {
            showToast(error.message || 'An error occurred', 'error');
        }
    });

    // Reset form handler
    resetFormButton.addEventListener('click', resetForm);

    // API Functions
    async function loadUsers() {
        showLoading(true);
        try {
            const response = await fetch('/users');
            const users = await response.json();
            renderUsers(users);
        } catch (error) {
            showToast('Failed to load users', 'error');
        }
        showLoading(false);
    }

    async function createUser(userData) {
        const response = await fetch('/users', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(userData)
        });
        if (!response.ok) throw new Error('Failed to create user');
        return response.json();
    }

    async function updateUser(userId, userData) {
        const response = await fetch(`/users/${userId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(userData)
        });
        if (!response.ok) throw new Error('Failed to update user');
        return response.json();
    }

    async function deleteUser(userId) {
        const response = await fetch(`/users/${userId}`, {
            method: 'DELETE'
        });
        if (!response.ok) throw new Error('Failed to delete user');
    }

    // UI Functions
    function renderUsers(users) {
        usersTableBody.innerHTML = users.map(user => `
            <tr>
                <td>${escapeHtml(user.name)}</td>
                <td>${escapeHtml(user.email)}</td>
                <td>${new Date(user.created_at).toLocaleString()}</td>
                <td>
                    <button class="btn btn-sm btn-primary btn-icon" onclick="editUser('${user.id}', '${escapeHtml(user.name)}', '${escapeHtml(user.email)}')">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn btn-sm btn-danger btn-icon" onclick="deleteUserHandler('${user.id}')">
                        <i class="fas fa-trash"></i>
                    </button>
                </td>
            </tr>
        `).join('');
    }

    function showLoading(show) {
        loadingIndicator.classList.toggle('d-none', !show);
    }

    function showToast(message, type) {
        const toastContainer = document.querySelector('.toast-container');
        const toast = document.createElement('div');
        toast.className = `toast toast-${type} show`;
        toast.setAttribute('role', 'alert');
        toast.innerHTML = `
            <div class="toast-body">
                ${message}
            </div>
        `;
        toastContainer.appendChild(toast);
        setTimeout(() => {
            toast.remove();
        }, 3000);
    }

    function resetForm() {
        userForm.reset();
        document.getElementById('userId').value = '';
    }

    function escapeHtml(unsafe) {
        return unsafe
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }

    // Make functions globally available
    window.editUser = function(id, name, email) {
        document.getElementById('userId').value = id;
        document.getElementById('name').value = name;
        document.getElementById('email').value = email;
    };

    window.deleteUserHandler = async function(id) {
        if (confirm('Are you sure you want to delete this user?')) {
            try {
                await deleteUser(id);
                showToast('User deleted successfully!', 'success');
                loadUsers();
            } catch (error) {
                showToast('Failed to delete user', 'error');
            }
        }
    };
});
