const socket = io();

const lobby = document.getElementById("lobby");
const roomList = document.getElementById("room-list");

const roomScreen = document.getElementById("room");
const roomCodeText = document.getElementById("room-code");
const gameStartBtn = document.getElementById("start-game");

const gameScreen = document.getElementById("game");
const submissionScreen = document.getElementById("submission-phase");
const simulationScreen = document.getElementById("simulation-phase");

const roleText = document.getElementById("role");
const gameEndBtn = document.getElementById("end-game");
const peekBtn = document.getElementById("choose-peek");
const travelBtn = document.getElementById("choose-travel");
const peekMenu = document.getElementById("peek-options");
const destinationMenu = document.getElementById("destination-options");
const departureMenu = document.getElementById("departure-options");
const submitDecisionBtn = document.getElementById("submit-decision");

document.getElementById("create-room").addEventListener("click", () => {
    socket.emit("create_room");
});

document.getElementById("leave-room").addEventListener("click", () => {
    socket.emit("leave_room");
});

gameStartBtn.addEventListener("click", () => {
    socket.emit("start_game");
});

gameEndBtn.addEventListener("click", () => {
    socket.emit("end_game"); 
});

peekBtn.addEventListener("click", () => {
    peekMenu.style.display = "block";
    destinationMenu.style.display = "none";
    departureMenu.style.display = "none";
});

travelBtn.addEventListener("click", () => {
    peekMenu.style.display = "none";
    destinationMenu.style.display = "block";
    departureMenu.style.display = "block";
});

submitDecisionBtn.addEventListener("click", () => {
    const actionMode =  document.querySelector('input[name="action-mode"]:checked')?.value ?? null;
    const peekTarget =  document.querySelector('input[name="peek-target"]:checked')?.value ?? null;
    const destination = document.querySelector('input[name="destination-target"]:checked')?.value ?? null;
    const departure =   document.querySelector('input[name="departure-time"]:checked')?.value ?? null;

    socket.emit("submit_decision", {
        "action_mode": actionMode,
        "peek_target": peekTarget,
        "destination": destination,
        "departure":   departure
    })
});


function setupSubmissionPhase(data){
    lobby.style.display = "none";
    roomScreen.style.display = "none";
    gameScreen.style.display = "block";

    submissionScreen.style.display = "block";
    simulationScreen.style.display = "none";
    
    if (data.is_alive){
        roleText.textContent = data.role;
        submitDecisionBtn.disabled = false;
    } else{
        roleText.textContent = "dead";
        submitDecisionBtn.disabled = true;
    }

    if (data.is_host) gameEndBtn.style.display = "block";
    else gameEndBtn.style.display = "none";

    peekMenu.innerHTML = "";
    for (const sid of data.peek_targets){
        const lab = document.createElement("label");
        const inp = document.createElement("input");
        
        inp.type = "radio";
        inp.name = "peek-target";
        inp.value = sid;
        
        lab.appendChild(inp);
        lab.append(`Peek at ${sid}`);

        peekMenu.appendChild(lab);
        peekMenu.appendChild(document.createElement("br"));
    }

    destinationMenu.innerHTML = "";
    for (const sid of data.destinations){
        const lab = document.createElement("label");
        const inp = document.createElement("input");
        
        inp.type = "radio";
        inp.name = "destination-target";
        inp.value = sid;
        
        lab.appendChild(inp);
        lab.append(`Travel for ${sid}`);

        destinationMenu.appendChild(lab);
        destinationMenu.appendChild(document.createElement("br"));
    }
}

function setupSimulationPhase(data){
    lobby.style.display = "none";
    roomScreen.style.display = "none";
    gameScreen.style.display = "block";

    submissionScreen.style.display = "none";
    simulationScreen.style.display = "block";

    simulationScreen.innerHTML = "";
    for (const sid of data.deaths){
        const p = document.createElement("p");
        p.textContent = `${sid} has died tonight.`;

        simulationScreen.appendChild(p);
    }

    const ul = document.createElement("ul");
    for (const msg of data.observations){
        const li = document.createElement("li");
        li.textContent = msg;

        ul.appendChild(li);
    }
    simulationScreen.append(ul);
}


socket.on("error", (data) => {
    console.log(data.msg);
})

socket.on("rooms_list", (rooms) => {
    roomList.innerHTML = "";

    for (const [code, room] of Object.entries(rooms)) {
        const btn = document.createElement("button");

        btn.textContent = `${code} (${room.players} players)`;

        btn.onclick = () => {
            socket.emit("join_room", { code });
        };

        roomList.appendChild(btn);
    }
});

socket.on("joined_room", (data) => {
    lobby.style.display = "none";
    roomScreen.style.display = "block";
    gameScreen.style.display = "none";

    roomCodeText.textContent = data.code;

    if (data.is_host) gameStartBtn.style.display = "block";
    else gameStartBtn.style.display = "none";
});

socket.on("left_room", () => {
    lobby.style.display = "block";
    roomScreen.style.display = "none";
    gameScreen.style.display = "none";
});

socket.on("start_submissions", (data) => {
    setupSubmissionPhase(data);
});

socket.on("start_simulation", (data) => {
    setupSimulationPhase(data);
});

socket.on("submission_accepted", () => {
    submitDecisionBtn.disabled = true;
});

socket.on("game_ended", () => {
    lobby.style.display = "block";
    roomScreen.style.display = "none";
    gameScreen.style.display = "none";
});
