// app/static/js/script.js
// Функція для обробки форми реєстрації
// app/static/js/script.js

function extractErrorMessage(error) {
    // 1) Якщо detail - просто рядок
    if (typeof error.detail === 'string') {
        return error.detail;
    }

    // 2) Якщо detail - масив помилок валідації Pydantic
    if (Array.isArray(error.detail)) {
        return error.detail
            .map(e => e.msg || JSON.stringify(e))
            .join('\n');
    }

    // 3) Фолбек: показати весь об'єкт
    return JSON.stringify(error);
}

// --- РЕЄСТРАЦІЯ ---
const registerForm = document.getElementById('registerForm');
if (registerForm) {
    registerForm.addEventListener('submit', async function (e) {
        e.preventDefault();

        const formData = new FormData(this);
        const userData = {
            email: formData.get('email'),
            password: formData.get('password')
        };

        try {
            const response = await fetch('/register', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(userData)
            });

            if (response.ok) {
                alert('Користувач успішно зареєстрований!');
                window.location.href = '/login';
            } else {
                const error = await response.json();
                const msg = extractErrorMessage(error);
                alert(`Помилка реєстрації:\n${msg}`);
            }
        } catch (err) {
            console.error('Помилка під час реєстрації:', err);
            alert('Сталася неочікувана помилка під час реєстрації');
        }
    });
}

// Функція для обробки форми входу
document.getElementById('loginForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const formData = new FormData(this);
    const userData = {
        email: formData.get('email'),
        password: formData.get('password')
    };
    
    try {
        const response = await fetch('/token', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(userData)
        });
        
        if (response.ok) {
            const tokenData = await response.json();
            localStorage.setItem('access_token', tokenData.access_token); // Зберігаємо токен
            alert('Успішний вхід!');
            window.location.href = '/profile'; // Перенаправлення на сторінку профілю
        } else {
            const error = await response.json();
            alert(`Помилка входу: ${error.detail}`);
        }
    } catch (error) {
        console.error('Помилка під час входу:', error);
        alert('Сталася помилка під час входу');
    }
});
