<script>
import { goto } from "$app/navigation";
import { gsap } from "gsap";
import { onMount } from 'svelte';

let question_categories = {
    '1':'Computers',
    '2':'Vehicles',
    '3':'Anime & Manga',
    '4':'Sports',
    '5':'Films'
}
let category_dropdown_boolean = $state(true)
let pop_up_message = $state()
let question = $state("Brain Battle")
let time_left = $state(30);
let round_number = $state(1);
let players = $state(
    {
        'playerid':{
            'points':10,
            'name':'Player 1',
            'pfp' :'2.jpg'
        },
        'playerid2':{
            'points':10,
            'name':'Player 2',
            'pfp' :'3.jpg'
        },'playerid3':{
            'points':10,
            'name':'Player 3',
            'pfp' :'4.jpg'
        },'playerid4':{
            'points':10,
            'name':'Player 4',
            'pfp' :'5.jpg'
        },'playerid5':{
            'points':10,
            'name':'Player 5',
            'pfp' :'1.jpg'
    }
}
);

let options = $state([])

onMount(()=>{
    sleep(3000).then(()=>{
        PopMessage('Round 1')
     })
    CurtainManager("open",true)
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

function StartGame(){
    CurtainManager('close')
    sleep(5000).then(()=>{
        let party_screen = document.getElementById('PartyScreen')
        party_screen.hidden = true
        let game_screen = document.getElementById('GameScreen')
        game_screen.hidden = false
        CurtainManager('open')
     })
    

}
function PopMessage(message){
    let pop_message_container = document.getElementById('popup_container');
    pop_message_container.hidden = false;
    pop_up_message = message;
     sleep(2000).then(()=>{
        gsap.to(pop_message_container,
            {
                opacity:0,
                duration:1,
                ease:'expo.out',
                onComplete: ()=>{
                    pop_message_container.hidden = true;
                }
            }
        )
     })
}

</script>

<div id="cur" class="absolute z-40 items-center grid grid-cols-2 h-full w-full overflow-hidden">
    <div id="leftcur" class="bg-blue-950 border-r-8 border-gray-900 h-full w-full">
        <div class="flex justify-end font-bitcount text-9xl items-center w-full h-full">
            Brain
        </div>
    </div>
    <div id="rightcur" class="bg-blue-950 border-l-8 border-gray-900 h-full w-full">
        <div class="flex justify-start pl-4 font-bitcount text-9xl items-center w-full h-full">
            Battle
        </div>
    </div>
</div>

<div id="PartyScreen" class="h-screen flex w-full bg-main bg-no-repeat overflow-hidden">
    <div class="flex h-full w-1/2">
        <div class="flex-row justify-center h-full w-full">
            <div class="flex justify-center items-center text-4xl h-1/6 text-white font-bitcount">
                PLAYERS {Object.entries(players).length}/5
            </div>
            <div class="grid h-5/6 w-1/2 mx-auto">
                {#each Object.entries(players) as [id, player]}
                    <div class="flex mx-auto items-center h-fit border-4 w-full rounded-4xl bg-indigo-800 border-blue-950">
                        <img src="pfp/{[player.pfp]}" alt="IMG" class="h-1/4 w-1/4 rounded-full">
                        <div class="flex text-white text-xl w-4/6 mx-auto">
                            {player.name}
                        </div>
                    </div>
                {/each}
            </div>

        
        
        </div>
  
    
    </div>
    <div class="h-full w-1/2">
        <div class="h-1/3 justify-between items-center w-full">
            
            <button onclick="{category_dropdown_boolean=!category_dropdown_boolean}" class="group border-4 mt-10 mx-auto border-blue-400 bg-blue-900 h-1/3 rounded-2xl w-5/6 flex justify-center items-center text-white font-bold font-bitcount text-xl">
                Select Questions Category
                <svg class="w-2.5 h-2.5 ms-3 {category_dropdown_boolean ? "rotate-180" : ''}" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 10 6">
                    <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="m1 1 4 4 4-4"/>
                </svg>
            </button>

            <div class="{category_dropdown_boolean ? 'relative' : 'hidden'} z-20 border-4 h-full overflow-x-hidden overflow-y-scroll border-slate-900  mx-auto rounded-b-lg  w-4/5  bg-blue-950">
                <ul class="p-3 space-y-1 text-sm text-gray-700 dark:text-gray-200" aria-labelledby="dropdownHelperButton">
                
                    {#each Object.entries(question_categories) as [id, category]}
                    
                            <li>
                                <div class="flex p-2 rounded-sm w-fit hover:bg-slate-900">
                                    <div class="flex items-center h-5">
                                        <input id="category-{id}-checkbox"  type="checkbox" value="" class="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded-sm focus:ring-blue-500 dark:focus:ring-blue-600 dark:ring-offset-gray-700 dark:focus:ring-offset-gray-700 focus:ring-2 dark:bg-gray-600 dark:border-gray-500">
                                    </div>
                                    <div class="ms-2 text-sm">
                                        <label for="category-{id}-checkbox" class="font-medium text-gray-300">
                                            {category}
                                        </label>
                                    </div>
                                </div>
                            </li>
                    
                    {/each}
                </ul>


            </div>

        </div>
        <div class="flex items-center justify-center h-2/3 w-full">
            <button onclick={StartGame()} class="border-4 border-blue-400 bg-blue-900 h-1/4 rounded-2xl w-1/3 flex justify-center items-center text-white font-bold font-bitcount text-3xl">
                Start
            </button>

        </div>
    </div>
</div>




<div id="GameScreen" hidden class="flex h-screen w-full bg-main bg-no-repeat overflow-hidden">

    <div id="popup_container" hidden class="absolute h-full backdrop-blur-md w-3/4 right-0"> 
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
                <div class="flex items-center h-1/8 w-full text-white text-xl  border-white">
                    <img src="pfp/{player.pfp}" alt='none' class="rounded-full h-full w-1/4"/>
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
                        <button class="border-3 p-4 w-fit mx-4 min-w-1/2 h-fit rounded-lg hover:border-blue-300 text-center border-blue-900 bg-indigo-950 shadow-2xl shadow-black text-xl text-slate-200">{option}</button>
                </div>
        {/each}
        </div>
        
    </div>



</div>