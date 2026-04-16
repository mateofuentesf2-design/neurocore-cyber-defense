const API_URL = "http://127.0.0.1:8000/login";

document.getElementById("loginForm").addEventListener("submit", async (e) => {
    e.preventDefault();

    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;

    try {
        const res = await fetch(API_URL, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ username, password })
        });

        if (!res.ok) {
            throw new Error("Login failed");
        }

        const data = await res.json();

        localStorage.setItem("token", data.access_token);

        window.location.href = "index.html";

    } catch (err) {
        alert("Invalid credentials");
        console.error(err);
    }
});