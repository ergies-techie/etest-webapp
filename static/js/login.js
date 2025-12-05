document.addEventListener("DOMContentLoaded", () => {
    const loginBtn = document.getElementById("register-save");
    const guestBtn = document.getElementById("guest-btn");
    loginBtn.addEventListener("mouseenter", () => {loginBtn.style.backgroundColor = "#3da8ff"});
    loginBtn.addEventListener("mouseleave", () => {loginBtn.style.backgroundColor = "#7ac3ff"});
    document.addEventListener("keydown", (evnt) => {if (evnt.key === "Enter"){
                                loginButtonClicked();
                                }
                            })

    loginBtn.addEventListener("click", loginButtonClicked); 
    
    guestBtn.addEventListener("mouseenter", () => {guestBtn.style.backgroundColor = "#3da8ff"});
    guestBtn.addEventListener("mouseleave", () => {guestBtn.style.backgroundColor = "#7ac3ff"});
    guestBtn.addEventListener("click", guestButtonClicked); 
    });

async function loginButtonClicked() {

        const username = document.getElementById("usernameReg").value;
        const password = document.getElementById("passwordReg").value;

        const response = await fetch("/api/login", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({username, password})
        });
        const result = await response.json();
        const msg = document.getElementById("msg");

        if(result.success) {
            msg.innerHTML = `<span style="color: green;">${result.message}</span>`;
            console.log(result.redirect)
            window.location.href = result.redirect;
        }
        else {
            msg.innerHTML = `<span style="color: red;">${result.error}</span>`;
        }
        };
async function guestButtonClicked(){
        let username = "guest";
        let password = "guest";
        const response = await fetch("/api/login", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({username, password})
        })
        
        const result = await response.json();
        if(result.success) {
            msg.innerHTML = `<span style="color: green;">${result.message}</span>`;
            console.log(result.redirect)
            window.location.href = result.redirect;
        }
        else {
            msg.innerHTML = `<span style="color: red;">${result.error}</span>`;
        }
}
const openBtn = document.getElementById('openPopup');
const closeBtn = document.getElementById('closePopup');
const overlay = document.getElementById('popupOverlay');

openBtn.onclick = () => {
    overlay.style.display = 'flex';
};

closeBtn.onclick = () => {
    overlay.style.display = 'none';
};

overlay.onclick = (e) => {
    if (e.target === overlay) {
        overlay.style.display = 'none';
    }
};

const registerSaveBtn = document.getElementById('register-save');
registerSaveBtn.onclick = async () => {
    const username = document.getElementById('usernameReg').value;
    const password = document.getElementById('passwordReg').value;
    overlay.style.display = 'none';

    const response = await fetch("/api/register", { //TODO create api/register route
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({username, password})
        });
        const result = await response.json();
        const msg = document.getElementById("msg");

        if(result.success) {
            msg.innerHTML = `<span style="color: green;">${result.message}</span>`;
            console.log(result.redirect)
            window.location.href = result.redirect;
        }
        else {
            msg.innerHTML = `<span style="color: red;">${result.error}</span>`;
        }
        };
