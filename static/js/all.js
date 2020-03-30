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

/// Request handling /////

function requestPromise(method, url, data = {}) {
  return new Promise(function(resolve, reject) {
    let req = new XMLHttpRequest();
    req.onreadystatechange = function() {
      if (req.readyState == 4) {
        if (req.status == 200) {
          resolve(req.responseText);
        } else {
          reject(req.status);
        }
      }
    };

    let asynced = true;
    req.open(method, url, asynced);
    // Handle sending
    if (method === "POST") {
      req.setRequestHeader("Content-Type", "application/json");
      req.send(JSON.stringify(data));
    } else if (method === "GET") {
      req.send();
    } else {
      console.log("Unrecognized method:", method);
    }
  });
}

//// GET DATA ////

// function getFromServer(url, callback, cbArg = null) {
//   xhttp = new XMLHttpRequest();
//   xhttp.onreadystatechange = function() {
//     if (this.readyState == 4 && this.status == 200) {
//       if (cbArg !== null) {
//         callback(cbArg);
//       } else {
//         callback();
//       }
//     }
//   };
// }

// function displayData(data) {
//   let items = { Nikotin: 0, Annat: 0 };
//   for (let item of data) {
//     let itemType = item[0];
//     items[itemType] ? (items[itemType] += 1) : (items[itemType] = 1);
//   }
//   document.querySelector(
//     "#data-nikotin"
//   ).innerHTML = `Nikotin: ${items.Nikotin}`;
//   document.querySelector("#data-annat").innerHTML = `Annat: ${items.Annat}`;
// }

// async function getData(sessionID = 0) {
//   // Get all the data from the database?

//   let req_url = "/get_data";
//   if (sessionID) {
//     req_url = "/get_session_items/" + sessionID;
//   }
//   let xhttp = new XMLHttpRequest();
//   xhttp.onreadystatechange = function() {
//     if (this.readyState == 4 && this.status == 200) {
//       var res = JSON.parse(xhttp.response);
//       displayData(res);
//       // return res;
//     }
//   };
//   xhttp.open("GET", req_url, true);
//   xhttp.send();
// }

function displayItemCount(itemCount) {
  document.querySelector(
    "#data-nikotin"
  ).innerHTML = `Nikotin: ${itemCount.Nikotin}`;
  document.querySelector("#data-annat").innerHTML = `Annat: ${itemCount.Annat}`;
}

// function getSessionItemCount(sessionID = 0) {
//   req_url = `/get_session_item_count/${sessionID}`;
//   let xhttp = new XMLHttpRequest();
//   xhttp.onreadystatechange = function() {
//     if (this.readyState == 4 && this.status == 200) {
//       var res = JSON.parse(xhttp.response);
//       displayItemCount(res);
//       // return res;
//     }
//   };
//   xhttp.open("GET", req_url, true);
//   xhttp.send();
// }

function updateItemCountPromise() {
  let sID = sessionStorage.sessionID ? sessionStorage.sessionID : "0";
  req_url = `/get_session_item_count/${sID}`;
  requestPromise("GET", req_url)
    .then(result => JSON.parse(result))
    .then(result => {
      displayItemCount(result);
    });
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
    // sendItem(item);
    sendItemPromise(item);
  });
}

// function sendItem(item) {
//   var xhttp = new XMLHttpRequest();

//   xhttp.onreadystatechange = function() {
//     if (this.readyState == 4 && this.status == 200) {
//       console.log("Sent data");
//       document.querySelector(
//         "#button-response"
//       ).innerHTML = `type: ${item.type}, lat: ${item.lat}, long: ${item.long}, time: ${item.datetime}`;
//       // getSessionItemCount(sessionStorage.sessionID);
//       updateItemCountPromise();
//     }
//   };
//   xhttp.open("POST", "/item", true);
//   xhttp.setRequestHeader("Content-Type", "application/json");
//   xhttp.send(JSON.stringify(item));
// }

function updateLastItemDisplay(item) {
  document.querySelector(
    "#button-response"
  ).innerHTML = `type: ${item.type}, lat: ${item.lat}, long: ${item.long}, time: ${item.datetime}`;
}

function sendItemPromise(item) {
  let method = "POST";
  let url = "item";
  let data = item;
  requestPromise(method, url, data)
    .then(() => {
      console.log("SIP => Sent data");
      updateLastItemDisplay(item);
      return;
    })
    .then(() => {
      console.log("SIP => updateItemCountPromise");
      updateItemCountPromise();
    });
}
