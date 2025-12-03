document.addEventListener("DOMContentLoaded", async () => {
    loadMenu();
});
async function loadMenu(){
    const response = await fetch("/api/getMyOptions");
    const data = await response.json();
    
    const menuButtonsContainer = document.createElement('div');
    menuButtonsContainer.className = 'menuBtnsContainer';
    data.forEach(a=>{
        const btn = document.createElement('button');
        btn.className = 'menuBtns';
        btn.textContent = a.text;
        btn.addEventListener("mouseenter", () => {btn.style.backgroundColor = "#868484ff"});
        btn.addEventListener("mouseleave", () => {btn.style.backgroundColor = "#fafafa"});
        btn.onclick = () => redirectF(a.href);
        menuButtonsContainer.appendChild(btn);
    });
    menu = document.getElementById("menu");
    menu.appendChild(menuButtonsContainer);
}

function redirectF(href){
    window.location.href = href;
}