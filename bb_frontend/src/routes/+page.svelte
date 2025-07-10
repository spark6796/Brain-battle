<script>
import { goto } from "$app/navigation";
import { gsap } from "gsap";
import { onMount } from 'svelte';


const api = import.meta.env.VITE_BACKEND_API
const protocol = import.meta.env.VITE_SSL_BOOL == 'TRUE' ? 'https' : 'http';

let mode = $state("host")
const pfp_list = Array.from({length: 5 + 1}, (_, i) => `pfp/${i}.jpg`);
let current_pfp = $state(pfp_list[Math.floor(Math.random()*pfp_list.length)]);

async function StartGame(event){
    document.getElementById('button').disabled = true
    event.preventDefault()
    const form = event.target;
    const username = form.querySelector('#name').value;
    const response = await fetch(`${protocol}://${api}/get_session`, {
        method: 'POST',
        body: JSON.stringify({username,current_pfp}),
    });
    const data = await response.json();
    const response_code = response.status
    if (response_code == 200){
        let session = data.sessionid
        sessionStorage.setItem('sessionid',session);
    }
    else
    {
        alert('Login Failed')
        window.location.reload();
        return
    }

    const session_id = sessionStorage.getItem('sessionid');
   
    let payload = { session_id };

    if (mode == 'join') {
        const game_id = window.prompt('Party CODE', '');
        if (!game_id) return goto('/');
        payload.game_id = game_id;
    }
    else {
        payload.mode = mode
        mode = 'host'
    }

    try {
        const apiUrl = `${protocol}://${api}/${mode}`;
        const response = await fetch(apiUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
        });

        if (!response.ok) {
        goto('/');
        }
    } catch {
        goto('/');
    }

    let main_cur = document.getElementById('cur').hidden = false
    let left_cur = document.getElementById('leftcur')
    let right_cur = document.getElementById('rightcur')
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
            onComplete: (()=>{
                goto('/game')
            })
        }
    )


}


function pfp_change(direction){
        let current_index = pfp_list.indexOf(current_pfp)
    
        if (direction == 'left'){
            if (current_index == 0){
                current_pfp = pfp_list[pfp_list.length-1]
            }
            else{
                current_pfp = pfp_list[current_index-1]
            }
        }
        else if (direction == 'right'){
            if (current_index == pfp_list.length-1){
                current_pfp = pfp_list[0]
            }
            else{
                current_pfp = pfp_list[current_index+1]
            }
        }
    }

</script>
 
<div class="appwidth:hidden h-screen w-full bg-gray-950 flex justify-center items-center text-6xl text-white text-center">
    Only for Big Screens
</div>


<div class="hidden absolute items-center appwidth:grid grid-cols-3 h-full min-w-full">
    <img src="leftbrain.png" alt="none" class="h-1/2 w-full"/>
    <div class="h-1/2 opacity-0 w-full border-2"></div>
    <img src="rightbrain.png" alt="none" class="h-1/2 w-full"/>
</div>
<div id="cur" hidden class="absolute z-40 text-slate-400 items-center grid grid-cols-2 h-full w-full overflow-hidden">
    <div id="leftcur" class="bg-blue-950 border-r-8 border-gray-900 h-full w-full opacity-0">
        <div class="flex justify-end font-bitcount text-9xl items-center w-full h-full">
            Brain
        </div>
    </div>
    <div id="rightcur" class="bg-blue-950 border-l-8 border-gray-900 h-full w-full opacity-0">
        <div class="flex justify-start pl-4 font-bitcount text-9xl items-center w-full h-full">
            Battle
        </div>
    </div>
</div>
<div class="h-screen hidden bg-main bg-no-repeat w-full appwidth:block">
    
    <div class="flex items-center justify-center text-8xl text-slate-200 animate-pulse pt-5 w-full h-1/6 font-bitcount">
        Brain Battle
    </div>
    <div class="w-full h-1/12 text-center font-mono text-xl text-white">
        Challange your brain
    </div>
    <div class="flex z-10 flex-col justify-center items-center h-1/4">
            <div class="flex w-1/7 h-4/6 justify-center items-center gap-9">
                <button onclick={()=>{pfp_change('left')}} class="text-5xl font-extrabold text-blue-100 animate-pulse hover:text-stone-300 mr-auto h-fit">&lt;</button>
                <img alt="pfp" src={current_pfp} class="border-4 h-full w-full rounded-full border-blue-900"/>
                <button onclick={()=>{pfp_change('right')}} class="text-5xl font-extrabold text-blue-100 animate-pulse hover:text-stone-300 ml-auto h-fit">&gt;</button>
            </div>
    </div>
    <div class="relative h-1/12 z-20  w-1/4 mx-auto"> 
        <div class="inline-flex w-full text-2xl font-bold text-slate-300 bg-blue-950 rounded">
            <button onclick={()=>{mode='host'}} class="{mode == 'host' ? 'border-4 border-gray-300' : ''} rounded-l w-full p-1">
              Host
            </button>
            <div class="border-2 border-blue-800"></div>
            <button onclick={()=>{mode='join'}} class="{mode == 'join' ? 'border-4 border-gray-300' : ''} rounded-r w-full p-1">
              Join
            </button>
        </div>
    </div>
    <div class="flex flex-col justify-center items-center h-1/4">
        <div class="relative z-20 h-full w-full">
            <div class="flex justify-center items-center h-full w-full">
                <form onsubmit={StartGame} class="flex h-2/3 w-1/4 items-center mx-auto gap-6">
                    <input id="name" required  maxlength="12" placeholder="Guest" class="bg-transparent focus:bg-none placeholder-slate-400 text-2xl focus:outline-none text-white border-b-2 border-b-zinc-300 w-2/3"/>
                    <button id="button" class="border-2 border-slate-700 font-bitcount hover:border-slate-400 bg-slate-900 w-1/3 h-1/2 text-2xl text-white rounded-lg animate-bounce">PLAY</button>
                </form>
            </div>
        </div>
    </div>
   
</div>