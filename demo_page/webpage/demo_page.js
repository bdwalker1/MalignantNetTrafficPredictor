function do_web_request(url, sectionId) {
    document.getElementById(sectionId).innerHTML = "Sending request, waiting for result and page reload.";
    response = fetch(url, {
        method: 'POST',
        headers: {
            'accept': 'application/json'
        },
        body: {}
    })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(responseData => {
            console.log('Success:', responseData);
        })
        .catch(error => {
            console.error('Error:', error);
        });
    window.location.reload();
}

function loadmodel(base_url, type, name) {
    method = ((type == 'official') ? 'loadofficialmodel' : 'loadusermodel');

    load_url = base_url + "/" + method + "/?filename=" + encodeURI(name);

    do_web_request(load_url, "model_list");
};

function deletemodel(base_url, filename) {
    if (confirm("Proceed with model deletion?") == true)
    {
        load_url = base_url + "/deletemodel/?filename=" + filename;

        do_web_request(load_url, "model_list");
    }
}

function model_creator(base_url, form) {

    load_url = base_url + "/createandtrainmodel/?name=" + encodeURI(form.name.value);
    load_url += "&description=" + encodeURI(form.description.value);
    load_url += "&n_estimators=" + encodeURI(form.n_estimators.value);
    load_url += "&learning_rate=" + encodeURI(form.learning_rate.value);
    load_url += "&max_depth=" + encodeURI(form.max_depth.value);
    load_url += "&trainingdataurl=" + encodeURI(form.trainingdataurl.value);

    do_web_request(load_url, "model_creator");
}

// function predict_from_json(base_url, form) {
//
//     load_url = base_url + "/predictfromjson/?json_str=" + encodeURI(form.json_string.value.replace(/\r?\n|\t/g, ""));
//     document.getElementById('json_predictions').innerHTML = load_url;
//
//     const response = fetch(load_url, {
//         method: 'POST',
//         headers: {
//             'accept': 'application/json'
//         },
//         body: JSON.stringify("")
//     })
//     .then(response => {
//         if (!response.ok) {
//             throw new Error('Network response was not ok');
//         }
//         return response.json();
//     })
//     .then(responseData => {
//         console.log('Success:', responseData);
//     })
//     .catch(error => {
//         document.getElementById("json_predictions").innerHTML = "Error: " + error + ;
//         console.error('Error:', error);
//     });
//
//     document.getElementById("json_predictions").innerHTML = response.json();
// }

function predict_from_json(jsonform) {

    load_url = "/apicall/?endpoint=predictfromjson&qstring=" +
        encodeURI("json_str=" + encodeURI(jsonform.json_string.value.replace(/\r?\n|\t/g, "")));
    const form = document.createElement("form");
    form.method = "POST";
    form.action = load_url;
    form.target = "json_predictions";
    form.style.display = "none";
    document.getElementById("json_predictions").onload = function () {json_loaded("json_predictions");}
    document.getElementById("json_predictions").contentDocument.body.innerHTML = "<pre>Working...</pre>";
    document.body.appendChild(form);
    form.submit();
    document.body.removeChild(form);
}

function predict_from_file(pffform) {

    load_url = "/apicall/?endpoint=predictfromfile&qstring=" +
        encodeURI("fileurl=" + encodeURI(pffform.inputdataurl.value));
    const form = document.createElement("form");
    form.method = "POST";
    form.action = load_url;
    form.target = "file_predictions";
    form.style.display = "none";
    document.getElementById("file_predictions").onload = function () {json_loaded("file_predictions");}
    document.getElementById("file_predictions").contentDocument.body.innerHTML = "<pre>Working... Results will open as download file when ready.</pre>";
    document.body.appendChild(form);
    form.submit();
    document.body.removeChild(form);
}

function predict_file2file(f2fform) {

    load_url = "/apicall/?endpoint=predictfile2file&qstring=" +
        encodeURI("inputurl=" + encodeURI(f2fform.inputdataurl.value) + "%26outputurl=" + encodeURI(f2fform.outputurl.value));
    const form = document.createElement("form");
    form.method = "POST";
    form.action = load_url;
    form.target = "file2file_results";
    form.style.display = "none";
    document.getElementById("file_predictions").onload = function () {json_loaded("file2file_results");}
    document.getElementById("file2file_results").contentDocument.body.innerHTML = "<pre>Working...</pre>";
    document.body.appendChild(form);
    form.submit();
    document.body.removeChild(form);
}

function json_loaded(frameid) {
    frame = document.getElementById(frameid);
    framedoc = "Fred";
    if (frame.contentDocument)
        framedoc = frame.contentDocument;
    frameText = framedoc.documentElement.textContent;
}

function openTab(tabId) {
    // Hide all tab content
    const tabContents = document.getElementsByClassName('tab-content');
    for (let i = 0; i < tabContents.length; i++) {
        tabContents[i].classList.remove('active');
    }

    // Remove active class from all tab buttons
    const tabButtons = document.getElementsByClassName('tab-button');
    for (let i = 0; i < tabButtons.length; i++) {
        tabButtons[i].classList.remove('active');
    }

    // Show the selected tab content
    document.getElementById(tabId).classList.add('active');

    // Add active class to the clicked button
    const activeButton = document.querySelector(`button[onclick="openTab('${tabId}')"]`);
    activeButton.classList.add('active');
}
