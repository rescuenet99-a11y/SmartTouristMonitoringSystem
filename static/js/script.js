/* ===========================================
   SMART TOURIST SAFETY MONITORING SYSTEM
   LESSON 4 - PART 1
   Route Database
=========================================== */

const routeData = {

    "Mayiladuthurai": {

        "Chennai": {
            distance: "281 KM",
            transport: ["Train", "Bus", "Car"],
            time: {
                Train: "5 Hours 20 Minutes",
                Bus: "6 Hours",
                Car: "5 Hours"
            }
        },

        "Trichy": {
            distance: "145 KM",
            transport: ["Train", "Bus", "Car"],
            time: {
                Train: "2 Hours 30 Minutes",
                Bus: "3 Hours",
                Car: "2 Hours 45 Minutes"
            }
        }

    },

    "Chennai": {

        "Madurai": {
            distance: "462 KM",
            transport: ["Train", "Bus", "Flight", "Car"],
            time: {
                Train: "7 Hours",
                Bus: "8 Hours",
                Flight: "1 Hour 10 Minutes",
                Car: "7 Hours"
            }
        },

        "Delhi": {
            distance: "2180 KM",
            transport: ["Flight", "Train"],
            time: {
                Flight: "2 Hours 45 Minutes",
                Train: "30 Hours"
            }
        },

        "Mayiladuthurai": {
            distance: "281 KM",
            transport: ["Train", "Bus", "Car"],
            time: {
                Train: "5 Hours 20 Minutes",
                Bus: "6 Hours",
                Car: "5 Hours"
            }
        }

    },

    "Madurai": {

        "Rameswaram": {
            distance: "173 KM",
            transport: ["Train", "Bus", "Car"],
            time: {
                Train: "3 Hours",
                Bus: "3 Hours 30 Minutes",
                Car: "3 Hours"
            }
        }

    }

};


/* ===========================================
   Helper Function
=========================================== */

function clearTransport(){

    document.getElementById("transport_mode").innerHTML =
    "<option value=''>Select Transport</option>";

    document.getElementById("distance").innerHTML =
    "Select Source & Destination";

    document.getElementById("travel_time").innerHTML =
    "Select Source & Destination";

}
/* ===========================================
   LESSON 4 - PART 2
   Update Transport
=========================================== */

function updateTransport() {

    let source = document.getElementById("source_location").value;

    let destination = document.getElementById("destination").value;

    let transport = document.getElementById("transport_mode");

    let distance = document.getElementById("distance");

    let time = document.getElementById("travel_time");

    transport.innerHTML = "<option value=''>Select Transport</option>";

    distance.innerHTML = "Select Source & Destination";

    time.innerHTML = "Select Source & Destination";

    if(source === "" || destination === ""){

        return;

    }

    if(source === destination){

        distance.innerHTML = "Source and Destination cannot be the same.";

        time.innerHTML = "-";

        return;

    }

    if(routeData[source] && routeData[source][destination]){

        let route = routeData[source][destination];

        route.transport.forEach(function(mode){

            let option = document.createElement("option");

            option.value = mode;

            option.text = mode;

            transport.appendChild(option);

        });

        distance.innerHTML =
        "<strong>Distance :</strong> " + route.distance;

        transport.selectedIndex = 1;

        updateTime();

    }
    else{

        distance.innerHTML =
        "<span style='color:red'>Route information not available.</span>";

        time.innerHTML = "-";

    }

}
/* ===========================================
   LESSON 4 - PART 3
   Update Travel Time
=========================================== */

function updateTime(){

    let source = document.getElementById("source_location").value;

    let destination = document.getElementById("destination").value;

    let transport = document.getElementById("transport_mode").value;

    let travelTime = document.getElementById("travel_time");

    if(source === "" || destination === ""){

        travelTime.innerHTML = "Select Source & Destination";

        return;

    }

    if(routeData[source] && routeData[source][destination]){

        let route = routeData[source][destination];

        if(route.time[transport]){

            travelTime.innerHTML =
            "<strong>Estimated Time :</strong> " +
            route.time[transport];

        }
        else{

            travelTime.innerHTML =
            "Travel time not available.";

        }

    }

}


/* ===========================================
   Reset Form (Optional)
=========================================== */

function resetTravelInfo(){

    document.getElementById("transport_mode").innerHTML =
    "<option value=''>Select Transport</option>";

    document.getElementById("distance").innerHTML =
    "Select Source & Destination";

    document.getElementById("travel_time").innerHTML =
    "Select Source & Destination";

}


/* ===========================================
   Page Loaded
=========================================== */

window.onload = function(){

    resetTravelInfo();

};