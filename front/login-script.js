const loginForm = document.getElementById('loginForm');

// 2. Intercept the submit event
loginForm.addEventListener('submit', async (event) => {
    // CRITICAL: Stop the browser from doing a traditional page reload
    event.preventDefault();

    // 3. Automatically extract the input data using the "name" attributes
    const formDataInstance = new FormData(loginForm);
    
    // 4. Convert it to the URL-encoded format FastAPI expects
    const urlEncodedData = new URLSearchParams(formDataInstance);

    // 5. Call your login logic and pass the formatted data
    await loginUser(urlEncodedData);
});

async function loginUser(urlEncodedData) {
    // 2. POST to your FastAPI endpoint (whether you named it /token or /login)
    try {
    const response = await fetch('/api/login', {
        method: 'POST',
        body: urlEncodedData
    });

    if (response.ok) {
        const data = await response.json();
        
        // 3. Save the token that FastAPI sent back
        localStorage.setItem('token', data.access_token);
        console.log("Logged in successfully!");
        window.location.href = '/agent-showcase-base.html';
    } else {
        const errorData = await response.json();
        alert(`Login failed: ${errorData.detail || 'Invalid credentials'}`);
    }
    } catch (error) {
        console.error("Network error:", error);
        alert("Something went wrong. Please try again later.");
    }
}