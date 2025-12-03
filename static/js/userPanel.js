document.addEventListener("DOMContentLoaded", async () => {
    const userDetails = document.getElementById("userName");
    userDetails.innerHTML = await getUserDetails();
    const logoutBtn = document.getElementById("logout");
    logoutBtn.addEventListener("click", logout);
});

async function getUserDetails(){
    try{
        const response = await fetch("/api/getUserName");
        if (!response.ok){
            throw new Error("Network response NOK")
        }
        const data = await response.json();
        const username = data.userName;
        return username;
    } catch (error) {
        console.log("error", error);
    }
}

async function logout() {
        const response = await fetch("/api/logout");   
        const result = await response.json();
        if (result.success) {window.location.href = result.redirect;}
}