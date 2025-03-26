function do_web_request(url) {
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

    do_web_request(load_url);
};

function deletemodel(base_url, filename) {
    if (confirm("Proceed with model deletion?") == true)
    {
        load_url = base_url + "/deletemodel/?filename=" + filename;

        do_web_request(load_url);
    }
}

function model_creator(base_url, form) {

    load_url = base_url + "/createandtrainmodel/?name=" + encodeURI(form.name.value);
    load_url += "&description=" + encodeURI(form.description.value);
    load_url += "&n_estimators=" + encodeURI(form.n_estimators.value);
    load_url += "&learning_rate=" + encodeURI(form.learning_rate.value);
    load_url += "&max_depth=" + encodeURI(form.max_depth.value);
    load_url += "&trainingdataurl=" + encodeURI(form.trainingdataurl.value);

    do_web_request(load_url);
}
