// Key-event handlers
let lastKeyDown = 0;
let lastKeyUp = 0;
let doubleClickDelta = 600;
let listenForUp = true;
// Eventlistener for keyboard event
document.addEventListener("keydown", function(e) {
  // Listen for keys A and N
  if (e.key == "Enter") {
    // sendItemPosition("Nikotin");
    handleEnterClick("down");
    console.log("keyDown");
  }
});

document.addEventListener("keyup", function(e) {
  if (e.key === "Enter") {
    handleEnterClick("up");
    console.log("keyUp");
  }
});

function checkForDoubleCLick() {
  // Register double click if double click

  window.setTimeout(function() {
    if (lastKeyDown > lastKeyUp) {
      sendItemPosition("Annat");
    } else {
      sendItemPosition("Nikotin");
    }
    setTimeout(function() {
      // Some extra time to release the button
      listenForUp = true;
    }, 300);
  }, doubleClickDelta);
}

function handleEnterClick(upOrDown) {
  let now = Date.now();
  if (upOrDown === "up" && listenForUp) {
    // Start listeing for doubleclick
    listenForUp = false;
    lastKeyUp = now;
    checkForDoubleCLick();
  } else if (upOrDown === "down") {
    lastKeyDown = now;
  }
}

//// GET DATA ////

function getFromServer(url, callback, cbArg = null) {
  xhttp = new XMLHttpRequest();
  xhttp.onreadystatechange = function() {
    if (this.readyState == 4 && this.status == 200) {
      if (cbArg !== null) {
        callback(cbArg);
      } else {
        callback();
      }
    }
  };
}

function displayData(data) {
  let items = { Nikotin: 0, Annat: 0 };
  for (let item of data) {
    let itemType = item[0];
    items[itemType] ? (items[itemType] += 1) : (items[itemType] = 1);
  }
  document.querySelector(
    "#data-nikotin"
  ).innerHTML = `Nikotin: ${items.Nikotin}`;
  document.querySelector("#data-annat").innerHTML = `Annat: ${items.Annat}`;
}

async function getData(sessionID = 0) {
  // Get all the data from the database?

  let req_url = "/get_data";
  if (sessionID) {
    req_url = "/get_session_items/" + sessionID;
  }
  let xhttp = new XMLHttpRequest();
  xhttp.onreadystatechange = function() {
    if (this.readyState == 4 && this.status == 200) {
      var res = JSON.parse(xhttp.response);
      displayData(res);
      // return res;
    }
  };
  xhttp.open("GET", req_url, true);
  xhttp.send();
}

function displayItemCount(itemCount) {
  document.querySelector(
    "#data-nikotin"
  ).innerHTML = `Nikotin: ${itemCount.Nikotin}`;
  document.querySelector("#data-annat").innerHTML = `Annat: ${itemCount.Annat}`;
}

function getSessionItemCount(sessionID = 0) {
  req_url = `/get_session_item_count/${sessionID}`;
  let xhttp = new XMLHttpRequest();
  xhttp.onreadystatechange = function() {
    if (this.readyState == 4 && this.status == 200) {
      var res = JSON.parse(xhttp.response);
      displayItemCount(res);
      // return res;
    }
  };
  xhttp.open("GET", req_url, true);
  xhttp.send();
}

function download(filename, text) {
  var element = document.createElement("a");
  element.setAttribute(
    "href",
    "data:text/plain;charset=utf-8," + encodeURIComponent(text)
  );
  element.setAttribute("download", filename);

  element.style.display = "none";
  document.body.appendChild(element);

  element.click();

  document.body.removeChild(element);
}

///// Send data to database /////

function getUTCDate() {
  return new Date()
    .toISOString()
    .replace("T", " ")
    .split(".")[0];
}

function sendItemPosition(type) {
  let dateTime = getUTCDate();
  console.log(dateTime);
  navigator.geolocation.getCurrentPosition(function(position) {
    item = {
      type: type,
      lat: position.coords.latitude,
      long: position.coords.longitude,
      datetime: dateTime,
      sessionID: sessionStorage.sessionID ? sessionStorage.sessionID : 0
    };
    sendItem(item);
  });
}

function sendItem(item) {
  var xhttp = new XMLHttpRequest();

  xhttp.onreadystatechange = function() {
    if (this.readyState == 4 && this.status == 200) {
      console.log("Sent data");
      document.querySelector(
        "#button-response"
      ).innerHTML = `type: ${item.type}, lat: ${item.lat}, long: ${item.long}, time: ${item.datetime}`;
      getSessionItemCount(sessionStorage.sessionID);
    }
  };
  xhttp.open("POST", "/item", true);
  xhttp.setRequestHeader("Content-Type", "application/json");
  xhttp.send(JSON.stringify(item));
}
