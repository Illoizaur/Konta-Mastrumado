// app/static/js/script.js

function extractErrorMessage(error) {
    if (typeof error.detail === 'string') {
        return error.detail;
    }

    if (Array.isArray(error.detail)) {
        return error.detail
            .map(e => e.msg || JSON.stringify(e))
            .join('\n');
    }

    return JSON.stringify(error);
}

// Функція для обробки форми реєстрації
// const registerForm = document.getElementById('registerForm');
// if (registerForm) {
//     registerForm.addEventListener('submit', async function (e) {
//         e.preventDefault();

//         const formData = new FormData(this);
//         const userData = {
//             email: formData.get('email'),
//             password: formData.get('password')
//         };

//         try {
//             const response = await fetch('/register', {
//                 method: 'POST',
//                 headers: {
//                     'Content-Type': 'application/json',
//                 },
//                 body: JSON.stringify(userData),
//                 credentials: 'include'
//             });

//             if (response.ok) {
//                 alert('Користувач успішно зареєстрований!');
//                 window.location.href = '/login';
//             } else {
//                 const error = await response.json();
//                 const msg = extractErrorMessage(error);
//                 alert(`Помилка реєстрації:\n${msg}`);
//             }
//         } catch (err) {
//             console.error('Помилка під час реєстрації:', err);
//             alert('Сталася неочікувана помилка під час реєстрації');
//         }
//     });
// }

// Функція для обробки форми входу

const loginForm = document.getElementById('loginForm');
if (loginForm) {
    loginForm.addEventListener('submit', async function (e) {
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
                body: JSON.stringify(userData),
                credentials: 'include'
            });

            if (response.ok) {
                const tokenData = await response.json();
                localStorage.setItem('access_token', tokenData.access_token);
                window.location.href = '/profile';
            } else {
                const error = await response.json();
                const msg = extractErrorMessage(error);
                alert(`Помилка входу:\n${msg}`);
            }
        } catch (err) {
            console.error('Помилка під час входу:', err);
            alert('Сталася неочікувана помилка під час входу');
        }
    });
}
