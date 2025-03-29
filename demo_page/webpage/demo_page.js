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
}

function loadmodel(type, name) {
    method = ((type == 'official') ? 'loadofficialmodel' : 'loadusermodel');

    session_id = document.getElementById("session_id").innerHTML;
    load_url = "/apicall/?session_id=" + session_id;
    load_url += "&endpoint=" + method + "&qstring=" + encodeURI("filename=" + encodeURI(name));

    do_web_request(load_url, "model_list");
    setTimeout(function(){window.location.reload();}, 500);
};

function deletemodel(filename) {
    if (confirm("Proceed with model deletion?") == true)
    {
        session_id = document.getElementById("session_id").innerHTML;
        load_url = "/apicall/?session_id=" + session_id;
        load_url += "&endpoint=deletemodel&qstring=" + encodeURI("filename=" + encodeURI(filename));

        do_web_request(load_url, "model_list");
        setTimeout(function(){window.location.reload();}, 500);
    }
}

function model_creator(form) {

    query = "name=" + encodeURI(form.name.value);
    query += "%26description=" + encodeURI(form.description.value);
    query += "%26n_estimators=" + encodeURI(form.n_estimators.value);
    query += "%26learning_rate=" + encodeURI(form.learning_rate.value);
    query += "%26max_depth=" + encodeURI(form.max_depth.value);
    query += "%26trainingdataurl=" + encodeURI(form.trainingdataurl.value);

    session_id = document.getElementById("session_id").innerHTML;
    load_url = "/apicall/?session_id=" + session_id;
    load_url += "&endpoint=createandtrainmodel&qstring=" + encodeURI(query);

    do_web_request(load_url, "model_creator");
    setTimeout(function(){window.location.reload();}, 500);
}

function predict_from_json(jsonform) {

    session_id = document.getElementById("session_id").innerHTML;
    load_url = "/apicall/?session_id=" + session_id;
    load_url += "&endpoint=predictfromjson&qstring=" +
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

    session_id = document.getElementById("session_id").innerHTML;
    load_url = "/apicall/?session_id=" + session_id;
    load_url += "&endpoint=predictfromfile&qstring=" +
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

    session_id = document.getElementById("session_id").innerHTML;
    load_url = "/apicall/?session_id=" + session_id;
    load_url += "&endpoint=predictfile2file&qstring=" +
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
