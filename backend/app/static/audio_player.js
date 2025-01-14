const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws';
const host = window.location.hostname;
const port = '8100';

const socket = new WebSocket(
  `${protocol}://${host}:${port}/websockets/audio`
);

socket.onopen = function () {
  console.log('WebSocket connection established.');
  socket.send(
    JSON.stringify({
      event: 'connect',
      data: window.location.pathname,
    })
  );
};

socket.onmessage = function (event) {
  try {
    const message = JSON.parse(event.data);
    console.log('Received message:', message);

    handleMessage(message);
  } catch (error) {
    console.error('Failed to parse JSON:', error);
  }
};

let channel_1_queue_elm = document.getElementById('channel1-queue');
let audio_data_1_elm = document.getElementById('audio-data-1');

let channel_2_queue_elm = document.getElementById('channel2-queue');
let audio_data_2_elm = document.getElementById('audio-data-2');

function handleMessage(message) {
  console.log('Processing message:', message);

  // Channel 1 Handling
  if (
    message.data &&
    message.data['channel-1'] &&
    message.data['channel-1'].current_audio
  ) {
    document.getElementById(
      'channel1-title'
    ).textContent = `Title: ${message.data['channel-1'].current_audio.title}`;
    document.getElementById(
      'channel1-artist'
    ).textContent = `Artist: ${message.data['channel-1'].current_audio.artist}`;
    document.getElementById(
      'channel1-position'
    ).textContent = `Position: ${message.data['channel-1'].current_audio.position}`;
  }

  // Channel 2 Handling
  if (
    message.data &&
    message.data['channel-2'] &&
    message.data['channel-2'].current_audio
  ) {
    document.getElementById(
      'channel2-title'
    ).textContent = `Title: ${message.data['channel-2'].current_audio.title}`;
    document.getElementById(
      'channel2-artist'
    ).textContent = `Artist: ${message.data['channel-2'].current_audio.artist}`;
    document.getElementById(
      'channel2-position'
    ).textContent = `Position: ${message.data['channel-2'].current_audio.position}`;
  }

  // Handling audio control events
  if (message.event === 'audio_control') {
    if (message.data.command === 'autoplay') {
      if (message.data.channel === 'channel-1') {
        audio_data_1_elm.style.display = 'flex';
      } else if (message.data.channel === 'channel-2') {
        audio_data_2_elm.style.display = 'flex';
      }
    }
  }

  // Channel 1 Queue Update
  if (
    message.data &&
    message.data['channel-1'] &&
    message.data['channel-1'].queue
  ) {
    channel_1_queue_elm.innerHTML = '';
    let ol = document.createElement('div');
    ol.classList.add('queue-list');
    ol.setAttribute('id', 'queue-list-1');
    message.data['channel-1'].queue.forEach((item) => {
      let li = document.createElement('span');
      li.classList.add('queue-item');
      li.textContent = item.title;
      ol.appendChild(li);
    });
    channel_1_queue_elm.appendChild(ol);
  }

  // Channel 2 Queue Update
  if (
    message.data &&
    message.data['channel-2'] &&
    message.data['channel-2'].queue
  ) {
    channel_2_queue_elm.innerHTML = '';
    let ol = document.createElement('div');
    ol.classList.add('queue-list');
    ol.setAttribute('id', 'queue-list-2');
    message.data['channel-2'].queue.forEach((item) => {
      let li = document.createElement('span');
      li.classList.add('queue-item');
      li.textContent = item.title;
      ol.appendChild(li);
    });
    channel_2_queue_elm.appendChild(ol);
  }
}

// Track volume levels
let volume1 = 50;
let volume2 = 50;

// Track fade states
let fadeIn1Active = false;
let fadeOut1Active = false;
let fadeIn2Active = false;
let fadeOut2Active = false;

// Volume sliders
const slider1 = document.getElementById('volume1');
const slider2 = document.getElementById('volume2');

slider1.addEventListener('mouseup', (event) => {
  const volume1 = event.target.value;
  console.log(`Channel 1 Volume: ${volume1}`);

  // Send WebSocket message for channel-1 volume change
  socket.send(
    JSON.stringify({
      event: 'audio_control',
      type: 'volume',
      data: {
        value: volume1,
        channel: 'channel-1',
      },
    })
  );
});

// Channel 2 volume change
slider2.addEventListener('mouseup', (event) => {
  const volume2 = event.target.value;
  console.log(`Channel 2 Volume: ${volume2}`);

  // Send WebSocket message for channel-2 volume change
  socket.send(
    JSON.stringify({
      event: 'audio_control',
      type: 'volume',
      data: {
        value: volume2,
        channel: 'channel-2',
      },
    })
  );
});
function toggleButtonState(button, isActive) {
  if (isActive) {
    button.classList.add('active');
  } else {
    button.classList.remove('active');
  }
}

let auto_play_button_1 = document.getElementById('auto-play-1');
let play_btn_1 = document.getElementById('play-btn-1');
let skip_btn_1 = document.getElementById('skip-btn-1');

let auto_play_button_2 = document.getElementById('auto-play-2');
let play_btn_2 = document.getElementById('play-btn-2');
let skip_btn_2 = document.getElementById('skip-btn-2');

// Channel 1 Autoplay button
auto_play_button_1.addEventListener('click', () => {
  auto_play_button_1.style.display = 'none';
  play_btn_1.style.display = 'flex';
  skip_btn_1.style.display = 'flex';

  socket.send(
    JSON.stringify({
      event: 'audio_control',
      data: 'auto_play',
      channel: 'channel-1',
    })
  );
});

// Channel 2 Autoplay button
auto_play_button_2.addEventListener('click', () => {
  auto_play_button_2.style.display = 'none';
  play_btn_2.style.display = 'flex';
  skip_btn_2.style.display = 'flex';

  socket.send(
    JSON.stringify({
      event: 'audio_control',
      data: 'auto_play',
      channel: 'channel-2',
    })
  );
});

// Toggle Fade In/Out buttons for Channel 1
document.getElementById('fadeIn1').addEventListener('click', () => {
  fadeIn1Active = !fadeIn1Active;
  toggleButtonState(
    document.getElementById('fadeIn1'),
    fadeIn1Active
  );
  socket.send(
    JSON.stringify({
      event: 'effects',
      data: {
        effect: 'fade_in',
        state: fadeIn1Active,
        channel: 'channel-1',
      },
    })
  );
  console.log(
    fadeIn1Active
      ? 'Channel 1 Fade In activated'
      : 'Channel 1 Fade In deactivated'
  );
});

document.getElementById('fadeOut1').addEventListener('click', () => {
  fadeOut1Active = !fadeOut1Active;
  toggleButtonState(
    document.getElementById('fadeOut1'),
    fadeOut1Active
  );
  socket.send(
    JSON.stringify({
      event: 'effects',
      data: {
        effect: 'fade_out',
        state: fadeOut1Active,
        channel: 'channel-1',
      },
    })
  );
  console.log(
    fadeOut1Active
      ? 'Channel 1 Fade Out activated'
      : 'Channel 1 Fade Out deactivated'
  );
});

// Toggle Fade In/Out buttons for Channel 2
document.getElementById('fadeIn2').addEventListener('click', () => {
  fadeIn2Active = !fadeIn2Active;
  toggleButtonState(
    document.getElementById('fadeIn2'),
    fadeIn2Active
  );
  socket.send(
    JSON.stringify({
      event: 'effects',
      data: {
        effect: 'fade_in',
        state: fadeIn2Active,
        channel: 'channel-2',
      },
    })
  );
  console.log(
    fadeIn2Active
      ? 'Channel 2 Fade In activated'
      : 'Channel 2 Fade In deactivated'
  );
});

document.getElementById('fadeOut2').addEventListener('click', () => {
  fadeOut2Active = !fadeOut2Active;
  toggleButtonState(
    document.getElementById('fadeOut2'),
    fadeOut2Active
  );
  socket.send(
    JSON.stringify({
      event: 'effects',
      data: {
        effect: 'fade_out',
        state: fadeOut2Active,
        channel: 'channel-2',
      },
    })
  );
  console.log(
    fadeOut2Active
      ? 'Channel 2 Fade Out activated'
      : 'Channel 2 Fade Out deactivated'
  );
});

// Play/Pause and Skip button functionality
document.querySelectorAll('.play-pause').forEach((button) => {
  button.classList.add('active');
  button.textContent = 'Pause';
  button.addEventListener('click', () => {
    const isActive = button.classList.contains('active');
    if (button.id === 'play-btn-1') {
      socket.send(
        JSON.stringify({
          event: 'audio_control',
          data: isActive ? 'pause' : 'play',
          channel: 'channel-1',
        })
      );
    } else if (button.id === 'play-btn-2') {
      socket.send(
        JSON.stringify({
          event: 'audio_control',
          data: isActive ? 'pause' : 'play',
          channel: 'channel-2',
        })
      );
    }
    toggleButtonState(button, !isActive);
    button.textContent = isActive ? 'Play' : 'Pause';
  });
});

document.querySelectorAll('.skip').forEach((button) => {
  button.addEventListener('click', () => {
    if (button.id === 'skip-btn-1') {
      socket.send(
        JSON.stringify({
          event: 'audio_control',
          data: 'skip',
          channel: 'channel-1',
        })
      );
    } else if (button.id === 'skip-btn-2') {
      socket.send(
        JSON.stringify({
          event: 'audio_control',
          data: 'skip',
          channel: 'channel-2',
        })
      );
    }
  });
});
