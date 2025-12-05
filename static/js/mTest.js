let myAnswers = []; // [questionID, answerID, rightAnswer]
let currentQuestionID;
let testFinished = false;

document.addEventListener("DOMContentLoaded", async () => {
    await getTenQIDs();
    await loadQuestion(currentQuestionID);
    await controlButtons();
    
});

async function loadQuestion(qid = null){
    const prev = document.querySelector(".questionIDs.active");
    if(prev){prev.classList.remove("active");}
    const current = document.getElementById(qid);
    if(current){current.classList.add("active");}
    let data;
    try {
        const response = await fetch("/api/getThisQuestion", {
            method: "POST",
            headers: {
                "Content-Type": "application/json" 
            },
            body: JSON.stringify({ 
                "qid":qid 
            })
        });
        data = await response.json();
    } catch (error) {
        console.error("Error:", error);
    }
    card = document.getElementById("QA");
    card.innerHTML = "";
    
    const questionContainer = document.createElement('div');
    const answerContainer = document.createElement('div');
    questionContainer.className = 'question';
    questionContainer.textContent = data.question;
    
    data.answers.forEach(a=>{
        const btn = document.createElement('button');
        btn.className = 'button answers';
        btn.textContent = a.text;
        btn.questionID = data.question_id;
        btn.rightAnswer = data.rightAnswer;
        btn.id = a.id + 1000000; 

        const answered = myAnswers.find(ans => ans[0] == data.question_id);
           
        if(answered){ 
                if(answered[1] == a.id){
                    btn.classList.add("selectedAnswer");
       }}

        if(testFinished){   
            btn.disabled = true;
            if(answered){ 
                console.log(answered[2], a.id);
                if(answered[2] == a.id){
                    btn.classList.remove("selectedAnswer");
                    btn.classList.add("ansveredCorrect");
                }
                if(btn.classList.contains("selectedAnswer")){
                    btn.classList.remove("selectedAnswer");
                    btn.classList.add("ansveredWrong");
                }
            }}
        btn.onclick = () => {checkAnswer(btn)} 
        answerContainer.appendChild(btn);
    });
    card.appendChild(questionContainer);
    card.appendChild(answerContainer);
}

async function checkAnswer(btn){
    const previouslySelected = document.querySelector(".answers.selectedAnswer");
    if(previouslySelected){
        previouslySelected.classList.remove("selectedAnswer");
    }
    btn.classList.add("selectedAnswer");
    answerButtons = document.querySelectorAll('.button.answers');
    answerButtons.forEach(button => {
        button.disabled = true;
    });

        
    sideBtn = document.getElementById(btn.questionID);
    sideBtn.classList.add('selectedAnswer');
    
    myAnswers = myAnswers.filter(ans => ans[0] != btn.questionID);
    myAnswers.push([btn.questionID, btn.id - 1000000, btn.rightAnswer])
}

function updateStatus(){
    const nodeListC = document.querySelectorAll('.ansveredCorrect.questionIDs');
    const itemsC = Array.from(nodeListC);
    const correctCount = itemsC.length;
    
    const nodeListW = document.querySelectorAll('.ansveredWrong.questionIDs');
    const itemsW = Array.from(nodeListW);
    const wrongCount = itemsW.length;
    
    const nodeListU = document.querySelectorAll('.unansvered.questionIDs');
    const itemsU = Array.from(nodeListU);
    const unansveredCount = itemsU.length;
    
    const statusLine = document.getElementById("status");
    statusLine.innerHTML=`Celkem zodpovězeno ${correctCount + wrongCount} otázek <br>
        ${correctCount} správně, ${wrongCount} špatně<br>
        úspěšnost ${((correctCount / (correctCount + wrongCount)) *100).toFixed(0)}%`;
}

function controlButtons(){
    const nextBtn = document.createElement('button');
    const backBtn = document.createElement('button');
    const menuBtn = document.createElement('button');

    nextBtn.textContent = "Další";
    backBtn.textContent = "Zpět";
    menuBtn.textContent = "Vyhodnotit test";

    nextBtn.className = "button next";
    menuBtn.className = "button return";
    backBtn.className = "button prev";

    nextBtn.onclick = () => goToNextQuestion();
    backBtn.onclick = () => goToPrevQuestion();
    menuBtn.onclick = () => evaluateTest(menuBtn); 
    const cont = document.getElementById('Control');

    cont.appendChild(backBtn);
    cont.appendChild(menuBtn);
    cont.appendChild(nextBtn);
}
function goToNextQuestion() {
    const current = document.querySelector(".questionIDs.active");
    if (!current) return;
    const next = current.nextElementSibling;  
    if (!next) return; 
    loadQuestion(next.id);
}
function goToPrevQuestion(){
    const current = document.querySelector(".questionIDs.active");
    if (!current) return;
    const prev = current.previousElementSibling;  
    if (!prev) return; 
    loadQuestion(prev.id);
}
function goToMenu(){
    window.location.href = "/dashboard";
}

function saveAnswer(){
    let questionID;
    let answerID;

    questionID = document.querySelector(".questionIDs.active");
    questionID = questionID.id;

    answerID = document.querySelector(".answers.selectedAnswer");
    answerID = answerID.id;
}
async function getTenQIDs(){
    let questionsNos = 1;
    const response = await fetch("/api/getTenQuestionsIDs");
    const data = await response.json();
    const allQContainer = document.createElement('div');
    data.forEach(a=>{
        
        const btn = document.createElement('button');
        btn.className = 'button questionIDs notAnsvered';
        if (questionsNos == 1){btn.classList.add('active');
            currentQuestionID = a.id;
        }
        btn.textContent = questionsNos;
        questionsNos += 1;
        btn.id = a.id;
        btn.onclick = () => {loadQuestion(btn.id);}
        allQContainer.appendChild(btn);
    });
    const cont = document.getElementById('questionsList');
    cont.appendChild(allQContainer);  
}

async function evaluateTest(menuBtn){
    testFinished = true;    
    const elements = Array.from(document.getElementsByClassName('notAnsvered'));
    elements.forEach(e => {e.classList.remove('notAnsvered'); e.classList.add('unansvered');});
    await myAnswers.forEach(a =>{
        sideBtn = document.getElementById(a[0]);
        sideBtn.classList.remove('selectedAnswer', 'unansvered');
        if(a[1] == a[2]){
            
            sideBtn.classList.add('ansveredCorrect');
        }
        else{
            sideBtn.classList.add('ansveredWrong');
        }
    });
    menuBtn.textContent = "Menu";
    menuBtn.onclick = () => goToMenu();
    updateStatus();
}