<script>
import { goto } from "$app/navigation";
import { gsap } from "gsap";
import { onMount } from 'svelte';

const api = import.meta.env.VITE_BACKEND_API
const protocol = import.meta.env.VITE_SSL_BOOL == 'TRUE' ? 'wss' : 'ws';

let socket;
let session_id;
let timer = null;
let im_leader = $state();
let options_disabled = $state(false)
let question_categories = $state({})
let category_change_trigger = $state(0);
let self_userid;
let party_code = $state()
let player_won_round = $state([])
let players_selected = $state([])
let category_dropdown_boolean = $state(true)
let pop_up_message = $state()
let question = $state("Brain Battle")
let time_left = $state(30);
let round_ended = $state(false)
let round_number = $state(1);
let players = $state({});
let leader_userid = $state();
let correct_option = $state()
let option_selected = $state()
let options = $state([])

$effect(()=>{
    if (leader_userid != self_userid){
        return
    }
    category_change_trigger
    if (socket){
        socket.send(JSON.stringify({
        category_change: question_categories,
        session: session_id
    }))
    }
})
function startTimer() {
    if (timer) return;
    timer = setInterval(() => {
      if (time_left > 0) {
        time_left--;
      } else {
        clearInterval(timer);
        timer = null;
      }
    }, 1000);
  }

function resetTimer() {
    clearInterval(timer);
    timer = null;
  }

function Initialize(){
    socket = new WebSocket(`${protocol}://${api}/join_game?session_id=${session_id}`);
    socket.onmessage = (event) => {
    let data = JSON.parse(event.data)
        if (data.action == "self_joined"){
            players = data.players
            self_userid = data.self_userid
            question_categories = data.categories
            party_code = data.game_id
            leader_userid = data.leader

            if (leader_userid == self_userid){
                im_leader = true
            }
            document.getElementById('PartyScreen').hidden = false
            CurtainManager('open',true)

            } 
        else if (data.action == "joined"){
                let name = data.name
                let pfp = data.pfp
                let userid = data.userid
                players[userid] = {name,pfp}
                } 

        else if (data.action == 'left'){
                let userid = data.userid
                delete players[userid];
                players = players
            }
        else if (data.action == 'category_update' && !im_leader){
            question_categories = data.categories
            }
        else if (data.action == 'kick'){
            alert('You were kicked')
            setTimeout(() => {
                goto('/')
            }, 1000)
        }
        else if (data.action == 'leader_left'){
            alert('Leader left the room')
            setTimeout(() => {
                goto('/')
            }, 1000)
        }
        else if (data.action == 'question'){
            round_ended = false
            time_left = 30;
            player_won_round = []
            correct_option = null
            option_selected = null
            options_disabled = false;
            round_number = data.round
            if (round_number == 1){
                StartGame()
                sleep(10000).then(()=>{
                resetTimer()
                startTimer()
            })
            }
            else{
                sleep(3000).then(()=>{
                resetTimer()
                startTimer()
            })
                PopMessage(`Round ${round_number}`,3)
            }
            sleep(2000).then(()=>{
                question = data.question
                options = data.options    
            })

            
            }
        else if (data.action == 'round_end'){
            resetTimer()
            players_selected = []
            round_ended = true
            correct_option = data.correct_answer
            let points_obj = data.points
            for (let player_id in points_obj){
                let before_points = players[player_id]['points']
                players[player_id]['points'] = points_obj[player_id]['points']
                let after_points = players[player_id]['points']
                if (before_points != after_points){
                    player_won_round.push(player_id)
                }
            }
        }
        else if (data.action == 'selected'){
            console.log(data)
            if (!players_selected.includes(data.selected)){
                players_selected.push(data.selected)
            }
        }
        else if (data.action == 'end'){
            PopMessage('Game Ended :)',0,true)
            sleep(2000).then(()=>{
                alert('Thanks for Playing!!')
                goto('/')
            })
        }
                
            };
            
            socket.onclose = () => {
                goto('/')
            };

            socket.onerror = () => {
                goto('/')
            };
    }

function sessionCheck(){
    session_id = sessionStorage.getItem('sessionid')
    if (session_id == null){
        alert('Invalid Session')
        goto('/')
        return
    }
    Initialize()
}

onMount(()=>{
    sessionCheck()
})

function CurtainManager(movement, hide_bool){
    let main_cur = document.getElementById('cur')
    let left_cur = document.getElementById('leftcur')
    let right_cur = document.getElementById('rightcur')
    main_cur.hidden = false
    if (movement == "open") {
        gsap.to(
            left_cur,
            {
                x:-1000,
                opacity:0,
                duration:4,
                ease: "expo.in",
            }
        )
        gsap.to(
            right_cur,
            {
                x:1000,
                opacity:0,
                duration:4,
                ease: "expo.in",
            }
        )
    }
    else{
        gsap.fromTo(
                left_cur,
                {
                    x:-1000,
                    opacity:0
                },
                {
                    x:0,
                    opacity:1,
                    duration:4,
                    ease: "expo.out",
                }
            )
            gsap.fromTo(
                right_cur,
                {
                    x:1000,
                    opacity:0
                },
                {
                    x:0,
                    opacity:1,
                    duration:4,
                    ease: "expo.out",
                }
            )
    }
    if (hide_bool){
        sleep(4000).then(()=>{
            main_cur.hidden = true
        })
    }
}

function sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

async function Kick(userid){
    let data = JSON.stringify({
        kick: userid,
        session: session_id
    })
    socket.send(data)
}


function SendOption(option){
    option_selected = option
    options_disabled = true
    let data = JSON.stringify({
        answer: option,
        session: session_id
    })
    socket.send(data)
}


function Start(){
    document.getElementById('start_button').disabled = true
    socket.send(JSON.stringify({
        start_game: true,
        session:session_id
    }))
}

function StartGame(){
    CurtainManager('close')
    sleep(5000).then(()=>{
        let party_screen = document.getElementById('PartyScreen')
        party_screen.hidden = true
        let game_screen = document.getElementById('GameScreen')
        game_screen.hidden = false
        CurtainManager('open',true)
        sleep(2000).then(()=>{
            PopMessage('Round 1',4)
        })
     })
    

}
function PopMessage(message, duration, permanent=false){
    let pop_message_container = document.getElementById('popup_container');
    pop_message_container.hidden = false;
    pop_message_container.style.opacity = 1
    pop_up_message = message;
    if (permanent) return
    sleep(2000).then(()=>{
        gsap.to(pop_message_container,
            {
                opacity:0,
                duration,
                ease:'expo.out',
                onComplete: ()=>{
                    pop_message_container.hidden = true;
                }
            }
        )
     })
}

</script>

<div id="cur" class="absolute z-40 items-center text-slate-400 grid grid-cols-2 h-full w-full overflow-hidden">
    <div id="leftcur" class="bg-blue-950 border-r-8 border-gray-900 h-full w-full">
        <div class="flex justify-end font-bitcount text-7xl items-center w-full h-full">
            Brain
        </div>
    </div>
    <div id="rightcur" class="bg-blue-950 border-l-8 border-gray-900 h-full w-full">
        <div class="flex justify-start pl-4 font-bitcount text-7xl items-center w-full h-full">
            Battle
        </div>
    </div>
</div>

<div hidden id="PartyScreen" class="h-screen flex w-full bg-main bg-no-repeat overflow-hidden">
    <div class="flex h-full w-1/2">
        <div class="flex-row justify-center h-full w-full">
            <div class="flex justify-center items-center text-4xl h-1/6 text-white font-bitcount">
                PLAYERS {Object.entries(players).length}/5
            </div>
            <div class="grid h-5/6 w-1/2 mx-auto">
                {#each Object.entries(players) as [id, player]}
                    <div class="flex mx-auto items-center h-fit border-4 w-full rounded-4xl bg-indigo-800 border-blue-950">
                        <img src={player.pfp} alt="IMG" class="h-1/4 w-1/4 rounded-full">
                        <div class="flex justify-center items-center text-white text-xl w-4/6 mx-auto">
                            {player.name}
                        </div>
                        <button onclick={Kick(id)} class="border-4 {leader_userid == id || !im_leader ? 'hidden' : ''} hover:border-red-500 rounded-2xl text-bold bg-red-500  text-red-600">✖</button>
                        <div class="{leader_userid == id ? '' : 'hidden'} pr-2">👑</div>
                    </div>
                {/each}
            </div>

        
        
        </div>
  
    
    </div>
    <div class="h-full w-1/2">
        <div class="h-1/3 justify-between items-center w-full">
            
            <button onclick={()=>category_dropdown_boolean=!category_dropdown_boolean} class="group border-4 mt-10 mx-auto border-blue-400 bg-blue-900 h-1/3 rounded-2xl w-5/6 flex justify-center items-center text-white font-bold font-bitcount text-xl">
                Select Questions Category
                <svg class="w-2.5 h-2.5 ms-3 {category_dropdown_boolean ? "rotate-180" : ''}" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 10 6">
                    <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="m1 1 4 4 4-4"/>
                </svg>
            </button>

            <div class="{category_dropdown_boolean ? 'relative' : 'hidden'} z-20 border-4 h-full overflow-x-hidden overflow-y-scroll border-slate-900  mx-auto rounded-b-lg  w-4/5  bg-blue-950">
                <ul class="p-3 space-y-1 text-sm text-gray-700 dark:text-gray-200" aria-labelledby="dropdownHelperButton">
                
                    {#each Object.entries(question_categories) as [category, enabled]}
                            <li>
                                <div class="flex p-2 rounded-sm w-fit hover:bg-slate-900">
                                    <div class="flex items-center h-5">
                                        <input onclick={()=>{question_categories[category]=!enabled;category_change_trigger++}} checked={enabled} disabled={!im_leader} id="category-{category}-checkbox"  type="checkbox" value="" class="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded-sm focus:ring-blue-500 dark:focus:ring-blue-600 dark:ring-offset-gray-700 dark:focus:ring-offset-gray-700 focus:ring-2 dark:bg-gray-600 dark:border-gray-500">
                                    </div>
                                    <div class="ms-2 text-sm">
                                        <label for="category-{category}-checkbox" class="font-medium text-gray-300">
                                            {category}
                                        </label>
                                    </div>
                                </div>
                            </li>
                    
                    {/each}
                </ul>


            </div>

        </div>
        <div class="flex flex-col items-center justify-center h-2/3 w-full">
            <div class="h-1/8 text-white font-bold text-2xl">CODE: {party_code}</div>
            <button id="start_button" disabled={!im_leader} onclick={()=>Start()} class="border-4 focus:border-blue-600 border-blue-400 bg-blue-900 h-1/4 rounded-2xl w-1/3 flex justify-center items-center text-white font-bold font-bitcount text-3xl">
                Start
            </button>

        </div>
    </div>
</div>


<!-- GAME SCREEN ---------------------------------------------------------- -->





<div hidden id="GameScreen" class="flex h-screen w-full bg-main bg-no-repeat overflow-hidden">

    <div id="popup_container" hidden class="absolute z-40 h-full backdrop-blur-md w-3/4 right-0"> 
        <div class="w-full font-bold font-bitcount text-white h-full flex justify-center items-center text-center text-6xl">
            {pop_up_message}
        </div>
    </div>

    <div class="border-r-8 border-blue-900 p-2 h-full bg-slate-950 w-1/3">
            <div class="flex items-center border-b-4 border-blue-800 h-1/8 w-full text-white text-4xl">
                <img src="favicon.png" alt='none' class="rounded-full h-full w-1/4"/>
                <div class="flex justify-center items-center h-full w-3/4">
                    <div class="flex text-2xl justify-center items-center border-4 text-slate-200 bg-blue-900 border-blue-500 font-bold font-serif w-3/4 rounded-2xl">
                        {round_number}/10
                    </div>
                </div>    

                <div class="flex justify-center items-center border-4 w-1/3 h-2/3 font-bold text-white text-xl  bg-blue-600 border-red-600 rounded-full">
                    {time_left}</div>                                   
            </div>
            
            <div class="flex justify-center font-bitcount text-2xl items-center text-white border-white h-1/10 w-full">
                LEADERBOARD
            </div>
            <!-- ----------- PLAYERS  -->


            {#each Object.entries(players) as [id, player]}
                <div class="flex mt-2 items-center h-1/8 w-full text-white text-xl {round_ended == false ? (players_selected.includes(id) ? 'border-2 border-yellow-500' : '') : ''}  {round_ended ? (player_won_round.includes(id) ? 'border-2 border-green-500' : 'border-2 border-red-500') : ''} rounded-full ">
                    <img src="{player.pfp}" alt='none' class="rounded-full h-full w-1/4"/>
                    <div class="truncate text-center h-1/2 w-3/4">
                        {player.name}
                    </div>
                    <div class="flex h-full w-1/3">
                        <div class="flex items-center justify-center font-mono">
                            {player.points}
                        </div>
                        <img class="h-1/2 my-auto" src="coin.png" alt="none">
                    </div>
                </div>
	        {/each}
            


    </div>

    <div class="flex-row h-full w-full">
        <div class="flex flex-col justify-end items-center text-slate-200 font-bold h-1/3 w-full">
            <div class="border-3 border-blue-950 m-2 my-auto rounded-lg px-5 p-2 text-xl w-fit font-mono text-center bg-blue-900">
                {question}
            </div>
        </div>
        <div class="grid grid-cols-2 grid-rows-2 w-full h-2/3 border-white">
        {#each options as option}
                <div class="flex justify-center items-center">
                        <button disabled={options_disabled} onclick="{()=>SendOption(option)}" class="border-3 focus:border-yellow-400 p-4 w-fit mx-4 min-w-1/2 h-fit rounded-lg {round_ended ? (correct_option == option ? 'bg-green-500': 'bg-red-600'): 'bg-indigo-950'} {option_selected == option ? 'border-yellow-400' : null} {options_disabled ? 'grayscale-75' : 'hover:border-blue-300'} text-center border-blue-900 shadow-2xl shadow-black text-xl text-slate-200">{option}</button>
                </div>
        {/each}
        </div>
        
    </div>



</div>