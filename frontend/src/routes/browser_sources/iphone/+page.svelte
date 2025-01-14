<script>
  import { DeviceMockup } from 'flowbite-svelte';
</script>


<main class="bg-slate-900 flex flex-col flex-1 h-screen overflow-clip">
  <div class="mockup-phone">
    <div class="camera"></div>
    <div class="display">
      <div class="skeletonNotification">
        <div class="w-full h-full" id="page-container">
          <div class="w-[350px] min-h-[300px] mx-auto mt-[50px]" id="dialog-container">
            <div class="relative min-h-[80px] max-h-[180px] rounded-[10px] mb-2 overflow-hidden shadow-[0_2px_5px_rgba(0,0,0,0.06)]">
              <div class="absolute h-full w-full bg-white/80"></div>
              <div class="h-[25px] relative text-black">
                <div class="absolute h-full w-full bg-white/80"></div>
                <div class="inherit relative text-sm">
                  <div class="float-left text-left w-max py-[3px] pl-[10px]">
                    <i class="far fa-comment"></i> iMessage
                  </div>
                  <div class="float-right text-right w-max py-[3px] pr-[10px]">
                    Sun 1:20 pm
                  </div>
                </div>
              </div>
              <div class="inherit relative text-sm px-[10px] py-2 pr-5 h-max">
                <strong>
                  Nathan D
                </strong>
                <br/>
                Yeah, that's sound with me. I'll see you in 10
              </div>
            </div>
          </div>
          <span class="text-sm absolute bottom-2 right-2"><i class="far fa-smile-wink"></i></span>
        </div>
      </div>
    </div>
  </div>
</main>

