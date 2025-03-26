function loadmodel(base_url, type, name) {
    method = ((type == 'official') ? 'loadofficialmodel' : 'loadusermodel');

    load_url = base_url + "/" + method + "/?filename=" + encodeURI(name);

    response = fetch(load_url, {
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