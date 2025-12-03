let answer;

document.addEventListener("DOMContentLoaded", async () => {
    await loadQuestion();
    await controlButtons();
    await loadAllQuestionsIDs();
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
    answer = data.rightAnswer;
    data.answers.forEach(a=>{
        const btn = document.createElement('button');
        btn.className = 'button answers';
        btn.textContent = a.text;
        btn.qID = data.question_id;
        btn.id = a.id + 100000; //lAQIDs uses ID from question as well
        btn.onclick = () => {checkAnswer(btn)} //TODO Get answer working
        answerContainer.appendChild(btn);
    });
    try{ 
        sideBtn = document.getElementById(data.question_id);
        sideBtn.classList.remove('ansveredCorrect','ansveredWrong','unansvered', 'error');
    }catch (error) {console.log(error);}
    card.appendChild(questionContainer);
    card.appendChild(answerContainer);
}

async function checkAnswer(btn){
    answerButtons = document.querySelectorAll('.button.answers');
    answerButtons.forEach(button => {
        button.disabled = true;
    });

    if (btn.id -100000 == answer){
        btn.classList.add('ansveredCorrect');
                                
        //sidepanel color change
        sideBtn = document.getElementById(btn.qID);
        sideBtn.classList.remove('ansveredCorrect','ansveredWrong','unansvered', 'error');
        sideBtn.classList.add('ansveredCorrect');
    }
    else{
        //wrong answer color change
        btn.classList.add('ansveredWrong');

        //correct answer button color change
        correctButton = document.getElementById(answer+100000);
        correctButton.classList.add('ansveredCorrect');
        
        //sidepanel color change
        sideBtn = document.getElementById(btn.qID);
        sideBtn.classList.remove('ansveredCorrect','ansveredWrong','unansvered', 'error');
        sideBtn.classList.add('ansveredWrong');
    }
    updateStatus();
    selectedQ(btn);
}

function updateStatus(){
    const nodeListC = document.querySelectorAll('.ansveredCorrect.sidebutton');
    const itemsC = Array.from(nodeListC);
    const correctCount = itemsC.length;
    
    const nodeListW = document.querySelectorAll('.ansveredWrong.sidebutton');
    const itemsW = Array.from(nodeListW);
    const wrongCount = itemsW.length;
    
    const nodeListU = document.querySelectorAll('.unansvered.sidebutton');
    const itemsU = Array.from(nodeListU);
    const unansveredCount = itemsU.length;
    
    const statusLine = document.getElementById("status");
    statusLine.innerHTML=`Zodpovězeno ${correctCount + wrongCount} otázek z 
        ${correctCount + wrongCount + unansveredCount},<br>
        ${correctCount} správně, ${wrongCount} špatně,<br>
        úspěšnost ${((correctCount / (correctCount + wrongCount)) *100).toFixed(0)}%.`;
}

async function loadAllQuestionsIDs(){
    const response = await fetch("/api/getAllQuestionIDs");
    const data = await response.json();
    const allQContainer = document.createElement('div');
    data.forEach(a=>{
        const btn = document.createElement('button');
        btn.className = 'button questionIDs';
        btn.classList.add('error','sidebutton');
        //TODO check if notAnswered is working
        if (a.answeredY){btn.classList.add('ansveredCorrect');btn.classList.remove('error');};
        if (a.answeredW){btn.classList.add('ansveredWrong');btn.classList.remove('error');};
        if (a.notAnswered){btn.classList.add('unviewed');btn.classList.remove('error');}; 
        //TODO update API to send this data
        btn.textContent = a.id;
        btn.id = a.id;
        btn.onclick = () => {loadQuestion(btn.id);}
        if (a.active){btn.classList.add('active')}
        allQContainer.appendChild(btn);
    });
    const cont = document.getElementById('questionsList');
    cont.appendChild(allQContainer);  
    //updateStatus(); //uncomment when classes are implemened
}

function controlButtons(){
    const nextBtn = document.createElement('button');
    const backBtn = document.createElement('button');
    const menuBtn = document.createElement('button');

    nextBtn.textContent = "Další";
    backBtn.textContent = "Zpět";
    menuBtn.textContent = "Menu";

    nextBtn.className = "button next";
    menuBtn.className = "button return";
    backBtn.className = "button prev";

    nextBtn.onclick = () => goToNextQuestion();
    backBtn.onclick = () => goToPrevQuestion();
    menuBtn.onclick = () => goToMenu();
    const cont = document.getElementById('Control');

    cont.appendChild(backBtn);
    cont.appendChild(menuBtn);
    cont.appendChild(nextBtn);
}
function goToNextQuestion() {
    const current = document.querySelector(".questionIDs.active");
    if (!current) return;
    // console.log(current.classList.contains('ansveredWrong'));
    // if (current.classList.contains() === null) return;
    if(!current.classList.contains('ansveredCorrect') && !current.classList.contains('ansveredWrong')) {
        current.classList.add('unansvered');
    }
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

function selectedQ(qBtn){
    // try {
    //     const response = await fetch("/api/selectedA", {
    //         method: "POST",
    //         headers: {
    //             "Content-Type": "application/json" 
    //         },
    //         body: JSON.stringify({ 
    //             "aID":(btn.id - 1000) 
    //         })
    //     });
    //     data = await response.json();
    // } catch (error) {
    //     console.error("Error:", error);
    // }
    }